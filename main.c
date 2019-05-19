#include <stdio.h>
#include "strings.h"

int main()
{
    gui_strings_t language_array[] = { gui_strings_En,
                                       gui_strings_Fr,
                                       gui_strings_Es,
                                       gui_strings_De};
    for (int i = 0; i < 4; ++i)
    {
        gui_strings_t* lang = &language_array[i];
        printf("%s %s!\t%s, %s!\r\n", lang->welcome, lang->user, lang->ok, lang->logout);
    }

    return 0;
}