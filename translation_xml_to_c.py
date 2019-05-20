#!/usr/bin/python3
"""
Author: Elkana Bronstein
Date:   May 2019

Brief:
    A utility to transform string translations from XML to C

Details:
    The output C source and header files can be used for any C application (no dependencies)
    The input XML files shall follow Android Localization format. For example:
    <resources>
        <string name="localization_manager">Localization Manager</string>
        <string name="admin_users">Administrators are people that manage the organization.</string>
        <string-array name="account_details_array">
            <item>username</item>
            <item>Email address</item>
        </string-array>
    </resources>
    This script customization is through companion 'translation_xml_to_c_cfg.py' config file
"""

#
# Imports
#
from colorama import init as init_colorama
from termcolor import colored
from xml.dom import minidom
# Configuration file
import translation_xml_to_c_cfg as CFG

#
# Constants
#
COLOR_CODE = {"OUTPUT": 'magenta',
              "DEBUG": 'cyan',
              "ERROR": 'red'}


#
# Functions
#
def print_debug(message):
    """ print a message with debug formatting and filtering
    :param message: message to be printed
    :type message:  string
    :return: None
    """
    if CFG.DEBUG_LOGGING:
        print(colored(message, COLOR_CODE["DEBUG"]))


def print_error(message):
    """ print a message with error formatting
    :param message: message to be printed
    :type message:  string
    :return: None
    """
    print(colored(message, COLOR_CODE["ERROR"]))


def create_output_header(language_names, members_name_and_count):
    """ Create a C header file to describe the languages dictionaries and dictionary struct
    :param language_names: names of languages to support
    :type language_names:  list (string)
    :param members_name_and_count: dictionary of member names -> 0 for non-array, count number of values for array
    :type members_name_and_count:  dictionary {string : int}
    :return: None
    """
    output_file_name = CFG.OUTPUT_HEADER_FILE_NAME
    print_debug("create_output_header {0}".format(output_file_name))

    # write header file
    with open(output_file_name, 'w') as output_header_file:
        # write prolog
        output_header_file.write(CFG.OUTPUT_HEADER_PROLOG)

        # write the translation structure definition
        output_header_file.write("// Definitions" + CFG.SOURCE_FILES_EOL)
        output_header_file.write("typedef struct {0}{1}".format(CFG.OUTPUT_STRUCT_TYPENAME, CFG.SOURCE_FILES_EOL))
        output_header_file.write("{" + CFG.SOURCE_FILES_EOL)
        for member_name in members_name_and_count:
            member_count = members_name_and_count[member_name]
            if 0 == member_count:
                # write the non-array member values
                output_header_file.write("    const char* {0};{1}".format(member_name, CFG.SOURCE_FILES_EOL))
            else:
                # write the array member values
                output_header_file.write("    const char* {0}[{1}];{2}".format(member_name,
                                                                               member_count,
                                                                               CFG.SOURCE_FILES_EOL))
        output_header_file.write("} " + CFG.OUTPUT_STRUCT_TYPENAME + ";" + CFG.SOURCE_FILES_EOL)

        # write forward decleration for available languages
        output_header_file.write(CFG.SOURCE_FILES_EOL + "// Forward Declerations" + CFG.SOURCE_FILES_EOL)
        for language in language_names:
            output_header_file.write("extern const {0} {1};{2}".format(CFG.OUTPUT_STRUCT_TYPENAME,
                                                                       CFG.OUTPUT_LANGUAGES_VARNAME.format(language),
                                                                       CFG.SOURCE_FILES_EOL))

    # print the file to screen (for debug)
    if CFG.OUTPUT_LOGGING:
        print(colored("Source File Created '{0}':\r\n".format(output_file_name)))
        with open(output_file_name, 'r') as output_source_file:
            print(colored(output_source_file.read(), COLOR_CODE["OUTPUT"]))

    # add access MACROs
    # TODO support default language


def create_output_source(language_name, members_dict):
    """ Create a C source file to define the language's dictionary
    :param language_name: name of language to create
    :type language_name:  string
    :param members_dict: dictionary of member names -> translated string(s)
    :type members_dict:  dictionary {string : string/list of strings}
    :return: None
    """
    output_file_name = CFG.OUTPUT_SOURCE_FILE_NAME.format(language_name)
    print_debug("create_output_source {0}".format(output_file_name))

    # write source file
    with open(output_file_name, 'w') as output_source_file:
        # write prolog
        output_source_file.write(CFG.OUTPUT_SOURCE_PROLOG.format(language_name))
        # write the struct initialization list (by member assignment)
        output_source_file.write("{" + CFG.SOURCE_FILES_EOL)
        for member_name in members_dict:
            value = members_dict[member_name]
            if type(value) is str:
                # write the non-array member values
                output_source_file.write("    .{0} = {1},{2}".format(member_name, value, CFG.SOURCE_FILES_EOL))
            elif (type(value) is list) and (type(value[0]) is str):
                # write the array member values
                output_source_file.write("    .{0} = {1}".format(member_name, CFG.SOURCE_FILES_EOL))
                for string in value:
                    output_source_file.write("        {0},{1}".format(string, CFG.SOURCE_FILES_EOL))
                output_source_file.write("             }" + CFG.SOURCE_FILES_EOL)
            else:
                print_error("unexpected type of member value {0}:{1}".format(member_name, type(value)))
        output_source_file.write("};" + CFG.SOURCE_FILES_EOL)

    # print the file to screen (for debug)
    if CFG.OUTPUT_LOGGING:
        print("Source File Created '{0}':\r\n".format(output_file_name))
        with open(output_file_name, 'r') as output_source_file:
            print(colored(output_source_file.read(), COLOR_CODE["OUTPUT"]))


def parse_input_xml(language_input_xml, members_name_and_count):
    """ Parse an XML containing language's dictionary,
         Update number of stings for each struct member,
         return a dictionary with the language translation(s) for each member
    :param language_input_xml: name of language xml file
    :type language_input_xml:  string
    :param members_name_and_count: dictionary of member names -> 0 for non-array, count number of values for array
    :type members_name_and_count:  dictionary {string : int}
    :return: None
    """
    print_debug("parse_input_xml {0}".format(language_input_xml))
    members_dict = dict()

    # parse the XML
    try:
        parsed_xml = minidom.parse(language_input_xml)
    except:
        print_error("Error parsing XML file: '{0}'".format(language_input_xml))
        raise  # abort further execution

    # parse all non-array strings into the dictionary 'members_dict;
    for non_array_element in parsed_xml.getElementsByTagName('string'):
        member_name = non_array_element.attributes['name'].value
        if non_array_element.firstChild is None:
            member_value = "0"
        else:
            member_value = '"' + non_array_element.firstChild.data + '"'

        # add to members dictionary for creating the output: language source file
        members_dict[member_name] = member_value
        # output 2: mark the member name as non-array for the output: all-languages header file
        members_name_and_count[member_name] = 0

    # parse all array strings into the dictionary 'member_arrs_dict;
    for array_element in parsed_xml.getElementsByTagName('string-array'):
        member_name = array_element.attributes['name'].value
        member_count = 0
        member_value = "{"
        for item in array_element.getElementsByTagName('item'):
            member_value += '"' + item.firstChild.data + '", '
            member_count += 1
        member_value += "}"

        # add to members dictionary for creating the output
        members_dict[member_name] = member_value
        # output 2: set the number of strings values for member name
        members_name_and_count[member_name] = member_count

    return members_dict


def main():
    """ Generate C header and sources that define dictionaries for the languages
    :return: None
    """

    # dict use for storing unique member names and value which indicates the array size
    member_number_of_strings = dict()
    # list of languages names (directly derived from CFG.INPUT_LANGUAGES_XML_FILES)
    language_names = list()
    # find languages and members properties (from any XML)
    for language in CFG.INPUT_LANGUAGES_XML_FILES:
        language_names += [language]
        # Parse an input XML and:
        # a. Update number of strings for each member name
        # b. Get dictionary for the current language
        members_dict_lang = parse_input_xml(CFG.INPUT_LANGUAGES_XML_FILES[language],
                                            member_number_of_strings)
        # create the output source file, using the language dictionary
        create_output_source(language, members_dict_lang)

    create_output_header(language_names, member_number_of_strings)
    print_debug("Done!")


#
# Run main
#
if __name__ == "__main__":
    init_colorama()
    main()
