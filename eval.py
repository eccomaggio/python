import re

# math_string = "1+246x3"
math_input = "1 + 24.0 * 3 / 2 - 4 + 2 * 8"
# N.B. problems with division because it currently expects integers! (so 36.0 confuses it!)
debug = True
# math_array = []
# prev = ""
# i = -1
# print(math_string)
# mathArr2 = re.sub(r"(\d+|x|\+|\-|\*|\/)",r"\1 ",math_string).split()

def make_array(raw_string):
    math_string = raw_string.replace(" ","")
    if debug: print(f"Cleaned input: {math_string}")
    math_array = []
    prev = ""
    i = -1
    for count, char in enumerate(math_string):
        pos = ""
        # if char.isdigit():
        if char in "0123456789.":
            pos = "num"
        elif char in ("+-/*x"):
            pos = "op"
        else:
            print (f"Character position {count}: not a number or operator.")
            break
        if pos == prev:
            if pos == "num":
                math_array[i] += char
            else:
                print(f"Character pos {count}: only one operator at a time allowed.")
            # print(f"run = ...{char} at {i}")
        else:
            math_array.append(char)
            i += 1
            # print(f"this = {char} at {i}")
            prev = pos
    return math_array

# math_array = make_array(math_string)

# print(math_array)
# if not (len(math_array) % 3):
#     print("Wrong number of arguments.")
#     quit()


def f_p(arr,result_arr):
    if len(arr) <= 1:
        result_arr += arr
        if debug: print(f"end of array:\n{result_arr},\n{arr}\n")
        return result_arr
    left = float(arr[0])
    op = arr[1]

    if op in "+-":
        result_arr += [left,op]
        if debug: print(f"addition / subtraction:\n{result_arr[2:]},\n{arr}\n")
        # right = str(0 - int(arr[2:1]) ) if op == "-" else arr[2:1] 
        # rest = [right] + arr[3:]
        # return rest
        return f_p(arr[2:],result_arr)

    elif op in "*x/":
        right = left / float(arr[2]) if op == "/" else left * float(arr[2])
        recurse = [str(right)] + arr[3:]
        if debug: print(f"division / multiplication:\n{result_arr}: ({left} {op} {int(arr[2])}) => {right}\n{recurse}\n")
        return f_p(recurse,result_arr)

print(f"Raw input: {math_input}")
math_array = make_array(math_input)
print(f"Primary processing: {math_array}")
print()
result_array = f_p(math_array,[])
print(result_array)

