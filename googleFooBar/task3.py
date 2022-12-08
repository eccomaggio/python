def solutionVerbose(x,y,target):
    s = 1
    local = 1
    for end in range(1, x + y):
        s = s + end - 1
        print(end,s, [i for i in range(s , s + end)])
    print(f"x={x}, y={y}, id={s + x - 1} (target={target})")
    return s + x - 1

def solution(x,y):
    s = 1
    local = 1
    for end in range(1, x + y):
        s = s + end - 1
    return str(s + x - 1)

# (x + y -1)!! + (x - 1)

a = (3,2,9)
a = (5,10,96)
a = (4,7,49)
#a = (14,10,96)

#x = solution(*a)
#y = solution(b[0],b[1])
#tmp = solutionVerbose(*a)
tmp = solution(*a[:2])
print(tmp, int(tmp) == a[2])
#print(solution(y,y==b[2]))
