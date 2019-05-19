#include <stdio.h>
#include "strings.h"

int main()
{
    struct
    {
        const char* name;
        gui_strings_t* strings;
    } languages[] = {
                           { "English" , &gui_strings_En},
                           { "French" , &gui_strings_Fr },
                           { "Spanish" , &gui_strings_Es },
                           { "German" , &gui_strings_De }
                         };

    for (int i = 0; i < 4; ++i)
    {
        gui_strings_t* lang = languages[i].strings;
        printf(" %s:\r\n", languages[i].name);
        printf(" %11s %-14s %8s, %s!\r\n", lang->welcome, lang->user, lang->ok, lang->logout);
    }

    return 0;
}