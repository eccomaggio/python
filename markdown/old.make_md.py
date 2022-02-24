#!/usr/bin/python

import sys
import os.path
import re




in_file = "test.md"
out_file = "md.html"
out_text = ""
EOL = "\n"
title = "pauly test"

html_head = f"""
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



# def unorderedList(bullet="", indent, context):
def listing(indent, context, bullet = "") :
    list_wrapper = "<ul>" if bullet else "<ol>"
    tag_open, tag_close = "<li>","</li>"
    if context == "open":
        tag_open = list_wrapper + EOL + tag_open
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

def inline_markup(line):
    line = line.replace("<","&lt;").replace(">", "&gt;").replace("&","&amp;")
    line = bold1.sub(r'<strong>\1</strong>', line)
    line = bold2.sub(r'<strong>\1</strong>', line)
    line = italic1.sub(r'<em>\1</em>', line)
    line = italic2.sub(r'<em>\1</em>', line)
    line = strikeout.sub(r'<s>\1</s>', line)
    line = inlineCode.sub(r'<code>\1</code>', line)
    line = links.sub(r'<a href="\2">\1</a>', line)
    line = anchor.sub(r'<span id="#\1">\1</span>', line)
    # line = to_anchor.sub(r'<a href="#\1">\1</a>', line)
    line = refs.sub(r'<img src="\2" alt="\1" />', line)
    line = emails.sub(r'<a href="mailto:\1">\1</a>', line)
    line = urls.sub(r'<a href="\1">\1</a>', line)
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
    bold1 = re.compile('\*\*(.+?)\*\*')
    bold2 = re.compile('__(.+?)__')
    italic1 = re.compile('_(.+?)_')
    italic2 = re.compile('\*(.+?)\*')
    strikeout = re.compile('~~(.*?)~~')
    inlineCode = re.compile('`(.*?)`')
    links = re.compile('[^!]\[(.*?)\]\s*\((.*?)\)')
    anchor = re.compile('\[\^(.*?)][^:]*')
    # to_anchor = re.compile('\[\^(.*?)]:\s*?')
    refs = re.compile('!\[(.*?)\]\((.*?)\)')
    emails = re.compile('&amp;lt;(.*?@.*?)&amp;gt;')
    # urls = re.compile('&amp;lt;(.*?\..*?)&amp;gt;')
    urls = re.compile('&amp;lt;(.*?[\.\#].*?)&amp;gt;')
    # emails = re.compile('<(.*?@.*?)>')
    # urls = re.compile('<(.*?\..*?)>')

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
            leading_sp = len(re.findall(r'\s', line))
            tmp = leading_sp - prev_lsp
            indent = 1 if tmp>0 else -1 if tmp<0 else 0
            prev_lsp = leading_sp

            line = line.strip() ## Also removes the final newline  
            isBlank = True
            para_tags = ("","")

            if line:
                isBlank = False
                # if "cb" in open_tags:
                if open_tags and open_tags[-1] == "code":
                    if line[0:3] == "```":
                        # open_tags.remove("cb")
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
                        # open_tags.remove(line_type)
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

                elif line[:2] in ("+ ", "- ", "* "):
                    line_type = "ul"
                    # if line_type in open_tags:
                    if open_tags and open_tags[-1] == line_type:
                        context = "inside"
                    else:
                        context = "open"
                        open_tags.append(line_type)
                    para_tags = listing(indent, context, line[0])
                    line = line[2:].lstrip()

                elif initial_digit.match(line) is not None:
                    line_type = "ol"
                    # if line_type in open_tags:
                    if open_tags and open_tags[-1] == line_type:
                        context = "inside"
                    else:
                        context = "open"
                        open_tags.append(line_type)
                    para_tags = listing(indent, context, "")
                    line = initial_digit.sub("",line,1)
                    
                else:
                    line_type = "p"
                    para_tags = paragraph()
                        
            # print(f"debug: {open_tags=}")

            # if "ul" in open_tags and line_type != "ul":

            ## Assumptions:
            ## lists could be embedded inside blockquotes & details
            ## no paragraph-tags can be embedded in a list
            # cleanup = ""
            # if open_tags:
            #     ot = open_tags[-1]
            #     if ot == "ul" or ot == "ol":
            #         ## if list embedded in another list
            #         if line_type == "ul" or line_type == "ol":
            #             if indent <= 0 and line_type != ot:
            #                 cleanup = "</ul>" if ot == "ul" else "</ol>"
            #                 open_tags.pop()
            #         ## only lists can be embedded inside lists
            #         else:
            #             # cleanup = "</ul>" if ot == "ul" else "</ol>"
            #             while open_tags and (open_tags[-1][1] == "l"):
            #                 cleanup = cleanup + "</" + open_tags[-1] + ">" 
            #                 open_tags.pop()

            #             open_tags.pop()
                        


            if open_tags:
                if open_tags[-1] == "ul" and line_type != "ul":
                    cleanup = "</ul>" + EOL
                    # open_tags.remove("ul")
                    open_tags.pop()
                # elif "ol" in open_tags and line_type != "ol":
                elif open_tags[-1] == "ol" and line_type != "ol":
                    cleanup = "</ol>" + EOL
                    # open_tags.remove("ol")
                    open_tags.pop()
            else: cleanup = ""

            if line:
                line = inline_markup(line)
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
