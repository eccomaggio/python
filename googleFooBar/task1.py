# Online Python 2.7 Compiler

from collections import OrderedDict

def solution(data,n):
    return [i for i in data if data.count(i) <= n and isinstance(i,int)]
    

	
x =   [1, 2, 3 , 3.3]

print(solution(x,6))
