#include "bezmen.h"

namespace {
class cprivate
{
public:
  cprivate(int p);
  int j;
};

cprivate::cprivate(int p):j(p)
{
}

}

cpublic::cpublic(void):cp(new cprivate(3))
{
}

cpublic::~cpublic()
{
  delete cp;
}

int main(void)
{
  cpublic j;
  return 0;
}