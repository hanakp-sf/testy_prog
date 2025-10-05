#include <iostream>

class Pokus
{
  public:
    Pokus(int phod = 0 ):hod(phod)
    {
       std::cout << "Pokus constructor" << std::endl;
    }
    Pokus& operator=(const Pokus& cp)
    { hod = cp.hod; 
      std::cout << "Pokus copy constructor" << std::endl;
      return *this;}
    int obsah(void) {return hod;}
    int hod;
};

int main(void)
{
  Pokus pok = Pokus(2);
  Pokus pk (3);


  std::cout << "pok: " << pok.obsah() << std::endl;
  pok = pk;
  return 0;
}