def build_acronym(s):
  acronym = ""
  for i, word in enumerate(s.split()):
    to_ignore = ["a", "for", "an", "and", "by", "of"]
    if i > 0 and word.lower() in to_ignore:
      continue
    acronym += word[0]
  return acronym.upper()





tests = (
  ("Search Engine Optimization", "SEO"),
  ("Frequently Asked Questions", "FAQ"),
  ("National Aeronautics and Space Administration", "NASA"),
  ("Federal Bureau of Investigation", "FBI"),
  ("For your information", "FYI"),
  ("By the way", "BTW"),
  ("An unstoppable herd of waddling penguins overtakes the icy mountains and sings happily", "AUHWPOTIMSH"),
)


for i, test in enumerate(tests, start=1):
  a, answer = test
  result = build_acronym(a)
  isCorrect = result == answer
  print(f"{i}: {a}\n\t=> {answer} \n\t= {isCorrect} [{result}]\n")