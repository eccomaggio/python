def get_food_chain(pairs):
  if len(pairs) == 1:
    return pairs[0]
  predators = {pair[0] for pair in pairs}
  prey = {pair[1] for pair in pairs}
  apex = list(predators.difference(prey))[0]
  result = [apex]
  while pairs:
    for i in range(len(pairs)):
      predator, prey = pairs[i]
      if predator == apex:
        result.append(prey)
        apex = prey
        pairs.pop(i)
        break

  return result


tests = (
  ([["cat", "mouse"]], ["cat", "mouse"]),
  ([["wolf", "deer"], ["deer", "grass"]], ["wolf", "deer", "grass"]),
  ([["hawk", "snake"], ["snake", "frog"], ["frog", "fly"]], ["hawk", "snake", "frog", "fly"]),
  ([["rabbit", "grass"], ["fox", "rabbit"], ["eagle", "fox"]], ["eagle", "fox", "rabbit", "grass"]),
  ([["seal", "salmon"], ["herring", "shrimp"], ["orca", "seal"], ["shrimp", "plankton"], ["salmon", "herring"]], ["orca", "seal", "salmon", "herring", "shrimp", "plankton"]),
)

for i, test in enumerate(tests, start=1):
  a, answer = test
  result = get_food_chain(a)
  isCorrect = result == answer
  print(f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n")