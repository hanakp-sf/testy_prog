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
	}
	vrchol* alt;
	vrchol* suc;
	bool usesym;
	bool term;
	union {
	    char tsym;
	    celo* nsym;
	};
	bool virtual isEqual(char c) {
		return tsym == c;
	}
};

class vrchol2: public vrchol
{
	public:
	vrchol2(char ptsym, bool pusesym, vrchol* psuc, vrchol* palt):vrchol(ptsym,pusesym,psuc,palt)
	{
	}
	bool virtual isEqual(char c) {
		return c == 'A' || c == '<';
	}		
};

std::vector<std::string> vety; 

int pos = 0;
int idVeta = 0;
bool bezchyba = true;

void priprav_vety()
{
	vety.push_back("cATGYTU");
	vety.push_back(" BATGYTU");
	vety.push_back("  cATGYTU");
	vety.push_back("BA");
	vety.push_back("bA");
	vety.push_back( "B<nj" );
	vety.push_back("S");
}

char sym()
{
	return (pos < vety[idVeta].length()) ? vety[idVeta][pos]: '\0';
}

void nextsym()
{
	pos++;
}

void analyzator( celo* pstart, bool* pzhoda)
{
	vrchol* pakt = pstart->vstup;
	
	do {
		if (pakt->term) {
			if (pakt->isEqual(sym())) {
			    *pzhoda = true;
			    if (pakt->usesym && pstart->pvtoken)
			        pstart->pvtoken->push_back(sym());
			    nextsym();
			} else 
			    *pzhoda = (pakt->tsym == PRAZDNY); 
		} else {
            if (pakt->nsym->pvtoken)
			    pakt->nsym->pvtoken->clear();
		    analyzator(pakt->nsym, pzhoda);
		}
	    pakt = *pzhoda ? pakt->suc:pakt->alt;	    
	} while (pakt != NULL);
}

int main(void) {
	vrchol2 charAA = vrchol2('A', true, NULL,NULL);
	vrchol charc = vrchol('c', true, &charAA,NULL);
	vrchol charB = vrchol('B', true, &charAA,&charc);
	vrchol charPraz = vrchol(PRAZDNY, false, &charB, NULL);
	vrchol charSpace = vrchol(' ', false, &charSpace, &charPraz);
	celo cstart = celo('S', &charSpace);
	std::string vt;

	priprav_vety();
	cstart.pvtoken = &vt;
	for(idVeta = 0;idVeta < vety.size(); idVeta++) {
		pos = 0;
		bezchyba = true;
		vt.clear();
	    analyzator(&cstart, &bezchyba);
        std::cout << "\"" << vety[idVeta] << "\" => "<< (bezchyba?"OK":"NOK") << ", VT:\"" << vt << '"' << 
        " Pos:" << pos << std::endl;
	}
    return 0;
}
