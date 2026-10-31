def rgb_to_hex(rgb):
  rgb_values = rgb[4:-1]
  r, g, b = [int(el) for el in rgb_values.split(",")]
  print(r, g, b)
  hex_values = f"#{make_hex_string(r)}{make_hex_string(g)}{make_hex_string(b)}"
  return hex_values

def make_hex_string(value):
  hex_val = hex(value)[2:]
  if len(hex_val) < 2:
    hex_val = f"0{hex_val}"
  return hex_val

tests = (
  ("rgb(255, 255, 255)", "#ffffff"),
  ("rgb(1, 11, 111)", "#010b6f"),
  ("rgb(173, 216, 230)", "#add8e6"),
  ("rgb(79, 123, 201)",  "#4f7bc9"),
)

for i, test in enumerate(tests, start=1):
  a, answer = test
  result = rgb_to_hex(a)
  isCorrect = result == answer
  print(f"{i}: {a}\n\t=> {answer} \n\t= {isCorrect} [{result}]\n")
