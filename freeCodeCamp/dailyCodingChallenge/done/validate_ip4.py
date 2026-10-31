import re

def is_valid_ipv4(ipv4):
  vals = [val for val in ipv4.split(".") if val]
  if len(vals) != 4:
    # print("ERROR: too long / short")
    return False
  for val in vals:
    if (other := re.sub(r'[0123456789]', "", val)):
      # print(f"ERROR: [{other}] shouldn't be there")
      return False
    if len(val) > 1 and val[0] == "0":
      # print(f"ERROR: [{val}] no trailing zeroes!")
      return False
    if int(val) > 255:
      # print(f"[ERROR: {int(val)} > 255")
      return False
  return True


tests = (
    ("192.168.1.1", True),
    ("0.0.0.0", True),
    ("255.01.50.111", False),
    ("255.00.50.111", False),
    ("256.101.50.115", False),
    ("192.168.101.", False),
    ("192168145213", False),
)

for i, test in enumerate(tests, start=1):
    a, answer = test
    result = is_valid_ipv4(a)
    isCorrect = result == answer
    if isCorrect:
      print(f"{i}: {a} \n\t{answer} is correct!!\n")
    else:
      print(f"{i}: {a} \n\t{answer} \n\t= **{isCorrect=}**\n\t[{result}]\n")