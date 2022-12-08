import re

def solution(s):
    r = [m.span()[0] for m in re.finditer('>', s)]
    l = [m.span()[0] for m in re.finditer('<', s)]
    #bows = [[b,bb] for b in r for bb in l ]
    return sum([1 for rb in r for lb in l if rb < lb]) * 2


a = "--->-><-><-->-"
b = ">----<"
c = "<<>><"

print(solution(a))
print(solution(b))
print(solution(c))
