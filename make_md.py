#!/usr/bin/python

import sys
import re

count_whitespace = re.compile("\s")



in_file = "test.md"
out_file = "md.html"
out_text = ""
EOL = "\n"
title = "pauly test"

html_head = f"""
<html>
<head>
<title>{title}</title>
</head>
<body>
"""

html_tail = """
</body>
"""

try:
    out_file = sys.argv[1]
except:
    print(f"defaulting to '{out_file}'")



def unorderedList(bullet, indent, context):
    # para_tags = f"list{line[0]}"
    # para_tags = ("<li>","</li>")
    if context == "open":
        para_tags = ("<ul>"+ EOL + "<li>","</li>")
    elif context == "inside":
        para_tags = ("<li>","</li>")
    return para_tags

def orderedList(indent, context):
    # para_tags = "olist"
    # para_tags = ("<li>", "</li>")
    if context == "open":
        para_tags = ("<ol>"+ EOL + "<li>","</li>")
    elif context == "inside":
        para_tags = ("<li>","</li>")
    return para_tags

def heading(line):
    count = re.compile("#+")
    depth = count.match(line).end()
    para_tags = (f"<h{depth}>", f"</h{depth}>")
    return para_tags

def blockquote(line):
    count = re.compile(">+")
    depth = count.match(line).end()
    para_tags = (depth * "<blockquote>", depth * "</blockquote>")
    return para_tags

def codeblock(instructions):
    if instructions == "open":
        para_tags = ("<pre><code>", "")
    elif instructions == "close":
        para_tags = ("", "</code></pre>")
    else: 
        para_tags = ("", "")
    return para_tags

def paragraph():
    para_tags = ("<p>","</p>")
    return para_tags

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
    initial_digit = re.compile(r'\d+\.')
    initial_gt = re.compile(r'>+')
    initial_hash = re.compile(r'#+')
    open_tags = []
    line_type = ""

    with open(in_file, 'r') as f:
        for index, line in enumerate(f):
            line = line.rstrip()
            indent = len(re.findall(count_whitespace, line))
            line = line.strip() ## Also removes the final newline  
            isBlank = True
            para_tags = ("","")

            if line:
                isBlank = False
                first_char = line[0]
                if "cb" in open_tags:
                    if line[0:3] == "```":
                        open_tags.remove("cb")
                        para_tags = codeblock("close")
                        line = line[3:]
                    else:
                        line_type = "cb"
                        para_tags = codeblock("inside")

                elif line[0:3] == "```":
                    line_type = "cb"
                    open_tags.append("cb")
                    para_tags = codeblock("open")
                    line = line[3:]

                elif first_char == "#":
                    line_type = "h"
                    para_tags = heading(line)
                    line = initial_hash.sub("",line,1)

                elif first_char == ">":
                    line_type = "bq"
                    para_tags = blockquote(line)
                    line = initial_gt.sub("",line,1)

                elif first_char in ("+", "-", "*"):
                    line_type = "ul"
                    if line_type in open_tags:
                        context = "inside"
                    else:
                        context = "open"
                        open_tags.append(line_type)
                    para_tags = unorderedList(first_char, indent, context)
                    line = line[1:].lstrip()

                elif initial_digit.match(line) is not None:
                    line_type = "ol"
                    if line_type in open_tags:
                        context = "inside"
                    else:
                        context = "open"
                        open_tags.append(line_type)
                    para_tags = orderedList(indent, context)
                    line = initial_digit.sub("",line,1)
                    
                else:
                    line_type = "p"
                    para_tags = paragraph()

            print(f"debug: {open_tags=}")

            if "ul" in open_tags and line_type != "ul":
                cleanup = "</ul>" + EOL
                open_tags.remove("ul")
            elif "ol" in open_tags and line_type != "ol":
                cleanup = "</ol>" + EOL
                open_tags.remove("ol")
            else: cleanup = ""

            if line:
                line = inline_tags(line)
            # else:
            #     line = "&nbsp;"

            # tag_open, tag_close = "<p>","</p>"
            tag_open, tag_close = para_tags
            line = tag_open + line + tag_close + EOL
            line = cleanup + line

            out_text += line
    
    with open(out_file, 'w') as f:
        f.write(html_head + out_text + html_tail)
