#include <iostream>
#include <vector>

typedef std::vector<int>::const_reverse_iterator cri;
int main(void)
{
  std::vector<int> vi;

  vi.push_back(1);
  vi.push_back(2);
  vi.push_back(-1);

  for( cri i = vi.crbegin(); i != vi.crend(); i++)
    std::cout << "vx: " << *i << std::endl;
  return 0;
}