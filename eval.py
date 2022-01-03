import re
import json
from collections import OrderedDict
from dataclasses import dataclass,field
from typing import List

@dataclass(order=True)
class Arg:
    """
    For float arguments
    """
    id: int = field(compare = False)
    value: float
    # value_id: int = field(compare = False, default = None)

@dataclass(order=True)
class Op:
    """
    For operators (+/-*)
    Comparison is based on precedence
    Update __post_init__ if more ops allowed
    """
    id: int = field(compare = False)
    symbol: str = field(compare = False)
    arg_ids: List[int] = field(compare = False,default_factory=list)
    op: int = field(compare = False,default=None)
    precedence: int = field(default=None)
    
    def __post_init__(self):
        self.arg_ids = [None, None]
        if not self.precedence:
            self.precedence = {"+": 1,"-":1,"*":2, "/":2}[self.symbol]
        if not self.op:
            self.op = {"+": "add","-":"sub","*":"mul", "x":
                    "mul","/":"div"}[self.symbol]

@dataclass(order=True)
class Bracket:
    """
    For brackets
    Comparison according to id (i.e. it is used to pair right/left braces)
    """
    id: int = field(compare = False)
    paired_with: int = field(default=None)
    is_opening: bool = field(compare = False, default=None)
    kind: int = field(compare = False, default=None)
    precedence: int = field(compare = False, default=10)
    nest_level: int = field(compare = False, default=None)



# math_string = "1+246x3"
math_input = "1.5 + 24.0 x -3 / 2 - 40 + 2 * 8"
ALLOWED_OPS = "+-/*x"
# op_lookup = {"+" : ["ADD",2], "-" : ["SUB",2], "*" : ["MUL",1], "/" : ["DIV",1]}
debug = True
debug1 = True

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

    # i = 0
    # while i < len(math_array) - 1:
    #     num = math_array[i]
    #     if isinstance(num,str) and num in "()":
    #         i += 1 
    #         continue
    #     i += 1
    #     while math_array[i] in "()":
    #         i += 1
    #     op = math_array[i]
    #     assert isinstance(num,float), f"Problem here: {math_array[:i]}^"
    #     assert isinstance(op,str), f"Problem here: {math_array[:i]}^"
    #     i += 1

    # assert isinstance(math_array[-1],float), f"End with a number: {math_array}"

    return math_array


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
"""

def parse(arr):
    # firstArg, lastArg, firstOp, lastOp = None, None, None, None
    math_dict = OrderedDict({})
    for id,el in enumerate(arr):
        ## ARG
        if isinstance(el,float):
            math_dict[id] = Arg(id,el)
        ## BRACKET
        elif el in "()":
            math_dict[id] = Bracket(id,is_opening = (el == "("))
        ## OP
        else:
            math_dict[id] = Op(id,el)

    return math_dict



def resolve(math_dict):
    ## Validate the expression first by listing elements excluding brackets
    id_list = [id for id in math_dict if not isinstance(math_dict[id], Bracket)]
    expr_pattern = "".join([type(math_dict[id]).__name__[0] for id in
        id_list])
    expected_pattern = ("AO" * (len(id_list) // 2)) + "A"
    if debug1:
        print(f"\n\n{expected_pattern} {expr_pattern}\n")
    assert expected_pattern == expr_pattern,"ERROR: expression should be <arg1 op arg2...>" 
    ## Fill in implied arguments
    first_op = math_dict[id_list[1]]
    last_op = math_dict[id_list[-2]]
    first_arg = math_dict[id_list[0]]
    last_arg = math_dict[id_list[-1]]
    first_op.arg_ids[0] = first_arg.id
    last_op.arg_ids[1] = last_arg.id
    for precedence in [2,3]:
        if debug: print(f"\nresolving, precedence {precedence}")
        for id in math_dict:
            curr_op = math_dict[id]
            ## Only need to parse OPs
            if isinstance(curr_op,Op) and curr_op.precedence == precedence:
                curr_pos = id_list.index(id)
                arg1 = math_dict[id_list[curr_pos - 1]]
                arg2 = math_dict[id_list[curr_pos + 1]]
                ## Use .get to avoid exceptions (None means 'out of range')
                prev = curr_pos - 2
                next = curr_pos + 2
                prev_op = math_dict.get(id_list[prev]) if prev >= 0 else None
                next_op = math_dict.get(id_list[next]) if next < len(math_dict) else None
                if debug: print(f"\tresolving op: {id}\n\t{arg1=}\n\t{arg2=}\n\t{prev_op=}\n\t{next_op=}")

                if prev_op:
                    if curr_op > prev_op:
                        curr_op.arg_ids[0] = arg1.id
                        prev_op.arg_ids[1] = id
                    elif curr_op <= prev_op:  
                        curr_op.arg_ids[0] = prev_op.id
                if next_op:
                    if curr_op > next_op:
                        curr_op.arg_ids[1] = arg2.id
                        next_op.arg_ids[0] = id
                    elif curr_op == next_op:
                        curr_op.arg_ids[1] = arg1.id
                        next_op.arg_ids[0] = id
                    else:
                        curr_op.arg_ids[1] = next_op.id
    return math_dict

        

math_array = tokenize(math_input)
if debug: print(f"Math array: {math_array}\n")
math_dict = parse(math_array)
for i in math_dict:
    print(f"id>> {i}: {math_dict[i]}")
parsed_dict = resolve(math_dict)
print(parsed_dict)
print()
for i in parsed_dict:
    print(f"id={i}: {parsed_dict[i]}")
print(parsed_dict[11].arg_ids)
quit()

result_array = final_pass(math_array)
if debug: print(f"Raw input: {math_input}")
print(result_array)

