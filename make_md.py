#!/usr/bin/python

import sys
import re

count_whitespace = re.compile("\s")



in_file = "test.md"
out_file = "md.html"
out_text = ""
EOL = "\n"

try:
    out_file = sys.argv[1]
except:
    print(f"defaulting to '{out_file}'")



def checkList(line):
    para_type = f"list{line[0]}"
    return para_type

def checkOList(line):
    para_type = "olist"
    return para_type

def checkHeading(line):
    count = re.compile("#+")
    depth = count.match(line).end()
    para_type = f"h{depth}"
    return para_type

def checkBlockquote(line):
    para_type = "bquo"
    count = re.compile(">+")
    depth = count.match(line).end()
    return para_type

def checkCode(line,to_close):
    para_type = "code"
    return para_type

def checkPara(line):
    para_type = "para"
    return para_type


if __name__ == "__main__":
    print(f"{out_file}")
    is_codeblock = False

    with open(in_file, 'r') as f:
        for index, line in enumerate(f):
            line = line.rstrip()
            indent = len(re.findall(count_whitespace, line))
            line = line.strip() ## Also removes the final newline  
            isBlank = True
            para_type = ""

            if line:
                isBlank = False
                first_char = line[0]
                if is_codeblock:
                    if line[0:3] == "```":
                        is_codeblock = False
                        para_type = checkCode(line, False)
                    else:
                        para_type = checkCode(line, True)
                elif line[0:3] == "```":
                    is_codeblock = True
                    para_type = checkCode(line, True)
                elif first_char in ("+", "-", "*"):
                    para_type = checkList(line)
                elif first_char == "#":
                    para_type = checkHeading(line)
                elif first_char == ">":
                    para_type = checkBlockquote(line)
                elif first_char.isnumeric():
                    para_type = checkOList(line)
                else:
                    para_type = checkPara(line)
                print(f"{para_type}: [{line[0]}]\t->{line}")

            else:
                line = "&nbsp;"

            tag_open, tag_close = "<p>","</p>"
            line = tag_open + line + tag_close + EOL

            out_text += line
    
    with open(out_file, 'w') as f:
        f.write(out_text)
