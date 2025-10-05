#include <iostream>

int main(void)
{
  int pre = 5;
  int pr2 = 89;
  int * const cislo = &pre;

  (*cislo)++;
   cislo = &pr2; // expected compile error
  std::cout << "cislo: " << *(cislo) << std::endl;
  return 0;
}