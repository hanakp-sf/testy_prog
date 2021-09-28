#include <iostream>
#include <map>

int main(void)
{
    std::map<const char, std::string>  ident;
    
    ident.insert(std::pair<const char, std::string>('A',std::string("a-val")));
    ident.insert(std::pair<const char, std::string>('B',std::string("b-val")));
    
    ident['C'].push_back('d');
    std::cout << '"' << ident['A'] << '"' << std::endl;
    std::cout << '"' << ident['B'] << '"' << std::endl;
    std::cout << '"' << ident['C'] << '"' << std::endl;
    ident['C'].clear();
    ident['C'].push_back('D');
    ident['C'].push_back('M');
    std::cout << '"' << ident['C'] << '"' << std::endl;
}
