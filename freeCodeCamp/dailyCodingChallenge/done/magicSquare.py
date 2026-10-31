def solve_magic_square(grid):
  vertical = []
  total = 0
  index_of_zero_row = -1
  for i, row in enumerate(grid):
    if 0 in row:
      index_of_zero_row = i
    vertical.append([])
    for j in range(len(grid[0])):
      vertical[i].append(grid[j][i])
  for row in [*grid, *vertical]:
    if 0 not in row:
      total = check_square(total, row)
      if total < 0:
        return "impossible"
  return total - sum(grid[index_of_zero_row])

# def solve_magic_square(grid):
#   vertical = []
#   total = 0
#   index_of_zero_row = -1
#   for i, row in enumerate(grid):
#     if 0 in row:
#       index_of_zero_row = i
#     else:
#       total = check_square(total, row)
#       if total < 0:
#         return "impossible"
#     vertical.append([])
#     for j in range(len(grid[0])):
#       vertical[i].append(grid[j][i])
#   for col in vertical:
#     if 0 not in col:
#       total = check_square(total, col)
#       if total < 0:
#         return "impossible"
#   return total - sum(grid[index_of_zero_row])




def check_square(total, row:list[int]):
  new_total = sum(row)
  if total and new_total != total:
    return -1
  else:
    total = new_total
  return total



tests = (
  ([[2, 7, 6], [9, 0, 1], [4, 3, 8]], 5),
  ([[0, 14, 12], [18, 10, 2], [8, 6, 16]], 4),
  ([[12, 17, 16], [19, 0, 10], [14, 13, 18]], "impossible"),
  ([[15, 35, 31], [43, 27, 11], [23, 19, 0]], 39),
  ([[26, 41, 14], [47, 35, 0], [32, 29, 44]], "impossible"),
)

for i, test in enumerate(tests, start=1):
  a, answer = test
  result = solve_magic_square(a)
  isCorrect = result == answer
  print(f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n")