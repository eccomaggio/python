#!/usr/bin/python

import sys
import re

count_whitespace = re.compile("\s")



in_file = "test.md"
out_file = "md.html"
out_text = ""
EOL = "\n"
stack = None
is_codeblock = False

try:
    out_file = sys.argv[1]
except:
    print(f"defaulting to '{out_file}'")



def checkList(line):
    print(f"{line[0]}: list, type={line[0]}: >>{line}")

def checkOList(line):
    print(f"{line[0]}: ordered list: >>{line}")

def checkHeading(line):
    count = re.compile("#+")
    depth = count.match(line).end()
    print(f"{line[0]}: heading level {depth}: >>{line}")

def checkBlockquote(line):
    count = re.compile(">+")
    depth = count.match(line).end()
    print(f"{line[0]}: blockquote level {depth}: >>{line}")

def checkCode(line):
    print(f"{line[0]}: code: >>{line}")

def checkPara(line):
    print(f"para: >>{line}")


if __name__ == "__main__":
    print(f"{out_file}")

    with open(in_file, 'r') as f:
        for index, line in enumerate(f):
            line = line.rstrip()
            indent = len(re.findall(count_whitespace, line))
            line = line.strip() ## Also removes the final newline  
            isBlank = True
            line_type = ()
            if line:
                isBlank = False
                # print(f">>>> {line}, [{line[0]}]")
                # match line[1]:
                #     case ("+" | "-" | "*"): line_type = ("list", line[1])
                #     case "#": line_type = checkHeading(line)
                #     case ">": line_type = checkBlockquote(line)
                #     case "`": line_type = checkCode(line)
                #     # case _: line_type = ("para") 
                #     case _: line_type = checkPara(line)
                first_char = line[0]
                if is_codeblock:
                    if line[0:3] == "```":
                        is_codeblock == False
                        print("..........codeblock ended")
                    checkCode(line)
                elif line[0:3] == "```":
                    is_codeblock == True
                    print("..........in a codeblock...")
                    checkCode(line)
                elif first_char in ("+", "-", "*"):
                    checkList(line)
                elif first_char == "#":
                    checkHeading(line)
                elif first_char == ">":
                    checkBlockquote(line)
                elif first_char.isnumeric():
                    checkOList(line)
                else:
                    checkPara(line)
            else:
                line = "&nbsp;"

            tag_open, tag_close = "<p>","</p>"
            line = tag_open + line + tag_close + EOL

            out_text += line
    
    with open(out_file, 'w') as f:
        f.write(out_text)
