#include<stdio.h>

/*
void SwapValues(unsigned int *pVal1, unsigned int *pVal2)
{

assert(pVal1 != NULL);
assert(pVal2 != NULL);

}

3. You have following code, what will be value of "b"?

int a[10] = {1,2,3,4,5,6,7,8,9,10}
int *b = *(&a[3] + 2);

4. Write macro which will return minimum of two given numbers.

5. You have value in "a" stored as big endian, write code to change its value to little endian.
*/

void main( void )
{
    int a[10] = { 1,2,3,4,5,6,7,8,9,10 };
    int* b = *(&a[3] + 2); // adresa a[5]
    printf("a=%#x\n", a);
    printf("a[1]=%#x\n", a +1 );
    printf("a[2]=%#x\n", a +2 );
    printf("b=%#x\n", b);
}
