#!/usr/bin/python

import sys
import os.path
import re
from collections import OrderedDict




in_file = "test.md"
out_file = "md.html"
out_text = ""
EOL = "\n"
title = "pauly test"

html_head = f"""
<!DOCTYPE html>
<html>
<head>
<title>{title}</title>
<!--<link rel="stylesheet" href="./md.css">-->
<link rel="stylesheet" href="./splendor.css">
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



# def listing(indent, context, bullet = "") :
#     list_wrapper = "<ul>" if bullet else "<ol>"
#     tag_open, tag_close = "<li>","</li>"
#     if context == "open":
#         tag_open = list_wrapper + EOL + tag_open
#     return (tag_open,tag_close)

def listing(context,prev, bullet = "") :
    list_wrapper = "<ul>" if bullet else "<ol>"
    prev = f'</{prev}>' if prev else ""
    tag_open, tag_close = "<li>","</li>"
    # print(f"{context=}")
    if context == "open_new":
        tag_open = list_wrapper + EOL + tag_open
    elif context == "close_prev":
        tag_open = prev + EOL + tag_open
    elif context == "close_prev_open_new":
        tag_open = prev + EOL + list_wrapper + EOL + tag_open
    return (tag_open,tag_close)

def heading(line):
    count = re.compile("#+")
    depth = count.match(line).end()
    para_tags = (f"<h{depth}>", f"</h{depth}>")
    return para_tags

def blockquote(line):
    count = re.compile(">+")
    depth = count.match(line).end()
    para_tags = (depth * "<blockquote><p>", depth * "</p></blockquote>")
    return para_tags

def codeblock(context):
    if context == "open":
        para_tags = ("<pre><code>", "")
    elif context == "close":
        para_tags = ("", "</code></pre>")
    else: 
        para_tags = ("", "")
    return para_tags

def details(context, displayDetails):
    if context == "open":
        tag = "<details open>" if displayDetails else "<details>"
        tag += "<summary>"
        para_tags = (tag,"</summary>")
    else:
        para_tags = ("","</details>")
    return para_tags

def horizontalRule():
    return ("<hr>", "")

def paragraph():
    para_tags = ("<p>","</p>")
    return para_tags

def inline_markup(r,line):
    line = line.replace("<","&lt;").replace(">", "&gt;").replace("&","&amp;")
    for i in r:
        line = r[i][0].sub(r[i][1],line)
    return line

def subCode(line):
    inside = p.findall(line)
    ## Abort if no codeblocks found
    if not inside:
        return line

    ## extract the <code> sections and remove the automatic escaping
    ## reintegrate into the regular markdown text
    outside = p1.findall(line)
    final = p2.findall(line)
    for i, match in enumerate(inside):
        tmp = match
        tmp = tmp.replace('&amp;lt;','<').replace('&amp;gt;','>').replace('&amp;','&')
        inside[i] = tmp
    out = ""
    for i,code in enumerate(outside):
        out += f"{code[0]}{inside[i]}{code[1]}"
    out += f"{''.join(final)}"
    return out


if __name__ == "__main__":
# def make_md(in_file, out_file):
    try:
        file_name = sys.argv[1]
    except:
        print("No filename specificed; I'll look for test.md")
        file_name = "test.md"
    # in_file = Path(file_name)
    # if not in_file.is_file():
    if not os.path.isfile(file_name): 
        print("Sorry. No markdown file found.")
        quit()
    else:
        in_file = file_name
        try:
            tmp = in_file[:in_file.rindex(".")]
        except:
            tmp = in_file
        out_file = tmp + ".html"

    print(f"Using the markdown in {in_file} to output html as {out_file}")

    ## regex to add inline styling
    r = OrderedDict()
    r['bold1'] = (re.compile('\*\*(.+?)\*\*'), r'<strong>\1</strong>') 
    r['bold2'] = (re.compile('__(.+?)__'), r'<strong>\1</strong>') 
    r['italic1'] = (re.compile('_(.+?)_'), r'<em>\1</em>') 
    r['italic2'] = (re.compile('\*(.+?)\*'), r'<em>\1</em>') 
    r['strikeout'] = (re.compile('~~(.*?)~~'), r'<s>\1</s>') 
    r['inlineCode'] = (re.compile('`(.*?)`'), r'<code>\1</code>') 
    r['links'] = (re.compile('[^!]\[(.*?)\]\s*\((.*?)\)'), r'<a href="\2">\1</a>') 
    r['anchor'] = (re.compile('\[\^(.*?)]'), r'<span id="#\1">\1</span>') 
    r['refs'] = (re.compile('!\[(.*?)\]\((.*?)\)'), r'<img src="\2" alt="\1" />') 
    r['emails'] = (re.compile('&amp;lt;(.*?@.*?)&amp;gt;'), r'<a href="mailto:\1">\1</a>') 
    r['urls'] = (re.compile('&amp;lt;(.*?[\.\#].*?)&amp;gt;'), r'<a href="\1">\1</a>') 

    ## regex to remove escaping inside <code> tags
    p = re.compile(r'(?:<code>)(.*?)(?:</code>)')
    p1 = re.compile(r'(.*?<code>).*?(</code>.*?)')
    p2 = re.compile(r'.*</code>(.*?)$')

    initial_digit = re.compile(r'\d+\.\s')
    initial_gt = re.compile(r'>+\s')
    initial_hash = re.compile(r'#+\s')
    open_tags = []
    line_type = ""
    prev_lsp = 0

    with open(in_file, 'r') as f:
        for index, line in enumerate(f):
            line = line.rstrip()

            ## calculate indent relative to prev (i.e -1, 0 or 1)
            tmp = re.match(r'\s*', line)
            leading_sp = len(tmp.group()) if tmp else 0
            tmp = leading_sp - prev_lsp
            indent = 1 if tmp>0 else -1 if tmp<0 else 0
            prev_lsp = leading_sp

            line = line.strip() ## Also removes the final newline  
            line_type = "blank"
            para_tags = ("","")

            if line:
                if open_tags and open_tags[-1] == "code":
                    if line[0:3] == "```":
                        open_tags.pop()
                        para_tags = codeblock("close")
                        line = line[3:]
                    else:
                        line_type = "code"
                        para_tags = codeblock("inside")

                elif line[0:3] == "```":
                    line_type = "code"
                    open_tags.append(line_type)
                    para_tags = codeblock("open")
                    line = line[3:]

                elif line[0:3] == "@@@" or line[0:3] == "@+@":
                    line_type = "details"
                    if line_type in open_tags:
                        open_tags.pop()
                        para_tags = details("close",False)
                    else:
                        displayOpen = line.find("+") == 1
                        open_tags.append(line_type)
                        para_tags = details("open",displayOpen)
                    line = line[3:]

                elif line[:3] == "***" or line[:3] == "---" or line[:3] == "___":
                    line_type = "hr"
                    para_tags = horizontalRule()
                    line = ""

                elif line[0] == "#":
                    line_type = "h"
                    para_tags = heading(line)
                    line = initial_hash.sub("",line,1)

                elif line[0] == ">":
                    line_type = "blockquote"
                    para_tags = blockquote(line)
                    line = initial_gt.sub("",line,1)

                elif line[:2] in ("+ ", "- ", "* ") or initial_digit.match(line) is not None:
                    line_type = "ol" if line[0].isdigit() else "ul"
                    prev = ""
                    # open_tag = open_tags[-1] if open_tags else ""
                    is_list = (open_tags[-1][1:3] == "l") if open_tags else False
                    # is_list = (open_tag[1:3] == "l") if open_tags else False
                    is_ul = (open_tags[-1] == line_type) if is_list else False
                    if is_list:
                        if indent == 0:
                            if is_ul:
                                context = "inside"
                            else:
                                context = "close_prev_open_new"
                                prev = open_tags.pop() if open_tags else ""
                                open_tags.append(line_type)
                        ## any type, revert to higher level so close prev
                        elif indent == -1:
                            context = "close_prev"
                            prev = open_tags.pop()
                        ## any type, adding a new level
                        elif indent == 1:
                            context = "open_new"
                            open_tags.append(line_type)
                    else:
                        context = "open_new"
                        open_tags.append(line_type)

                    bullet = "" if line_type == "ol" else line[0]
                    para_tags = listing(context,prev,bullet)
                    # print(f"\tl.{index + 1}>>{line_type}>>{para_tags}")
                    if line_type == "ul":
                        line = line[2:].lstrip()
                    else:
                        line = initial_digit.sub("",line,1)

                else:
                    line_type = "p"
                    para_tags = paragraph()
                        
            print(f"l.{index + 1:3}: {line_type:12} {indent:2} {open_tags}")

            if open_tags:
                if open_tags[-1] == "ul" and line_type != "ul":
                    cleanup = "</ul>" + EOL
                    open_tags.pop()
                elif open_tags[-1] == "ol" and line_type != "ol":
                    cleanup = "</ol>" + EOL
                    open_tags.pop()
            else: cleanup = ""

            if line:
                line = inline_markup(r,line)
                if line_type != "cb":
                    line = subCode(line)

            tag_open, tag_close = para_tags
            line = tag_open + line + tag_close + EOL
            line = cleanup + line

            out_text += line
    
    with open(out_file, 'w') as f:
        f.write(html_head + out_text + html_tail)


# if __name__ == "__main__":
#     make_md(in_file,out_file)
