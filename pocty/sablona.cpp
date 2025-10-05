#include <iostream>

template <typename T>
class Inc 
{
 public:
  Inc(T hod):hodnota(hod)
  {
  }
  T get( void) { return hodnota; }
  Inc& operator++(int) {
    hodnota++;
    return *this;
  }
 private:
  T hodnota;
};

void fun( const Inc<int>& rf )
{
  rf++; // generuje chybu
}

int main(void)
{
  Inc<int> ciselny (4);
  fun(ciselny);
  std::cout << "vx: " << ciselny.get() << std::endl;
  return 0;
}