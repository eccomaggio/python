import re


def is_spam(number):
  country, area, local = number.split()
  local3, local4 = local.split("-")
  area = area[1:-1]
  country = country[1:]
  # for i, el in enumerate([country, area, local3, local4]):
  #   print(f"{i}: {el} {len(el)}")
  if len(area) != 3 or len(local3) != 3 or len(local4) != 4 or len(country) > 2:
    print("Wrong length")
    return True
  if not country.startswith("0"):
    print("Country code ({country}) must start with 0")
    return True
  if not (200 <= int(area) <= 900):
    print(f"Area code ({area}) must be between 200 and 900")
    return True
  total = f"{sum([int(el) for el in f'{local3}'])}"
  if total in local4:
    print(f"{total} is in {local4}")
    return True
  whole = f"{country}{area}{local3}{local4}"
  for digit in set(whole):
    pattern = f"{digit}{{4}}"
    res = re.search(pattern, whole)
    if res:
      print(f"{digit} => {res.group()}")
      return True

  return False


tests = (
  ("+0 (200) 234-0182", False),
  ("+091 (555) 309-1922", True),
  ("+1 (555) 435-4792", True),
  ("+0 (955) 234-4364", True),
  ("+0 (155) 131-6943", True),
  ("+0 (555) 135-0192", True),
  ("+0 (555) 564-1987", True),
  ("+00 (555) 234-0182", False),
)

for i, test in enumerate(tests, start=1):
    a, answer = test
    result = is_spam(a)
    isCorrect = result == answer
    print(
        f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n"
    )
