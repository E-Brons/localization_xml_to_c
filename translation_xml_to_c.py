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

Copyright:
(c) Copyright 2018 Stanley Black & Decker
ALL RIGHTS RESERVED
This is a private source - distribution and/or use is forbidden without a written permission by owner
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
DEBUG_LOGGING = True
OUTPUT_LOGGING = True

COLOR_CODE = {"OUTPUT": 'magenta',
              "DEBUG": 'cyan',
              "ERROR": 'red'}


#
# Functions
#
def print_debug(message):
    if DEBUG_LOGGING:
        print(colored(message, COLOR_CODE["DEBUG"]))


def print_error(message):
    print(colored(message, COLOR_CODE["ERROR"]))


def create_output_header(language_names, members_name_and_count):
    output_file_name = CFG.OUTPUT_HEADER_FILE_NAME

    # write header file
    with open(output_file_name,'w') as output_header_file:
        # write prolog
        output_header_file.write(CFG.OUTPUT_HEADER_PROLOG)

        # write the translation structure definition
        output_header_file.write("// Definitions" + CFG.SOURCE_FILES_EOL)
        output_header_file.write("typedef struct {0}{1}".format(CFG.OUTPUT_STRUCT_TYPENAME, CFG.SOURCE_FILES_EOL))
        output_header_file.write("{"+ CFG.SOURCE_FILES_EOL)
        for member_name in members_name_and_count:
            member_count = members_name_and_count[member_name]
            if 0 == member_count:
                # write the non-array member values
                output_header_file.write("    const char* {0};{1}".format(member_name, CFG.SOURCE_FILES_EOL))
            else:
                # write the array member values
                output_header_file.write("    const char* {0}[{1}];{2}".format(member_name, member_count, CFG.SOURCE_FILES_EOL))
        output_header_file.write("} " + CFG.OUTPUT_STRUCT_TYPENAME + ";" + CFG.SOURCE_FILES_EOL)

        # write forward decleration for available languages
        output_header_file.write(CFG.SOURCE_FILES_EOL + "// Forward Declerations" + CFG.SOURCE_FILES_EOL)
        for language in language_names:
            lang_var = CFG.OUTPUT_LANGUAGES_VARNAME.format(language)
            output_header_file.write("extern const {0} {1};{2}".format(CFG.OUTPUT_STRUCT_TYPENAME, lang_var, CFG.SOURCE_FILES_EOL))

    # print the file to screen (for debug)
    if OUTPUT_LOGGING:
        print("Source File Created '{0}':\r\n".format(output_file_name))
        with open(output_file_name,'r') as output_source_file:
            print(colored(output_source_file.read(), COLOR_CODE["OUTPUT"]))


def create_output_source(language_name, members_dict, member_arrs_dict):
    output_file_name = CFG.OUTPUT_SOURCE_FILE_NAME.format(language_name)

    #write source file
    with open(output_file_name,'w') as output_source_file:
        # write prolog
        output_source_file.write(CFG.OUTPUT_SOURCE_PROLOG.format(language_name))
        output_source_file.write("{" + CFG.SOURCE_FILES_EOL)
        # write the non-array member values
        for member_name in members_dict:
            value = members_dict[member_name]
            output_source_file.write("    .{0} = {1},{2}".format(member_name, value, CFG.SOURCE_FILES_EOL))
        # write the array member values
        for member_name in member_arrs_dict:
            output_source_file.write("    .{0}[] = {1}".format(member_name, CFG.SOURCE_FILES_EOL))
            for value in member_arrs_dict[member_name]:
                output_source_file.write("        {0},{1}".format(value, CFG.SOURCE_FILES_EOL))
            output_source_file.write("             }" + CFG.SOURCE_FILES_EOL)
        output_source_file.write("};" + CFG.SOURCE_FILES_EOL)

    # print the file to screen (for debug)
    if OUTPUT_LOGGING:
        print("Source File Created '{0}':\r\n".format(output_file_name))
        with open(output_file_name,'r') as output_source_file:
            print(colored(output_source_file.read(), COLOR_CODE["OUTPUT"]))


def parse_input_xml(language_name, language_input_xml, member_name_dict):
    print_debug("parse_input_xml {0} {1} {2}".format(language_name, language_input_xml, member_name_dict))

    # parse the XML
    try:
        parsed_xml = minidom.parse(language_input_xml)
    except:
        print_error("Error parsing XML file: '{0}'".format(language_input_xml))
        raise  # abort further execution

    # parse all non-array strings into the dictionary 'members_dict;
    members_dict = dict()
    for element in parsed_xml.getElementsByTagName('string'):
        member_name = element.attributes['name'].value
        if None == element.firstChild:
            member_value = "0"
        else:
            member_value = '"' + element.firstChild.data +'"'

        # add to members dictionary for creating the output: language source file
        members_dict[member_name] = member_value
        # output 2: mark the member name as non-array for the output: all-languages header file
        member_name_dict[member_name] = 0
        print_debug(" .{0} = {1},".format(member_name, members_dict[member_name]))

    # parse all array strings into the dictionary 'member_arrs_dict;
    member_arrs_dict = dict()
    for element in parsed_xml.getElementsByTagName('string-array'):
        member_name = element.attributes['name'].value
        print_debug(".{0} [] = ...; // string arrays are currently not supported".format(member_name))
        # TODO - implement arrays

    # create the output source file
    create_output_source(language_name, members_dict, member_arrs_dict)


def main():
    # dict use for storing unique struct-member names and value which indicates the array size
    g_member_name_dict = dict()
    g_language_names = list()
    for language in CFG.INPUT_LANGUAGES_XML_FILES:
        parse_input_xml(language, CFG.INPUT_LANGUAGES_XML_FILES[language], g_member_name_dict)
        g_language_names += [language]

    create_output_header(g_language_names, g_member_name_dict)

#
# Run main
#
if __name__ == "__main__":
    init_colorama()
    main()