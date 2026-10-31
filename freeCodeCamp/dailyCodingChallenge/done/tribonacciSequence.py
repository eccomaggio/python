def tribonacci_sequence(start_sequence, length):
  current_pos = 3
  sequence = [*start_sequence]
  while current_pos < length:
    sub_sequence = sequence[current_pos - 3:current_pos]
    sequence.append(sum(sub_sequence))
    current_pos += 1
  sequence = sequence[:length]
  return sequence


tests:tuple[tuple[list[int], int, list[int]],...] = (
  ([0, 0, 1], 20,[0, 0, 1, 1, 2, 4, 7, 13, 24, 44, 81, 149, 274, 504, 927, 1705, 3136, 5768, 10609, 19513]),
  ([21, 32, 43], 1,  [21]),
  ([0, 0, 1], 0, []),
  ([10, 20, 30], 2, [10, 20]),
  ([10, 20, 30], 3, [10, 20, 30]),
  ([123, 456, 789], 8,[123, 456, 789, 1368, 2613, 4770, 8751, 16134]),
  )

for i, test in enumerate(tests, start=1):
    a, b, answer = test
    result = tribonacci_sequence(a, b)
    isCorrect = result == answer
    print(f"{i}: {a}, {b} \n\t{answer} \n\t= {isCorrect}\n\t[{result}]\n")
