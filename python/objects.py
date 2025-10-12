a = 'abc'
b = 'abc'
 
class Node:
    def __init__(self, data):
        self.data = data
        
    def __eq__(self, other):
        return self.data == other.data
            
if  __name__ == '__main__':
    print ("a,b su strings")
    print(f'id(a) = {id(a)}')
    print(f'id(b) = {id(b)}')
    print(f'a is b: {a is b}')
    print(f'a == b: {a == b}')
    
    print('---------------------------')
    c = Node('A')
    d = c
    print ("c,d su ten isty object")
    print(f'id(c) = {id(c)}')
    print(f'id(d) = {id(d)}')
    print(f'c is d: {c is d}')
    print(f'c == d: {c == d}')
    
    print('---------------------------')
    c = Node('A')
    d = Node('A')
    print ("c,d su ten rozne object")
    print(f'id(c) = {id(c)}')
    print(f'id(d) = {id(d)}')
    print(f'c is d: {c is d}')
    print(f'c == d: {c == d}')