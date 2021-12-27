import re

# math_string = "1+246x3"
math_input = "-1.5 + -24.0 x 3 / 2 - 40 + 2 * 8"
ALLOWED_OPS = "+-/*x"
debug = True

def make_array(raw_string):
    math_string = raw_string.replace(" ","")
    if debug: print(f"Cleaned input: {math_string}")
    math_array = []
    prev = ""
    i = -1
    for count, char in enumerate(math_string):
        el_type = ""
        if char in "0123456789.":
            el_type = "NUM"
        elif char in ALLOWED_OPS:
            el_type = "OP"
            ## Allow negative numbers
            if char == "-" and (prev == "" or math_array[-1] in ALLOWED_OPS):
                el_type = "NUM"
        elif char in "()":
            el_type = "BR"
        else:
            print (f"Character at position {count} not a number or operator.")
            continue

        if el_type == prev and el_type != "BR":
            if el_type == "NUM":
                math_array[i] += char
                if debug: print(f"{el_type} added: {char}")
            else:
                print(f"Character el_type {count}: only one operator at a time allowed.")
        else:
            math_array.append(char)
            if debug: print(f"{el_type} added: {char}")
            i += 1
        prev = el_type

    if debug: print(f"first pass:\n{math_array}")
    for i, el in enumerate(math_array):
        if el in ALLOWED_OPS:
            if el == "x":
                math_array[i] = "*"
        elif el in "()":
            continue
        else:
            math_array[i] = float(el)

    i = 0
    while i < len(math_array) - 1:
        num = math_array[i]
        if isinstance(num,str) and num in "()":
            i += 1 
            continue
        i += 1
        while math_array[i] in "()":
            i += 1
        op = math_array[i]
        assert isinstance(num,float), f"Problem here: {math_array[:i]}^"
        assert isinstance(op,str), f"Problem here: {math_array[:i]}^"
        i += 1

    assert isinstance(math_array[-1],float), f"End with a number: {math_array}"

    return math_array

def final_pass(arr):
    ## Strip out brackets for now
    basic_array = [el for el in arr if isinstance(el,float) or 
            (isinstance(el,str) and el not in "()")]
    if debug: print(f"basic array:\n{basic_array}")
    for i,el in enumerate(basic_array):
        if isinstance(el,str) and el == "-":
           basic_array[i] = "+"
           basic_array[i + 1] = 0 - basic_array[i + 1]
    
    final_result = [el for el in f_p(basic_array,[]) if isinstance(el,float)]
    return sum(final_result)
    # return f_p(basic_array,[])

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
        return f_p(arr[2:],result_arr)

    elif op in "*x/":
        right = left / float(arr[2]) if op == "/" else left * float(arr[2])
        # recurse = [str(right)] + arr[3:]
        recurse = [right] + arr[3:]
        if debug: print(f"division / multiplication:\n{result_arr}: ({left} {op} {int(arr[2])}) => {right}\n{recurse}\n")
        return f_p(recurse,result_arr)

math_array = make_array(math_input)
if debug: print(f"Primary processing: {math_array}\n")
result_array = final_pass(math_array)
if debug: print(f"Raw input: {math_input}")
print(result_array)

