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
//$Revision: 1.38 $
using namespace std;
#include "hk_string.h"
//#include "hk_class.h"
#include <stdlib.h>
#include <stdio.h>
#include <iostream>

#include <iconv.h>
#include <errno.h>
#include <locale.h>
#include <nl_types.h>
#include <langinfo.h>
#include <cmath>
#ifdef HAVE_CONFIG_H
#include <config.h>
#endif



hk_string smallstringconversion(const hk_string & what, const hk_string& from, const hk_string& to)
{
    if (from==to) return what;
    hk_string result;
  /*  iconv_t handle=iconv_open(to.c_str(),from.c_str());
    if (handle==(iconv_t)-1)
    {
        cerr <<"conversion from: "<<from<<" to: "<<to<<endl;
        cerr <<"hk_string smallstringconversion: Conversion not possible"<<endl;
        return result;
    }

    size_t buffersize=100;
    char* outbuffer= new char[buffersize+sizeof(wchar_t)];
    char* outbufferpointer=outbuffer;
    const char* inbufferpointer=what.c_str();
    size_t availableinbuffersize=what.size();
    size_t availableoutputbuffersize=buffersize;

    bool process_convert=true;
    size_t convertresult;
    while (process_convert)
    {
        convertresult=iconv(handle,(ICONV_CONST char**)&inbufferpointer,&availableinbuffersize,&outbufferpointer,&availableoutputbuffersize);
        if (convertresult==(size_t)-1)
        {
            if (errno==E2BIG)
            {                                     //buffer full
                result.append(outbuffer,buffersize-availableoutputbuffersize);
                outbufferpointer=outbuffer;
                availableoutputbuffersize=buffersize;
            }
            else
            if (errno==EILSEQ)
            {
//undefined character => ignore it
//                   cerr <<"hk_string smallstringconversion: undefined character !!!"<<endl;
                inbufferpointer +=sizeof(char);
                if (availableinbuffersize>sizeof(char))availableinbuffersize -=sizeof(char);

            }
            else
            {                                     //a real error occured
//                 cerr<<"hk_string:: Error while converting  errno:"<<errno<<" convertresult: '"<<convertresult<<"'"<<endl;
// 		cerr <<"conversion from: '"<<from<< "' to: '"<<to<<"'"<<endl;
                iconv_close(handle); 
                delete[] outbuffer;
                return what; //nevertheless return the string unchanged
            }
        }
        else
        {
            process_convert=false;
            *outbufferpointer=L'\0';
            result.append(outbuffer,outbufferpointer-outbuffer);
        }

    }
    iconv_close(handle);
    delete[] outbuffer; */
    return result;
}


hk_string l2u(const hk_string& what,const hk_string& localcharset)
{
    hk_string use_locale=(localcharset.size()==0?nl_langinfo(CODESET):localcharset);
//    cout <<"aktueller Zeichensatz: "<<use_locale<<endl;
    return smallstringconversion(what,use_locale,"UTF-8");
}


hk_string u2l(const hk_string& what,const hk_string& localcharset)
{
    hk_string use_locale=(localcharset.size()==0?nl_langinfo(CODESET):localcharset);
//    cout <<"aktueller Zeichensatz: "<<use_locale<<endl;
    return smallstringconversion(what,"UTF-8",use_locale);
}


hk_string string2upper(const hk_string& what)
{
    string w=what;
    for (hk_string::size_type tt=0;tt<w.size();tt++)
    {
        w[tt]=toupper(w[tt]);
    }
    return w;
}


hk_string string2lower(const hk_string& what)
{
    string w=what;
    for ( hk_string::size_type tt=0;tt<w.size();tt++)
    {
        w[tt]=tolower(w[tt]);
    }
    return w;
}


hk_string format_number(double value,bool separator,int digits,const hk_string& locale)
{
    hk_string origlocale=setlocale(LC_NUMERIC,NULL);
    hk_string origmonetarylocale=setlocale(LC_MONETARY,NULL);
   // setlocale(LC_NUMERIC,(locale!=""?locale.c_str():hk_class::locale().c_str()));
   // setlocale(LC_MONETARY,(locale!=""?locale.c_str():hk_class::locale().c_str()));

    /*if (digits>10)
    {
        cerr<< "digits>10=>gekürzt"<<endl;
        digits=10;
    }*/
    int size= 500 +(digits>0?digits:0);
    char* buffer=new char[size];
    if (digits>-1)
    {
        snprintf(buffer,size,"%d",digits);
    }
    hk_string format="%0";
    if (separator)format="%'0";
    if (digits>-1)
    {
        format+=".";
        format+=buffer;
    } ;
    format+="f";
    hk_string result;
    snprintf(buffer,size,format.c_str(),value);
    result=buffer;
//    cout <<"formatstr: "<<format<<" digits: "<<digits<<" wert: "<<value<< " result: "<<result<<endl;
    delete[] buffer;
    setlocale(LC_NUMERIC,origlocale.c_str());
    setlocale(LC_MONETARY,origmonetarylocale.c_str());
    return result;
}


hk_string format_number(const hk_string& value,bool is_locale, bool separator,int digits,const hk_string& locale)
{
    double d=(is_locale?localestring2double(value):standardstring2double(value));
    return format_number(d,separator,digits,locale);
}


hk_string remove_separators(const hk_string& value)
{
    hk_string result=value;

    lconv* c=localeconv();
    if (c)
    {
        hk_string sep=c->thousands_sep;
//      cout <<"thsd_sep "<<sep<<" comma "<<c->decimal_point <<endl;
        if (sep.size()>0) result=replace_all(sep,value,"");
        sep=c->mon_thousands_sep;
        if (sep.size()>0) result=replace_all(sep,value,"");
    }
//  cout<<"remove separators orig: "<<value<<" neu: "<<result<<endl;
    return result;

}


double localestring2double(const hk_string& localenumberstring)
{

    hk_string origlocale=setlocale(LC_NUMERIC,NULL);
    hk_string origmonetarylocale=setlocale(LC_MONETARY,NULL);
  //  setlocale(LC_NUMERIC,hk_class::locale().c_str());
  //  setlocale(LC_MONETARY,hk_class::locale().c_str());
    double v=0;
    sscanf(remove_separators(localenumberstring).c_str(),"%lf",&v);
    setlocale(LC_NUMERIC,origlocale.c_str());
    setlocale(LC_MONETARY,origmonetarylocale.c_str());
    return v;
}


long int localestring2int(const hk_string& localenumberstring)
{
    hk_string origlocale=setlocale(LC_NUMERIC,NULL);
    hk_string origmonetarylocale=setlocale(LC_MONETARY,NULL);
    //setlocale(LC_NUMERIC,hk_class::locale().c_str());
    //setlocale(LC_MONETARY,hk_class::locale().c_str());
    long int v;
    sscanf(remove_separators(localenumberstring).c_str(),"%ld",&v);
    setlocale(LC_NUMERIC,origlocale.c_str());
    setlocale(LC_MONETARY,origmonetarylocale.c_str());
    return v;

}


long unsigned int localestring2uint(const hk_string& localenumberstring)
{
    hk_string origlocale=setlocale(LC_NUMERIC,NULL);
    hk_string origmonetarylocale=setlocale(LC_MONETARY,NULL);
    //setlocale(LC_NUMERIC,hk_class::locale().c_str());
    //setlocale(LC_MONETARY,hk_class::locale().c_str());
    long unsigned int v;
    sscanf(remove_separators(localenumberstring).c_str(),"%lu",&v);
    setlocale(LC_NUMERIC,origlocale.c_str());
    setlocale(LC_MONETARY,origmonetarylocale.c_str());
    return v;

}


double standardstring2double(const hk_string& standardnumberstring,const hk_string& standardlocale)
{

    hk_string origlocale=setlocale(LC_NUMERIC,NULL);
    hk_string origmonetarylocale=setlocale(LC_MONETARY,NULL);
    setlocale(LC_NUMERIC,standardlocale.c_str());
    setlocale(LC_MONETARY,standardlocale.c_str());
    double v=0;
    sscanf(remove_separators(standardnumberstring).c_str(),"%lf",&v);
    setlocale(LC_NUMERIC,origlocale.c_str());
    setlocale(LC_MONETARY,origmonetarylocale.c_str());
    return v;
}


long int standardstring2int(const hk_string& standardnumberstring,const hk_string& standardlocale)
{

    hk_string origlocale=setlocale(LC_NUMERIC,NULL);
    hk_string origmonetarylocale=setlocale(LC_MONETARY,NULL);
    setlocale(LC_NUMERIC,standardlocale.c_str());
    setlocale(LC_MONETARY,standardlocale.c_str());
    long int v=0;
    sscanf(remove_separators(standardnumberstring).c_str(),"%ld",&v);
    setlocale(LC_NUMERIC,origlocale.c_str());
    setlocale(LC_MONETARY,origmonetarylocale.c_str());
    return v;
}


hk_string format_standard_number(double value,bool separator,int digits,const hk_string& standardlocale)
{
    hk_string result=format_number(value,separator,digits,standardlocale);
    return result;
}


hk_string longint2string(long int value)
{
    const int bsize=50;
    char* m= new char[bsize];
    snprintf(m,bsize,"%ld",value);
    hk_string result=m;
    delete[] m;
    return result;

}


hk_string ulongint2string(unsigned long int value)
{
    const int bsize=50;
    char* m= new char[bsize];
    snprintf(m,bsize,"%lu",value);
    hk_string result=m;
    delete[] m;
    return result;

}


hk_string format_standard_number(const hk_string& value,bool separator,int digits,const hk_string& standardlocale)
{
    double d=localestring2double(value);
    return format_standard_number(d,separator,digits,standardlocale);

}


hk_string replace_all(const hk_string& what,const hk_string& where,const hk_string& with)
{
  if (what.size()==0||where.size()==0) return where;
    hk_string p_result=where;
    hk_string::size_type pos=-with.size();
    while ((pos=p_result.find(what,pos+with.size()))<p_result.size())
    {
        p_result.replace(pos,what.size(),with);
    }
    return p_result;
}


const hk_string whitespace=" \t\n";

hk_string trimleft(const hk_string& t)
{
 hk_string::size_type p=0;
 hk_string result=t;
 while(p<=t.size())
 {
  if (!isspace(result[p]))
   {
    if ( p>0) result.erase(0,p);
    return result;
   }
  ++p;
 }
return result;
}

hk_string trimright(const hk_string& t)
{
 if (t.size()==0) return t;
 hk_string result=t;
 long p=result.size()-1;
 while(p>=0)
 {
  if (!isspace(result[p]))
   {
     result.erase(p+1);
     return result;
   }
  --p;
 }
return result;
}

hk_string trim(const hk_string& t)
{
  return trimleft(trimright(t));
}

 const char hexa[] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};

hk_string bin2hex(char n)
{
  hk_string result;
  unsigned char c=n;
  c=c>>4;
  result=hexa[c];
  c=n&0x0f;
  result+=hexa[c];
  return result;


}


char       hex2bin(const hk_string& h)
{
  unsigned char result=strtol(h.c_str(),NULL,16);
  return result;
}

