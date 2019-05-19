# localization_xml_to_c

A utility to transform string translations from XML to C

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
