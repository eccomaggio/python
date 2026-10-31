def to_binary(decimal):
  binary = ""
  while decimal:
    decimal, mod = divmod(decimal, 2)
    binary = f"{binary}{mod}"
  return binary[::-1]


tests = [
    (5, "101"),
    (12, "1100"),
    (50, "110010"),
    (99, "1100011"),
]

for i, test in enumerate(tests, start=1):
    a, answer = test
    result = to_binary(a)
    isCorrect = result == answer
    print(
        f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n"
    )
