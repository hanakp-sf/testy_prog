#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#define PLUS 1
#define MINUS 0
#define ANO 1
#define NIE 0
#define MAX 1000

int  distribucia[] = {MINUS,PLUS,MINUS};
char oper[] = {'-','+'};
int koef[] = { -1,1};


int main(int argc, char* argv[]){
	time_t secs;
	int vstup,operacia,prvy,druhy,vysledok,odpoved, limit = 0; 
	int opakovat = NIE;
  
  if (argc > 1)
    limit = atoi(argv[1]);
  if (limit < 1)
    limit = MAX;
  secs = time(NULL);
	srand((unsigned int) secs);
	do{
		if (opakovat == NIE ){
  	  operacia = distribucia[rand()%3];
      prvy = rand()%(limit+1); 
	    druhy = prvy == limit? 0: rand()%(limit+1-prvy); 
      if ( operacia == MINUS && prvy < druhy ){
        // vymena
        vysledok = prvy;
        prvy = druhy;
        druhy = vysledok;
      }
      vysledok = prvy + koef[operacia]*druhy;
		}else
      opakovat = NIE;
		printf("%d %c %d = ",prvy,oper[operacia],druhy);
  	
    vstup = getchar();
		if(vstup == '\n')
			break;
    odpoved = 0;	
		while(vstup != '\n') {
      vstup -= 48;
      if (vstup > 9 || vstup < 0)
        opakovat = ANO;
      
      odpoved = 10*odpoved + vstup;
      vstup = getchar();
    }
		if((opakovat == NIE) && (odpoved == vysledok)){
		  printf (" Dobre !\n");
		}else{
			printf(" Zle !\n");
			opakovat = ANO;
		}
	}while(1); 
	return 0;
}
