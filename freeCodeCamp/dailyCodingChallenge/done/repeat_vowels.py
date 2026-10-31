def repeat_vowels(s):
  vowel_count = 0
  new_s = ""
  for letter in s:
    extra = ""
    if letter in "aeiouAEIOU":
      extra = letter.lower() * vowel_count
      vowel_count += 1
    new_s = f"{new_s}{letter}{extra}"
    # print(f"{letter} * {vowel_count} = {extra} => {new_s}")
  return new_s

tests = (
  ("hello world", "helloo wooorld"),
  ("freeCodeCamp", "freeeCooodeeeeCaaaaamp"),
  ("AEIOU", "AEeIiiOoooUuuuu"),
  ("I like eating ice cream in Iceland", "I liikeee eeeeaaaaatiiiiiing iiiiiiiceeeeeeee creeeeeeeeeaaaaaaaaaam iiiiiiiiiiin Iiiiiiiiiiiiceeeeeeeeeeeeelaaaaaaaaaaaaaand"),
)

for i, test in enumerate(tests, start=1):
    a, answer = test
    result = repeat_vowels(a)
    isCorrect = result == answer
    print(f"{i}: {a}\n\t=> {answer} \n\t= {isCorrect} [{result}]\n")
