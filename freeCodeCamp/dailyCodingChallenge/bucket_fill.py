import pprint


def bucket_fill(grid, target_color):
  visited = set()
  stats = []
  designator = 0
  for row_num, row in enumerate(grid):
    for col_num, value in enumerate(row):
      if (row_num, col_num) in visited:
        # print(f"**row: {row_num}[{col_num}] already visited")
        continue
      # print(f"**row: {row_num}[{col_num}] checking further...")
      cell_count = 0
      colour = value
      old_visited = visited.copy()
      cell_count, visited = trace_area(
        grid, row_num, col_num, colour, visited, cell_count
      )
      print(f"*{designator} [{colour}] = {visited.difference(old_visited)}")
      current = [designator, colour, cell_count]
      stats.append(current)
      designator += 1
  # all_inspected = sum([el[2] for el in stats])
  # total = len(grid) * len(grid[0])
  # print(f"**{all_inspected} and {len(visited)} should be same as {total} (total cell count) = {total == all_inspected}")
  pprint.pp(stats)
  without_target_colour = [el for el in stats if el[1] != target_color]
  return len(without_target_colour)

def trace_area(grid, row_num, col_num, colour, visited, cell_count):
  if (row_num, col_num) in visited or colour != grid[row_num][col_num]:
    return cell_count, visited
  visited.add((row_num, col_num))
  cell_count += 1
  for r, c in [(0,1), (0, -1), (1, 0), (-1, 0)]: # [right, left, top, bottom]
    new_row, new_col = row_num + r, col_num + c
    if 0 <=new_row < len(grid) and 0 <= new_col < len(grid[0]):
      cell_count, visited = trace_area(grid, new_row, new_col, colour, visited, cell_count)
  return cell_count, visited




tests = (
    ([["R", "R"],
      ["R", "R"]
      ], "G", 1),

    ([["B", "B", "B"],
      ["B", "B", "B"],
      ["B", "B", "B"]
      ], "B", 0),

    ([
      ["G", "Y", "Y"],
      ["G", "Y", "G"],
      ["Y", "Y", "G"]
      ], "R", 3),

    ([
      ["G", "G", "P", "Y"],
      ["O", "P", "P", "P"],
      ["O", "O", "P", "G"],
      ["G", "O", "O", "G"]
      ], "P", 5,),

    ([
      ["G", "G", "C", "C", "O"],
      ["B", "Y", "B", "Y", "O"],
      ["B", "J", "O", "J", "B"],
      ["G", "Y", "Y", "Y", "B"],
      ["G", "P", "P", "G", "G"]
      ], "Y", 12,),

    ([
      ["G", "G", "G", "G", "G"],
      ["G", "Y", "G", "Y", "G"],
      ["G", "Y", "G", "Y", "G"],
      ["G", "Y", "Y", "Y", "G"],
      ["G", "G", "G", "G", "G"]
      ], "Y", 1,),
)

for i, test in enumerate(tests, start=1):
    a, b, answer = test
    result = bucket_fill(a, b)
    isCorrect = result == answer
    print(
        f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n"
    )
