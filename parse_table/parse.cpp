#include <iostream>
#include <vector>

#define PRAZDNY '\0'

typedef char CHAR;

class vrchol;

class celo
{
	public:
	celo(char psym, vrchol* pvstup):sym(psym), vstup(pvstup), pvtoken(NULL)
	{
	}
	char sym;
	vrchol* vstup;
	std::basic_string<CHAR>* pvtoken;
};

class vrchol 
{
    public:
	vrchol(char ptsym, bool pusesym, vrchol* psuc, vrchol* palt):tsym(ptsym), suc(psuc), 
	alt(palt), usesym(pusesym), term(true)
	{
		pid = "DEF";
	}
	vrchol* alt;
	vrchol* suc;
	bool usesym;
	const char* pid;
	bool term;
	union {
	    char tsym;
	    celo* nsym;
	};
	bool virtual isEqual(char c) {
		return tsym == c;
	}
};

class vrcholoddelovace: public vrchol
{
	public:
	vrcholoddelovace(char ptsym, bool pusesym, vrchol* psuc, vrchol* palt):vrchol(ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c) {
		return isspace(c);
	}		
};



class vrcholvzatvorkach: public vrchol
{
	public:
	vrcholvzatvorkach(char ptsym, bool pusesym, vrchol* psuc, vrchol* palt):vrchol(ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c) {
		return c != '"';
	}		
};

class vrcholvolny: public vrchol
{
	public:
	vrcholvolny(char ptsym, bool pusesym, vrchol* psuc, vrchol* palt):vrchol(ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c) {
		return (c != '"') && (c != '.') && !isspace(c) && (c != PRAZDNY);
	}		
};

std::vector<std::string> vety; 

int pos = 0;
int idVeta = 0;
bool bezchyba = true;

void priprav_vety()
{
	vety.push_back("cb");
	vety.push_back(" BATGYTU  ");
	vety.push_back("  cATG.YTU  ");
	vety.push_back("BA.   ");
	vety.push_back("b\"A");
	vety.push_back( "B.n" );
	vety.push_back("S k");
	vety.push_back("s");
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

void analyzator( celo* pstart, bool* pzhoda)
{
	vrchol* pakt = pstart->vstup;
	
	do {
	//	std::cerr << "inloop" << std::endl;
		if (pakt->term) {
		//	std::cerr << "interm" << std::endl;
			if (pakt->isEqual(sym())) {
			//	std::cerr << "isequ" << std::endl;
			    *pzhoda = true;
			  //  std::cerr << "istr" << std::endl;
			    if (pakt->usesym && pstart->pvtoken)
			        pstart->pvtoken->push_back(sym());
			    //std::cerr << "istokset" << std::endl;    
			    nextsym();
			    //std::cerr << "isnext" << std::endl; 
			} else 
			    *pzhoda = (pakt->tsym == PRAZDNY); 
		} else {
            if (pakt->nsym->pvtoken)
			    pakt->nsym->pvtoken->clear();
		//	std::cerr << "rek" << std::endl;	
		    analyzator(pakt->nsym, pzhoda);
		}
	//	std::cerr << '"' << pakt->pid << "\" " << (*pzhoda?"true":"false") << std::endl;
	    pakt = *pzhoda ? pakt->suc:pakt->alt;	    
	} while (pakt != NULL);
}

int main(void) {	
	// STR2
	vrchol nPraz = vrchol(PRAZDNY, false, NULL, NULL);
	vrcholvolny nDal = vrcholvolny('E', true, &nDal, &nPraz);	
	vrcholvolny nprve = vrcholvolny('D',true, &nDal, NULL);
	celo str2 = celo('2', &nprve);
	
	// STR1
	vrchol nPraz1 = vrchol(PRAZDNY, false, NULL, NULL);
	vrcholvolny nDal1 = vrcholvolny('F', true, &nDal1, &nPraz1);	
	vrcholvolny nprve1 = vrcholvolny('P',true, &nDal1, NULL);	
	celo str1 = celo('N', &nprve1);

	vrchol konPraz = vrchol(PRAZDNY, false, NULL, NULL);
	vrcholoddelovace konSpace = vrcholoddelovace(' ', false, &konSpace, &konPraz);

    vrchol str2nterm = vrchol('2', false, &konSpace, NULL);
    vrchol charDot = vrchol('.', false, &str2nterm, &konSpace);
    vrchol str1nterm = vrchol('1', false, &charDot, NULL);

	vrchol zacPraz = vrchol(PRAZDNY, false, &str1nterm, NULL);
	vrcholoddelovace zacSpace = vrcholoddelovace(' ', false, &zacSpace, &zacPraz);
	
	celo star = celo('S', &zacSpace);
	
	str2nterm.nsym = &str2;
	str2nterm.term = false;
	str1nterm.nsym = &str1;
	str1nterm.term = false;
	
	zacSpace.pid = "zacSpace";
	zacPraz.pid = "zacPraz";
	str1nterm.pid = "str1nterm";
	
/*	vrchol2 charAA = vrchol2('A', true, NULL,NULL);
	vrchol charc = vrchol('c', true, &charAA,NULL);
	vrchol charB = vrchol('B', true, &charAA,&charc);
	vrchol charPraz = vrchol(PRAZDNY, false, &charB, NULL);
	vrchol charSpace = vrchol(' ', false, &charSpace, &charPraz);
	celo cstart = celo('S', &charSpace);*/
	std::string vt1;
	std::string vt2;

	priprav_vety();
	str1.pvtoken = &vt1;
	str2.pvtoken = &vt2;
	for(idVeta = 0;idVeta < vety.size(); idVeta++) {
		pos = 0;
		bezchyba = true;
		vt1.clear();
		vt2.clear();
	    analyzator(&star, &bezchyba);
        std::cout << "\"" << vety[idVeta] << "\" => "<< (bezchyba && eof()?"OK":"NOK") << ", VT:\"" << vt1 
        << '"'  << ", VT2:\"" << vt2 << '"' << std::endl;
	}
    return 0;
}
