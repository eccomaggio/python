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



def unorderedList(line,indent):
    para_type = f"list{line[0]}"
    return para_type

def orderedList(line,indent):
    para_type = "olist"
    return para_type

def heading(line):
    count = re.compile("#+")
    depth = count.match(line).end()
    para_type = f"h{depth}"
    return para_type

def blockquote(line):
    para_type = "bquo"
    count = re.compile(">+")
    depth = count.match(line).end()
    return para_type

def codeblock(line,to_close):
    para_type = "code"
    return para_type

def paragraph(line, indent):
    para_type = "para"
    return para_type

def inline_tags(line):
    bold1 = re.compile('\*\*(.+?)\*\*')
    bold2 = re.compile('__(.+?)__')
    italic1 = re.compile('_(.+?)_')
    italic2 = re.compile('\*(.+?)\*')
    strikeout = re.compile('~~(.*?)~~')
    links = re.compile('[^!]\[(.*?)\]\s*\((.*?)\)')
    refs = re.compile('!\[(.*?)\]\((.*?)\)')

    line = line.replace("<","&lt;").replace(">", "&gt;").replace("&","&amp;")
    line = bold1.sub(r'<b>\1</b>', line)
    line = bold2.sub(r'<b>\1</b>', line)
    line = italic1.sub(r'<i>\1</i>', line)
    line = italic2.sub(r'<i>\1</i>', line)
    line = strikeout.sub(r'<s>\1</s>', line)
    line = links.sub(r'<a href="\2">\1</a>', line)
    line = refs.sub(r'<img src="\2" alt="\1" />', line)
    return line


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
            initial_digit = re.compile(r'\d+\.')
            initial_gt = re.compile(r'>+')
            initial_hash = re.compile(r'#+')

            if line:
                isBlank = False
                first_char = line[0]
                if is_codeblock:
                    if line[0:3] == "```":
                        is_codeblock = False
                        para_type = codeblock(line, False)
                        line = line[3:]
                    else:
                        para_type = codeblock(line, True)
                elif line[0:3] == "```":
                    is_codeblock = True
                    para_type = codeblock(line, True)
                    line = line[3:]
                elif first_char in ("+", "-", "*"):
                    para_type = unorderedList(line, indent)
                    line = line[1:].lstrip()
                elif first_char == "#":
                    para_type = heading(line)
                    line = initial_hash.sub("",line,1)
                elif first_char == ">":
                    para_type = blockquote(line)
                    line = initial_gt.sub("",line,1)
                # elif first_char.isnumeric():
                elif initial_digit.match(line) is not None:
                    para_type = orderedList(line, indent)
                    line = initial_digit.sub("",line,1)
                else:
                    para_type = paragraph(line, indent)
                try:
                    print(f"{para_type}: [{line[0]}]\t->{line}")
                except:
                    print(f"oops: {line}")

            else:
                line = "&nbsp;"

            line = inline_tags(line)

            tag_open, tag_close = "<p>","</p>"
            line = tag_open + line + tag_close + EOL

            out_text += line
    
    with open(out_file, 'w') as f:
        f.write(out_text)
