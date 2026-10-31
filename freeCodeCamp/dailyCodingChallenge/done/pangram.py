import re

def is_pangram(sentence, letters):
  s = re.sub(r'[^a-z]', '', sentence.lower())
  pangram = sorted(set(s))
  l = sorted(letters)
  result = pangram == l
  print(f"**{sentence} => {s}\n=>{pangram}\n=={l} ({letters})")
  return result


tests = (
  (("hello", "helo"), True),
  (("hello", "hel"), False),
  (("hello", "helow"), False),
  (("hello world", "helowrd"), True),
  (("Hello World!", "helowrd"), True),
  (("Hello World!", "heliowrd"), False),
  (("freeCodeCamp", "frcdmp"), False),
  (("The quick brown fox jumps over the lazy dog.", "abcdefghijklmnopqrstuvwxyz"),True),
)

for i, test in enumerate(tests, start=1):
    (a, b), answer = test
    result = is_pangram(a, b)
    isCorrect = result == answer
    print(f"{i}: {a}, {b} \n\t{answer} \n\t= {isCorrect}\n\t[{result}]\n")
