#include <list>
#include <string>
#include "hk_string.h"

class hk_datasource
{
    public:
        virtual     ~hk_datasource();
        hk_datasource();
        void runtest( hk_string frompart);
        void parse_tablepart(void);

       typedef class fieldoriginclass
       {
         public:
	 hk_string fieldname;
	 hk_string alias;
	 fieldoriginclass()
	  {
	  }
	 bool operator=(const fieldoriginclass& o)
	   {
	     fieldname=o.fieldname;
	     alias=o.alias;
	     return true;
	   }
         };

/**
 *struct_parsed_sql is needed for parsing th SQL-statement in hk_datasource
 */
        typedef class
        {
            public:
                hk_string
                    select_part,
                    from_part,
                    where_part,
                    groupby_part,
                    having_part,
                    orderby_part ;
		    std::list <fieldoriginclass> fieldpart;
		    std::list <std::pair<hk_string,hk_string> > tablepart;
        } struct_parsed_sql;

        struct_parsed_sql* p_parsed_sql;
        hk_string p_identifierdelimiter;
};