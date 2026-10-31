def second_largest(arr):
  arr = sorted([*set(arr)], reverse=True)
  print(arr)
  return arr[1]


tests = (
  ([1, 2, 3, 4] , 3),
  ([20, 139, 94, 67, 31], 94),
  ([2, 3, 4, 6, 6], 4),
  ([10, -17, 55.5, 44, 91, 0], 55.5),
  ([1, 0, -1, 0, 1, 0, -1, 1, 0], 0)
)


for i, test in enumerate(tests, start=1):
  a, answer = test
  result = second_largest(a)
  isCorrect = result == answer
  print(f"{i}: {a}\n\t=> {answer} \n\t= {isCorrect} [{result}]\n")
