def parse_roman_numeral(numeral):
  lookup = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
  }
  total = 0
  prev_el = 0
  for string_el in reversed(numeral):
    el = lookup[string_el]
    if el >= prev_el:
      total += el
    else:
      total -= el
    prev_el = el
  return total

tests = (
  ("III", 3),
  ("IV", 4),
  ("XXVI", 26),
  ("XCIX", 99),
  ("CDLX", 460),
)

for i, test in enumerate(tests, start=1):
  a, answer = test
  result = parse_roman_numeral(a)
  isCorrect = result == answer
  print(f"{i}: {a} = {result} {isCorrect} [{answer}]\n")
