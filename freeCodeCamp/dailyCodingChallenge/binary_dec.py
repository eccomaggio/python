def to_decimal(binary):
  n = [
     2 ** i
     for i, el in enumerate(binary[::-1])
     if int(el)
  ]
  return sum(n)

tests = [
    ("101", 5),
    ("1010", 10),
    ("10010", 18),
    ("1010101", 85),
]

for i, test in enumerate(tests, start=1):
    a, answer = test
    result = to_decimal(a)
    isCorrect = result == answer
    print(
        f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n"
    )
