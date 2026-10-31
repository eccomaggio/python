import pprint

def rotate(matrix):
  col_count = len(matrix[0])
  if col_count < 2:
    return matrix
  length = col_count - 1
  rotated = [ [-1 for _ in range(col_count)] for _ in range(col_count)]
  # print(f"*** {length=}")
  # pprint.pprint(rotated, width=20)
  for row, line in enumerate(matrix):
    for col, value in enumerate(line):
      # print(f"row,col ({row},{col}) => col,row ({col}, {length - row}) = {value=}")
      rotated[col][length - row] = value
  # pprint.pprint(rotated, width=20)
  return rotated


tests = (
  ([[1]], [[1]]),
  ([[1, 2], [3, 4]], [[3, 1], [4, 2]]),
  ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[7, 4, 1], [8, 5, 2], [9, 6, 3]]),
  ([[0, 1, 0], [1, 0, 1], [0, 0, 0]], [[0, 1, 0], [0, 0, 1], [0, 1, 0]]),
)


for i, test in enumerate(tests, start=1):
    a, answer = test
    result = rotate(a)
    isCorrect = result == answer
    pprint.pprint(result, width=15)
    if isCorrect:
      # print(f"{i}: {a} \n\t{answer} is correct!!\n")
      print(f"{i}: correct!!\n")
    else:
      print(f"{i}: wrong!!\n")
      # print(f"{i}: {a} \n\t{answer} \n\t= **{isCorrect=}**\n\t[{result}]\n")