// ****************************************************************************
// copyright (c) 2000-2005 Horst Knorr <hk_classes@knoda.org>
// This file is part of the hk_classes library.
// This file may be distributed and/or modified under the terms of the
// GNU Library Public License version 2 as published by the Free Software
// Foundation and appearing in the file COPYING included in the
// packaging of this file.
// This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
// WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
// ****************************************************************************
#ifndef HK_STRING
#define HK_STRING
#include <string>
using namespace std;
/**
 *
 *@short base class for strings in hk_classes
 *@version $Revision: 1.20 $
 *@author Horst Knorr (hk_classes@knoda.org)
 *should one day work with unicode. In the moment it is just the standard string class
 *of your stl-library
 */

    typedef std::basic_string <char> hk_string;
// typedef basic_string <wchar_t> wstring;


extern "C"
{
    hk_string smallstringconversion(const hk_string & what, const hk_string& from, const hk_string& to);
    hk_string l2u(const hk_string& what,const hk_string& locale="");
    hk_string u2l(const hk_string& what,const hk_string& locale="");
    hk_string string2upper(const hk_string& what);
    hk_string string2lower(const hk_string& what);

}


/**
 *formats a double value into a string. It uses your set locale.
 *@param separator if true your local thousands separator is used i.e the number 12345.6789
 * will be displayed in Germany as 12.345,6789 and in USA as 12,345.6789
 *@param digits the amount of digits of the number part <0. E.g. if digits is 2 the above number
would be 12345.68
*/
hk_string format_number(double value,bool separator=true,int digits=2,const hk_string& locale="");
hk_string format_number(const hk_string& value,bool is_locale, bool separator,int digits,const hk_string& locale);

/**
 *formats a double value into a string ignoring your locale.
 *@param separator if true your local thousands separator is used i.e the number 12345.6789
 12,345.6789
*@param digits the amount of digits of the number part <0. E.g. if digits is 2 the above number
would be 12345.68
*/
hk_string format_standard_number(double value,bool separator=false,int digits=8,const hk_string& standardlocale="C");
hk_string format_standard_number(const hk_string& value,bool separator=false,int digits=8,const hk_string& standardlocale="C");

/**
 *converts a number in a string (which uses your locale) in a double value
 */
double localestring2double(const hk_string& localenumberstring);

long int localestring2int(const hk_string& localenumberstring);
long unsigned int localestring2uint(const hk_string& localenumberstring);

/**
 *converts a number in a string (which ignores your locale) in a double value
 */
double standardstring2double(const hk_string& standardnumberstring,const hk_string& standardlocale="C");
/**
 *converts a number in a string (which ignores your locale) in a long int value
 */
long int standardstring2int(const hk_string& standardnumberstring,const hk_string& standardlocale="C");
/**
 * converts a long int number to a non localized string
 */
hk_string longint2string(long int value);
/**
 * converts a unsigned long int number to a non localized string
 */
hk_string ulongint2string(unsigned long int value);
/**
 *replaces all characters 'what' in 'where' with 'with'.
 *@param what the search string to be replaced
 *@param where the string which should be altered
 *@param with the string replacement string
 *@return the new string
 */
hk_string replace_all(const hk_string& what,const hk_string& where,const hk_string& with);


hk_string trimleft(const hk_string&);
hk_string trimright(const hk_string&);
hk_string trim(const hk_string&);
hk_string bin2hex(char n);
char       hex2bin(const hk_string&);

#endif
