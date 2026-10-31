import pprint
from collections import defaultdict
import itertools


def bucket_fill(grid, target_color):
  if not grid or not grid[0]:
    return 0
  row_max, col_max = len(grid), len(grid[0])
  visited = set()
  stats = []
  designator = 0

  def trace_area(start_row, start_col, colour, visited):
    stack = [(start_row, start_col)]
    visited.add((start_row, start_col))
    while stack:
      row, col = stack.pop()
      for r, c in [(0,1), (0, -1), (1, 0), (-1, 0)]: # [right, left, top, bottom]
        row_num, col_num = row + r, col + c
        if (
            0 <=row_num < row_max and
            0 <= col_num < col_max and
            grid[row_num][col_num] == colour and
            (row_num, col_num) not in visited
          ):
          # visited = trace_area(row_num, col_num, colour, visited)
          visited.add((row_num, col_num))
          stack.append((row_num, col_num))
    return visited

  for row_num, row in enumerate(grid):
    for col_num, colour in enumerate(row):
      if (row_num, col_num) in visited:
        continue
      old_visited = visited.copy()
      visited = trace_area(row_num, col_num, colour, visited)
      # print(f"*{designator} [{colour}] = {visited.difference(old_visited)}")
      current = [designator, colour, visited.difference(old_visited)]
      stats.append(current)
      designator += 1

  print("stats:")
  pprint.pp(stats)
  consolidated = defaultdict(int)
  largest = {}
  for designator, colour, locations in stats:
    if not consolidated[colour]:
      largest[colour] = next(iter(locations))
    consolidated[colour] += len(locations)
  # print(f"{largest=}")

  ordered = sorted(consolidated.items(), key=lambda x:x[1], reverse=True)
  ordered = [(colour, total, largest[colour]) for colour, total in ordered]
  print(f"{ordered=}")
  if len(ordered) == 1 and ordered[0][0] == target_color:
    return 0
  next_colour = [*[colour for colour, *_ in ordered][1:], target_color]
  print(f"{next_colour=}")
  instructions = []
  return len(consolidated)


tests = (
([
  ["B", "B"],
  ["B", "B"]
    ], "R", 1),
  ([
    ["G", "G", "G"],
    ["G", "G", "G"],
    ["G", "G", "G"]
    ], "G", 0),
  ([
    ["P", "P", "Y"],
    ["Y", "P", "Y"],
    ["Y", "P", "P"]
    ], "O", 2),
  ([
    ["G", "Y", "C", "C"],
    ["Y", "Y", "Y", "B"],
    ["C", "Y", "B", "B"],
    ["C", "B", "B", "C"]
    ], "R", 4),
  ([
    ["G", "G", "O", "O"],
    ["G", "Y", "B", "Y"],
    ["B", "Y", "B", "Y"],
    ["B", "Y", "B", "Y"],
    ["G", "G", "G", "G"]
    ], "P", 5),
  ([
    ["R", "G", "R", "G"],
    ["R", "G", "R", "G"],
    ["B", "B", "B", "B"],
    ["B", "B", "B", "B"],
    ["R", "G", "R", "G"]
    ], "Y", 3),
)

for i, test in enumerate(tests, start=1):
    a, b, answer = test
    result = bucket_fill(a, b)
    isCorrect = result == answer
    print(
        f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n"
    )


"""
The Last Challenge: Bucket Fill 3
Today marks a year of daily coding challenges. This is the last new one for now. Good luck!

Given a 2D grid of single-letter color strings and a target color, return the minimum number of flood fill "clicks" needed to make the entire grid that color.

Each click changes the clicked cell's color and the entire region of connected cells of the same color (4-directional).
Clicks can use any color as an intermediate step, not just the target color.
"""


## The version using recursion
# def bucket_fill(grid, target_color):
#   visited = set()
#   stats = []
#   designator = 0

#   def trace_area(row_num, col_num, colour, visited):
#     if (row_num, col_num) in visited or colour != grid[row_num][col_num]:
#       return visited
#     visited.add((row_num, col_num))
#     for r, c in [(0,1), (0, -1), (1, 0), (-1, 0)]: # [right, left, top, bottom]
#       new_row, new_col = row_num + r, col_num + c
#       if 0 <=new_row < len(grid) and 0 <= new_col < len(grid[0]):
#         visited = trace_area(new_row, new_col, colour, visited)
#     return visited

#   for row_num, row in enumerate(grid):
#     for col_num, colour in enumerate(row):
#       if (row_num, col_num) in visited:
#         continue
#       old_visited = visited.copy()
#       visited = trace_area(row_num, col_num, colour, visited)
#       # print(f"*{designator} [{colour}] = {visited.difference(old_visited)}")
#       current = [designator, colour, visited.difference(old_visited)]
#       stats.append(current)
#       designator += 1
#   consolidated = defaultdict(int)
#   for el in stats:
#     consolidated[el[1]] += len(el[2])

#   ordered = sorted(consolidated.items(), key=lambda x:x[1], reverse=True)
#   pprint.pp(stats)
#   print(ordered)
#   if len(ordered) == 1 and ordered[0][0] == target_color:
#     return 0
#   return len(consolidated)
