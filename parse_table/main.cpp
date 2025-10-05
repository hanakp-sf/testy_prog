#include <iostream>
#include "hk_datasource.h"

int main(void) {
  hk_datasource theobj;
  
  theobj.runtest("form");
  theobj.runtest("schm.tblname");
  theobj.runtest("\"form\"");
  theobj.runtest("\"schm.tblname\"");
  theobj.runtest("\"schm\".tblname");
  theobj.runtest("schm.\"tblname\"");
  theobj.runtest("\"schm\".\"tblname\"");
  std::cout << "Koniec" << std::endl;
  return 0;
}