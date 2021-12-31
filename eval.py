import re
import json

# math_string = "1+246x3"
math_input = "1.5 + 24.0 x -3 / 2 - 40 + 2 * 8"
ALLOWED_OPS = "+-/*x"
op_lookup = {"+" : ["ADD",2], "-" : ["SUB",2], "*" : ["MUL",1], "/" : ["DIV",1]}
debug = True
debug1 = False

def tokenize(raw_string):
    """
    Parses character by character to create and validate an array of expressions
    """
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
            print (f"Error: Character at position {count} not a number or operator.")
            continue

        if el_type == prev and el_type != "BR":
            if el_type == "NUM":
                math_array[i] += char
                if debug1: print(f"{el_type} added: {char}")
            else:
                print(f"Error: Character el_type {count}: only one operator at a time allowed.")
        else:
            math_array.append(char)
            if debug1: print(f"{el_type} added: {char}")
            i += 1
        prev = el_type

    ## Clean up and validate math code   
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

"""
def OLD_f_p(arr,result_arr):
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
"""

def f_p(arr,result_arr):
    ## end of string = return condition (return final argument)
    if len(arr) <= 1:
        result_arr += arr
        if debug: print(f"end of array:\n{result_arr},\n{arr}\n")
        return result_arr
    left = arr[0]
    op = arr[1]

    if op in "+-":
        symbol = "ADD" if op == "+" else "SUB"
        result_arr += [symbol,left]
        if debug: print(f"addition / subtraction:\n{result_arr[2:]},\n{arr}\n")
        return f_p(arr[2:],result_arr)

    elif op in "*x/":
        ## process op & return as right hand argument of another op
        ## do this by removing the original right-hand argument
        symbol = "DIV" if op == "/" else "MUL"
        right = [symbol,left,arr[2]]
        # recurse = [str(right)] + arr[3:]
        recurse = [right] + arr[3:]
        if debug: print(f"division / multiplication:\n{result_arr}: ({left} {op} {int(arr[2])}) => {right}\n{recurse}\n")
        return f_p(recurse,result_arr)


# def parse(arr):
#     i = 0
#     arr1 = []
#     while arr:
#         if len(arr) == 1:
#             arr1 += arr[0]
#             break
#         left = arr[0]
#         op = arr[1]
#         print(f"{left=},{op=}\n\t{arr=}\n\t{arr1=}")
#         if op in "*x/":
#             symbol = "DIV" if op == "/" else "MUL"
#             right = [[symbol,left,arr[i + 2]]]
#             arr1 += right
#             # arr1 = arr1[:-1] + right
#             arr = right + arr[3:]
#         else:
#             arr1 += [left,op]
#             arr = arr[2:]
#     return arr1
        

def parse(arr):
    i = 0
    math_dict = {}
    for id,el in enumerate(arr):
        if isinstance(el,float):
            math_dict[id] = {"type": "ARG", "value": el}
        elif el in "()":
            math_dict[id] = {"type": "BR"}
        else:
            math_dict[id] = {
                    "type": "OP", 
                    "op":   op_lookup[el][0],
                    "precedence": op_lookup[el][1],
                    "argIDs": [None, None]}
            if id == 1:
                math_dict[id]["argIDs"] = [0,None]
            elif id == len(arr) - 2:
                math_dict[id]["argIDs"] = [None,0]
    return math_dict



def pass_1(math_dict):
    for precedence in range(1,3):
        for op in [el for el in math_dict 
                if math_dict[el]["type"] == "OP" and
                math_dict[el]["precedence"] == precedence
                ]:
            # print(math_dict[op],op)
            curr_op = math_dict[op]
            arg1 = math_dict[op - 1]
            arg2 = math_dict[op + 1]
            prev_op = math_dict.get[op - 1] 
            next_op = math_dict.get[op + 1]

            if prev_op:
                if curr_op["precedence"] > prev_opp["precedence"]:
                    curr_op["argIDs"][0] = arg1["value"]
                    prev_op["argIDs"][1] = op - 1
                elif curr_op["precedence"] == prev_op["precedence"]:  
                    curr_op["argIDs"][0] = op - 1
                else:
                    pass #add in the rest of the logic here 

        

math_array = tokenize(math_input)
if debug: print(f"Math array: {math_array}\n")
math_dict = parse(math_array)

# tmp = f_p(math_array,[])
# tmp = parse(math_array)
# for i in math_dict:
#     print(f"id={i}: {tmp[i]}")
result = pass_1(math_dict)
quit()

result_array = final_pass(math_array)
if debug: print(f"Raw input: {math_input}")
print(result_array)

