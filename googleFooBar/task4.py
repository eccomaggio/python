from tkinter import W


m = [
  [0,1,0,0,0,1],  # s0, the initial state, goes to s1 and s5 with equal probability
  [4,0,0,3,2,0],  # s1 can become s0, s3, or s4, but with different probabilities
  [0,0,0,0,0,0],  # s2 is terminal, and unreachable (never observed in practice)
  [0,0,0,0,0,0],  # s3 is terminal
  [0,0,0,0,0,0],  # s4 is terminal
  [0,0,0,0,0,0],  # s5 is terminal
]

m = [
[0, 2, 1, 0, 0], 
[0, 0, 0, 3, 4], 
[0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0], 
[0, 0, 0, 0, 0]
]


def prettify(m):
    print("...s0 s1 s2 s3 s4 s5")
    for row in range(len(m)):
        states = []
        denominator = sum(m[row])
        if not denominator:
          denominator = ""
        else:
          denominator = f"/{denominator}"
        for j in range(len(m[row])):
            probability = m[row][j]
            if probability != 0:
                states += [f"s{j} ({probability})"]
        print(f"s{row}",m[row], f"s{row}=>",states, denominator)
        
def solution(m):
  # paths = ["*"]
  all_s = len(m[0])
  terminal_s = {i: [] for i in range(all_s) if sum(m[i]) == 0}
  print(terminal_s)
  # paths = check_path(m,0,paths)
  # for terminal in terminal_s.keys():
  #   print(f"\n...terminal: s{terminal}:")
  #   for row_i in range(len(m) - 1, -1, -1):
  #     check_path(m, row_i,terminal)
  path = recurse()
  return path

# def check_path(m, state, paths):
#   row = m[state]
#   if sum(row):
#     for s in range(len(row)):
#       val = row[s]
#       if val:
#         print(f"s{state}: s{s}={val}")
#         paths = [[f"{state}: s{s}={val}"] + check_path(m, s, paths)]
#   return paths


def check_path(m, row_i, target):
  if row_i < 0:
    return 
  else:
    row = m[row_i]
    # print(">>>",row)
    if sum(row):
      val = row[target]
      if val:
        # print(f"s{row_i}: target={target}, val={val}")
        tmp = [f"{row_i}: s{target} ({val})"]
        print(*tmp)
        check_path(m, row_i - 1, row_i)
      else:
        return 
    else:
      return 


def recurse(s=0, path=None, depth=-1):
  # global terminal_s
  global m
  print(">>&", s,depth,sum(m[s]))
  path = path if path else []
  depth += 1
  path.append([s])
  if not sum(m[s]):
    print("!! terminal")
    return path
  elif depth > 100:
    print("!! too deep")
    return path
  else:
    for s1 in m[s]:
      recurse(s1, path, depth)





prettify(m)
x = solution(m)
print(x)