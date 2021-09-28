#include <iostream>
#include <vector>
#include <map>

#define PRAZDNY '\0'

typedef char CHAR;

CHAR sym2(const std::basic_string<CHAR>* pveta, int pos)
{
    return pos < pveta->length() ? (*pveta)[pos] : PRAZDNY;
}

int nextsym2(const std::basic_string<CHAR>* pveta, int pos)
{
    return pos < pveta->length() ? ++pos : pos;
}

bool eof2(const std::basic_string<CHAR>* pveta, int pos)
{
	return pos >= pveta->length();
}

class datasource {
	
	public:
	    datasource(void):p_identdelim('"'),p_schemadelim('.')
	    {
		}
	    const char p_identdelim;
	    const char p_schemadelim;
};

class symbol;

class parsestatus 
{
public:
    bool zhoda;
    const std::basic_string<CHAR>* pveta;
    int currpos;
    const symbol* pprev;
    const symbol* pnext;
    const datasource * pdata;
    std::map<const char, std::basic_string<CHAR> > identifiers;
    std::basic_string<CHAR>* currident;
};

class symbol 
{
public:
    symbol ( const symbol * next,const symbol * alt ):pnext(next),palt(alt)
    {
    }
    const symbol * pnext;
    const symbol * palt;
    virtual void process(parsestatus * pstatus) const;
    virtual bool matches(const CHAR currchar, const datasource * pdata) const;
    virtual void onZhoda(const CHAR currchar, parsestatus * pstatus) const
    {
    }
};

bool symbol::matches(const CHAR currchar, const datasource * pdata) const
{
    return false;
}

void symbol::process(parsestatus * pstatus) const
{
    pstatus->zhoda = matches(sym2(pstatus->pveta,pstatus->currpos), pstatus->pdata);
   // std::cerr << "'" << sym2(pstatus->pveta,pstatus->currpos) << "' -> " << (pstatus->zhoda ? "OK":"NOK" )<< std::endl;
    if (pstatus->zhoda) {
        onZhoda(sym2(pstatus->pveta,pstatus->currpos), pstatus);
        pstatus->currpos = nextsym2(pstatus->pveta,pstatus->currpos);
        pstatus->pnext = pnext;
    }else
        pstatus->pnext = palt;
    pstatus->pprev = this;
}

// terminal symbol
class tsymbol: public symbol 
{
public:
    tsymbol(CHAR termsym, const symbol * next, const symbol * alt):symbol(next,alt),tsym(termsym)
    {
    }
    CHAR tsym;
    virtual bool matches(const CHAR currchar, const datasource * pdata) const;
    virtual void onZhoda(const CHAR currchar, parsestatus * pstatus) const;
};

bool tsymbol::matches(const CHAR currchar,const datasource * pdata) const
{
    return currchar == tsym;
}

void tsymbol::onZhoda(const CHAR currchar, parsestatus * pstatus) const
{
    // update identificator
    if (pstatus->currident != NULL)
        pstatus->currident->push_back(currchar);
}

// non-terminal symbol
class nsymbol: public symbol 
{
public:
    nsymbol(char pid, const symbol* def, const symbol* next, const symbol* alt):symbol(next, alt),pdef(def),id(pid)
    {
    }
    const symbol* pdef;
    const char id;
    virtual void process(parsestatus * pstatus) const;
};

void nsymbol::process(parsestatus * pstatus) const
{
    const symbol * pcur = pdef;
    
    pstatus->pprev = this;
    pstatus->currident = (id == PRAZDNY ? NULL: &(pstatus->identifiers[id]));
    while ( pcur != NULL) {
        pcur->process(pstatus);
        pcur = pstatus->pnext;
    }
    // return from recurse
    pstatus->pprev = this;
    pstatus->pnext = pnext;
}

// empty symbol
class esymbol: public symbol 
{
public:
    esymbol(const symbol * next, const symbol * alt):symbol(next,alt)
    {
    }

    virtual void process(parsestatus * pstatus) const;
};

void esymbol::process(parsestatus * pstatus) const
{
    pstatus->zhoda = true;
   // std::cerr << "'" << sym2(pstatus->pveta,pstatus->currpos) << "' -> " << (pstatus->zhoda ? "OK":"NOK" )<< std::endl;
    pstatus->pprev = this;        
    pstatus->pnext = pnext;
}

// whitespace char symbol
class wsymbol: public symbol 
{
public:
    wsymbol(const symbol * next, const symbol * alt):symbol(next,alt)
    {
    }

    virtual bool matches(const CHAR currchar, const datasource * pdata) const;
};

bool wsymbol::matches(const CHAR currchar,const datasource * pdata) const
{
    return isspace(currchar);
}

//  allowed char symbol
class asymbol: public tsymbol 
{
public:
    asymbol(const symbol * next, const symbol * alt):tsymbol(PRAZDNY,next,alt)
    {
    }

    virtual bool matches(const CHAR currchar, const datasource * pdata) const;
};

bool asymbol::matches(const CHAR currchar,const datasource * pdata) const
{
    return (currchar != pdata->p_identdelim) && (currchar != pdata->p_schemadelim) 
        && !isspace(currchar) && (currchar != PRAZDNY);
}

//  identifier delimiter symbol
class isymbol: public symbol 
{
public:
    isymbol(const symbol * next, const symbol * alt):symbol(next,alt)
    {
    }

    virtual bool matches(const CHAR currchar, const datasource * pdata) const;
};

bool isymbol::matches(const CHAR currchar,const datasource * pdata) const
{
    return (currchar == pdata->p_identdelim);
}

//  schema delimiter symbol
class ssymbol: public symbol 
{
public:
    ssymbol(const symbol * next, const symbol * alt):symbol(next,alt)
    {
    }

    virtual bool matches(const CHAR currchar, const datasource * pdata) const;
};

bool ssymbol::matches(const CHAR currchar,const datasource * pdata) const
{
    return (currchar == pdata->p_schemadelim);
}

class vrchol;

class celo
{
	public:
	celo(char psym, const vrchol* pvstup):sym(psym), vstup(pvstup), pvtoken(NULL)
	{
	}
	char sym;
	const vrchol* vstup;
	std::basic_string<CHAR>* pvtoken;
};

class vrchol 
{
    public:
	vrchol(const char* ppid, char ptsym, bool pusesym, const vrchol* psuc, const vrchol* palt): pid(ppid),tsym(ptsym), 
	suc(psuc), alt(palt), usesym(pusesym), term(true)
	{
	}
	vrchol(const char* ppid, const celo* pnsym, bool pusesym, const vrchol* psuc, const vrchol* palt): pid(ppid),
	nsym(pnsym), suc(psuc), alt(palt), usesym(pusesym), term(false)
	{
	}
	const vrchol* alt;
	const vrchol* suc;
	bool usesym;
	const char* pid;
	bool term;
	union {
	    char tsym;
	    const celo* nsym;
	};
	bool virtual isEqual(CHAR c, const datasource& inst) const
	{
		return tsym == c;
	}
};

class vrcholidendelim: public vrchol
{
	public:
	vrcholidendelim(const char* ppid, char ptsym, bool pusesym, const vrchol* psuc, const vrchol* palt):
	vrchol(ppid,ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c, const datasource& inst) const {
		return c == inst.p_identdelim;
	}		
};

class vrcholschemadelim: public vrchol
{
	public:
	vrcholschemadelim(const char* ppid, char ptsym, bool pusesym, const vrchol* psuc, const vrchol* palt):
	vrchol(ppid,ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c, const datasource& inst) const {
		return c == inst.p_schemadelim;
	}		
};

class vrcholoddelovace: public vrchol
{
	public:
	vrcholoddelovace(const char* ppid, char ptsym, bool pusesym, const vrchol* psuc, const vrchol* palt):
	vrchol(ppid,ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c, const datasource& inst) const {
		return isspace(c);
	}		
};


class vrcholvzatvorkach: public vrchol
{
	public:
	vrcholvzatvorkach(const char* ppid,char ptsym, bool pusesym, const vrchol* psuc, const vrchol* palt):
	vrchol(ppid,ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c,const datasource& inst) const
	{
		return (c != inst.p_identdelim) && (c != PRAZDNY);
	}		
};

class vrcholvolny: public vrchol
{
	public:
	vrcholvolny(const char* ppid, char ptsym, bool pusesym, const vrchol* psuc, const vrchol* palt):
	vrchol(ppid, ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c,const datasource& inst) const
	{
		return (c != inst.p_identdelim) && (c != inst.p_schemadelim) && !isspace(c) && (c != PRAZDNY);
	}		
};

std::vector<std::string> vety; 

int pos = 0;
int idVeta = 0;
bool bezchyba = true;

void priprav_vety()
{
	vety.push_back("cb");
/*	vety.push_back(" BATGYTU  ");
	vety.push_back("  cATG.YTU  ");
	vety.push_back("BA.   ");
	vety.push_back("b\"A");
	vety.push_back( "B.n" );
	vety.push_back("S k");
	vety.push_back("\"sch\".tbl"); 
	vety.push_back("\"S.k\""); 
	vety.push_back("\"sch\".\"tbl.s\""); */
    vety.push_back("  ca");
    vety.push_back("1b  ");
    vety.push_back("  1kl.jk");
    vety.push_back("  1v ");
}

char sym()
{
	return (pos < vety[idVeta].length()) ? vety[idVeta][pos]: '\0';
}

void nextsym()
{
	if (pos < vety[idVeta].length())
	    pos++;
}

bool eof()
{
	return pos >= vety[idVeta].length();
}

/*
class analyzer 
{
	public:
	analyzer(datasource* pdat):p_data(pdat)
	{
	}
	
	datasource* p_data;
	std::map<const celo*, std::string*> identif;
	
// NAM2
    static const vrchol nPraz;
    static const vrcholvolny nDal;	
    static const vrcholvolny nprve;
    static const celo nam2;
    static const celo nam1;
// NAMEX
    static const vrchol nPrazEx;
    static const vrcholvzatvorkach nDalEx;	
    static const vrcholvzatvorkach nprveex;
    static const celo namex2;
    static const celo namex1;	
	
    static const vrchol konPraz;
    static const vrcholoddelovace konSpace;

    static const vrcholidendelim dq22;
    
    static const vrchol namex2nterm;
    static const vrchol nam2nterm;
    static const vrcholidendelim dq21;
      
    static const vrcholschemadelim charDot;
    
    static const vrcholidendelim dq12;
    static const vrchol namex1nterm;
    static const vrchol nam1nterm;
    static const vrcholidendelim dq11;     
    
	static const vrchol zacPraz;
	static const vrcholoddelovace zacSpace;
	
	static const celo star;
	void analyzator( const celo* pstart, bool* pzhoda);
	
};

// NAM2
const vrchol analyzer::nPraz = vrchol("nPraz",PRAZDNY, false, NULL, NULL);
const vrcholvolny analyzer::nDal = vrcholvolny("nDal",'E', true, &analyzer::nDal, &analyzer::nPraz);	
const vrcholvolny analyzer::nprve = vrcholvolny("nprve",'D',true, &analyzer::nDal, NULL);

const celo analyzer::nam2 = celo('2', &analyzer::nprve);
const celo analyzer::nam1 = celo('N', &analyzer::nprve);
// NAMEX
const vrchol analyzer::nPrazEx = vrchol("nPrazEx",PRAZDNY, false, NULL, NULL);
const vrcholvzatvorkach analyzer::nDalEx = vrcholvzatvorkach("nDalEx",'E', true, &analyzer::nDalEx, &analyzer::nPrazEx);	
const vrcholvzatvorkach analyzer::nprveex = vrcholvzatvorkach("nprveex",'D',true, &analyzer::nDalEx, NULL);

const celo analyzer::namex2 = celo('2', &analyzer::nprveex);
const celo analyzer::namex1 = celo('N', &analyzer::nprveex);	

const vrchol analyzer::konPraz = vrchol("konPraz",PRAZDNY, false, NULL, NULL);
const vrcholoddelovace analyzer::konSpace = vrcholoddelovace("konSpace",' ', false, &analyzer::konSpace, &analyzer::konPraz);
const vrcholidendelim analyzer::dq22 = vrcholidendelim("dq22",'"', false, &analyzer::konSpace, NULL);
const vrchol analyzer::namex2nterm = vrchol("namex2nterm",&analyzer::namex2, false, &analyzer::dq22, NULL);
const vrchol analyzer::nam2nterm = vrchol("nam2nterm",&analyzer::nam2, false, &analyzer::konSpace, NULL);
const vrcholidendelim analyzer::dq21 = vrcholidendelim("dq21",'"', false, &analyzer::namex2nterm, &analyzer::nam2nterm);   
const vrcholschemadelim analyzer::charDot = vrcholschemadelim("charDot",'.', false, &analyzer::dq21, &analyzer::konSpace);  
const vrcholidendelim analyzer::dq12 = vrcholidendelim("dq12",'"', false, &analyzer::charDot, NULL);
const vrchol analyzer::namex1nterm = vrchol("namex1nterm", &analyzer::namex1, false, &analyzer::dq12, NULL);
const vrchol analyzer::nam1nterm = vrchol("nam1nterm",&analyzer::nam1, false, &analyzer::charDot, NULL);
const vrcholidendelim analyzer::dq11 = vrcholidendelim("dq11",'"', false, &analyzer::namex1nterm, &analyzer::nam1nterm);      
const vrchol analyzer::zacPraz = vrchol("zacPraz",PRAZDNY, false, &analyzer::dq11, NULL);
const vrcholoddelovace analyzer::zacSpace = vrcholoddelovace("zacSpace",' ', false, &analyzer::zacSpace, &analyzer::zacPraz);	

const celo analyzer::star = celo('S', &analyzer::zacSpace);

void analyzer::analyzator( const celo* pstart, bool* pzhoda)
{
	const vrchol* pakt = pstart->vstup;
	
	do {
	//	std::cerr << "inloop" << std::endl;
		if (pakt->term) {
			//std::cerr << "interm" << std::endl;
			if (pakt->isEqual(sym(), *p_data)) {
			//	std::cerr << pakt->pid << ": isequ" << std::endl;
			    *pzhoda = true;
			  //  std::cerr << "istr" << std::endl;
			    if (pakt->usesym)
			        identif[pstart]->push_back(sym());
			    //std::cerr << "istokset" << std::endl;    
			    nextsym();
			    //std::cerr << "isnext" << std::endl; 
			} else 
			    *pzhoda = (pakt->tsym == PRAZDNY); 
		} else {
			identif[pakt->nsym]->clear();
			//std::cerr << "rek" << std::endl;	
		    analyzator(pakt->nsym, pzhoda);
		}
		//std::cerr << '"' << pakt->pid << "\" " << (*pzhoda?"true":"false") << std::endl;
	    pakt = *pzhoda ? pakt->suc:pakt->alt;	    
	} while (pakt != NULL);
}

*/

class analyzer 
{
	public:
	analyzer(datasource* pdat)
	{
        st.currpos = 0;
        st.zhoda = false;
        st.pdata = pdat;
        st.currident = NULL;
	}
    static const nsymbol start;
    static const nsymbol B;
    static const nsymbol C;
    static const ssymbol dot;
    static const tsymbol p1;
    static const tsymbol b1;
    static const asymbol i1;
    static const asymbol i2;
    static const esymbol e1;
    static const wsymbol s1;
    static const wsymbol s2;
    static const esymbol e2;
    static const esymbol e3;

    parsestatus st;
    void analyze (void)
    {
        start.process(&st);
        if (!eof2(st.pveta,st.currpos))  
            st.zhoda = false;
    }
};

/*
 * ------------>--->[B]--dot-->[C]----------->-->
 *     ^       |                     ^       |
 *     |       |                     |       |
 *      -- s <-                       -- s <-
 *
 *    s je space
 * 
 * B/C----> i1 ----------->-------
 *             ^       |
 *             |       | 
 *              -- i2 <-
 */ 
const esymbol analyzer::e1 = esymbol( NULL, NULL);
const asymbol analyzer::i2 = asymbol( &analyzer::i2, &analyzer::e1);
const asymbol analyzer::i1 = asymbol( &analyzer::i2, NULL);

const esymbol analyzer::e3 = esymbol( NULL, NULL);
const wsymbol analyzer::s2 = wsymbol( &analyzer::s2, &analyzer::e3);

const nsymbol analyzer::C = nsymbol('C', &analyzer::i1, &analyzer::s2, NULL);
const ssymbol analyzer::dot = ssymbol( &analyzer::C, NULL);

const nsymbol analyzer::B = nsymbol('B', &analyzer::i1, &analyzer::dot, NULL);

const esymbol analyzer::e2 = esymbol( &analyzer::B, NULL);
const wsymbol analyzer::s1 = wsymbol( &analyzer::s1, &analyzer::e2);

const nsymbol analyzer::start = nsymbol(PRAZDNY, &analyzer::s1, NULL, NULL);

int main(void) {	

	datasource dt;

	priprav_vety();
	for(idVeta = 0;idVeta < vety.size(); idVeta++) {
        
        analyzer an(&dt);
        an.st.pveta = &vety[idVeta];
        an.analyze();
        std::cout << "|" << *(an.st.pveta) << "| => ";
        if (an.st.zhoda) {
            std::cout << "OK id['B']=" << "|" << an.st.identifiers['B'] << "|";
            std::cout << ", id['C']=" << "|" << an.st.identifiers['C'] << "|";
        } else
            std::cout << "NOK";
        std::cout  << std::endl;
	}
    return 0;
}
