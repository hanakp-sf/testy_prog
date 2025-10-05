#include "hk_datasource.h"
#include <iostream>

hk_datasource::hk_datasource():p_parsed_sql(new struct_parsed_sql),p_identifierdelimiter("\"")
{
}

hk_datasource::~hk_datasource()
{
  if (p_parsed_sql != NULL)
    delete p_parsed_sql;
}

void hk_datasource::runtest( hk_string frompart)
{
  if (p_parsed_sql != NULL) {
    delete p_parsed_sql;
    p_parsed_sql = new struct_parsed_sql;
  }
  p_parsed_sql->from_part = frompart;
  parse_tablepart();
  std::list<std::pair<hk_string,hk_string> >::iterator it=p_parsed_sql->tablepart.begin();

std::cout << "frompart: #" <<p_parsed_sql->from_part << "#" << std::endl;

  while (it!=p_parsed_sql->tablepart.end())
  {
    std::cerr <<"=========="<< std::endl;
    std::cerr <<"  tablename : #"<<(*it).first<<"#"<< std::endl;
    std::cerr <<"  tablealias: #"<<(*it).second<<"#"<< std::endl;
    std::cerr <<"=========="<< std::endl << std::endl;

   ++it;
  }
  
}

void hk_datasource::parse_tablepart(void)
{
    //return;
    /*
    The following code does not work correctly yet
    */
    if (!p_parsed_sql) return;
    hk_string::size_type offset=0;
    hk_string quotedtype;
    hk_string nexttag;
    hk_string tststring=p_parsed_sql->from_part;
    enum
    {
	S_START,S_IN_DEFINITION,S_IN_IDENTIFIERQUOTED,S_IN_ALIAS,S_IN_ALIASQUOTED
    } state=S_START;



//parser begin
hk_string tag;
int row=1;
int col=1;
hk_string errormessages;
hk_string error="row %ROW% column %COL% :";
hk_string errorclose=error+"Too many closing brackets\n";
hk_string erroropen=error+"Too many open brackets\n";
std::pair<hk_string,hk_string> table;
while (offset<=tststring.size())
{
	hk_string xs(1,tststring[offset]);
	switch (state)
	{



	case S_START:
			nexttag="";
			tag="";
			if (isspace(xs[0]))
				{
					if (xs=="\n")
					{
						++row;col=0;
					}
				  break;
				}
			if (xs==p_identifierdelimiter)
			 {
			   state=S_IN_IDENTIFIERQUOTED;
			   break;

			 }
			else
			{
			 state=S_IN_DEFINITION;
			}
 			 tag=xs;
			break;




	case S_IN_DEFINITION:
	           {
			if (isspace(xs[0]))
			{
			 if (xs=="\n")
				{
				 ++row;col=0;
				}
        		if (string2upper(nexttag)=="AS")
        		{
				state=S_IN_ALIAS;
				table.first=trim(tag.substr(0,tag.size()-2));
				tag="";
				break;
        		}
        		else
        		{
				state=S_IN_ALIAS;
				table.first=trim(tag);
				tag="";
				break;
        		}

        		nexttag="";
				//ignore white spaces
			}
			else
			if (xs==p_identifierdelimiter)
			{
			  state=S_IN_IDENTIFIERQUOTED;
			}
			else

			if (xs==",")
			{
			table.first=trim(tag);
			p_parsed_sql->tablepart.insert(p_parsed_sql->tablepart.end(),table);
			table.first="";
			table.second="";
			tag="";
			state=S_START;

			}
    		        if (isspace(xs[0]))
			  {
			 nexttag="";
			}
			else nexttag+=xs;
    		        tag+=xs;

			break;
			}





	case S_IN_IDENTIFIERQUOTED:
					nexttag="";
					if (xs==p_identifierdelimiter)
					{
					   state=S_IN_DEFINITION;
					 }
					else
					{
					tag=tag+xs;
					}
					break;
	case S_IN_ALIASQUOTED:
	{
					if (xs!=p_identifierdelimiter)
					{
					  tag=tag+xs;

					}
					else
					{
					hk_string comma=",";
					while(offset<=tststring.size()&&','!=tststring[offset])
					   ++offset;
					state=S_START;
					{

					table.second=tag;
					p_parsed_sql->tablepart.insert(p_parsed_sql->tablepart.end(),table);
					table.first="";
					table.second="";
					tag="";
					state=S_START;

					}
					}
					break;
					};

	case S_IN_ALIAS:
					if (tag.size()==0&& xs==p_identifierdelimiter)
					{
					   state=S_IN_ALIASQUOTED;
					   break;


					}
					if (xs=="(")
					{
					   std::cerr <<"Error! '(' in alias definition!"<<std::endl;
					   return;
					}
					if (xs==",")
					{

					table.second=tag;
					p_parsed_sql->tablepart.insert(p_parsed_sql->tablepart.end(),table);
					table.first="";
					table.second="";
					tag="";
					state=S_START;

					}
				else
					{
					if (isspace(xs[0])&& tag.size()==0)
					{
					  ;
					}
					else
					tag+=xs;
					}
					break;


	}
	++offset;++col;



}

      switch (state)
  {
    case S_IN_ALIAS:			table.second=trim(tag);break;
    default:				table.first=trim(tag);
					break;
  }
  if (table.first.size()>0)
           p_parsed_sql->tablepart.insert(p_parsed_sql->tablepart.end(),table);




  return;
  std::list<std::pair<hk_string,hk_string> >::iterator it=p_parsed_sql->tablepart.begin();

  while (it!=p_parsed_sql->tablepart.end())
  {
    std::cerr <<"selectdef:"<< std::endl;
    std::cerr <<"=========="<< std::endl;
    std::cerr <<"  tablename : #"<<(*it).first<<"#"<< std::endl;
    std::cerr <<"  tablealias: #"<<(*it).second<<"#"<< std::endl;
    std::cerr <<"=========="<< std::endl << std::endl;

   ++it;
  }

  std::cerr <<tststring<< std::endl;
}