# !/usr/bin/python

"""
Meant to parse markdown but is very limited. Needs re-writing to allow
for embedding.

'lazy indenting' doesn't work 
code blocks must be delimited with three backticks on a sep line
I added in super limited support for details>summary:
    >-

Final notes to self:
    start again!
    look for patterns
    blanks should be evaluated along with following line
    indents are significant (2-4 spaces = indent) i some situations

    Build a skeleton version that just outputs e.g.
    para:	blah…
    h2:		blah
    ol-li		blah
    li		blah (i.e directly after trigger, with/without indent)
    -p		blah (i.e. indented p after blank)

    matches should be made in a function
    that way, it can be reapplied for embedding

"""

import sys
import os.path
import re
from collections import OrderedDict




in_file = "test.md"
out_file = "md.html"
out_text = ""
EOL = "\n"
# title = "pauly test"
# tmp = in_file.rfind(".")
# title = in_file[:tmp] if tmp >= 0 else "from markdown file"

headings = []
id_count = 0


try:
    out_file = sys.argv[1]
except:
    print(f"defaulting to '{out_file}'")



def is_embedded(taglist,the_list, result=[], count=0):
    '''Returns list of all matching tags + their pos: [[<tag>,pos],...]'''
    # print(f"<debug> {count}: {the_list}")
    if count == 0:
        result.clear()
    if not isinstance(taglist, list):
        taglist = [taglist]
    if the_list:
        pos = 0
        for i, tag in enumerate(the_list[::-1]):
            for target in taglist:
                if target == tag:
                    pos = (len(the_list) - i) - 1
                    result.insert(0,[tag,pos])
                    break
        is_embedded(taglist,the_list[:pos],result,count + 1)
    return result

def inline_markup(r,line):
    line = " " + line.replace("<","&lt;").replace(">", "&gt;").replace("&","&amp;")
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
        # tmp = tmp.replace('&amp;lt;','<').replace('&amp;gt;','>').replace('&amp;','&')
        tmp = tmp.replace('&amp;','&')
        inside[i] = tmp
    out = ""
    for i,code in enumerate(outside):
        out += f"{code[0]}{inside[i]}{code[1]}"
    out += f"{''.join(final)}"
    return out

def pre_parse(line):
    global id_count
    line_type = subtype = ""


    is_indented = bool(re.match(r' {2}|\t',line))
    line = line.lstrip()

    ## codeblocks
    if line[0:3] == "```":
        line_type = "codeblock"
        line = line[3:]

    ## SINGLE-LINE ELEMENTS

    ## horizontal rule
    elif line[:3] == "***" or line[:3] == "---" or line[:3] == "___":
        line_type = "hr"
        line = ""

    ## headings
    elif line[0] == "#":
        level = h_depth.match(line).end()
        line_type = f"h{level}"
        id_count += 1
        subtype = f"h_{id_count}"
        headings.append((f'h_{id_count}',line))
        line = initial_hash.sub("",line,1)

    ## MULTI-LINE

    ## details/summary (new)
    elif line[:2] == ">+" or line[:2] == ">-":
        line_type = "details"
        status = "show" if line[1] == "+" else "hide"
        id_count += 1
        subtype = f"open:{status}:s_{id_count}"
        line = line[3:]
    
    ## blockquotes
    elif line[0] == ">":
        line_type = "blockquote"
        line = line[1:].lstrip()
        ## NEED TO ADD IN RECURSION HERE?

    ## lists (li): bullets (ul) & ol
    elif line[:2] in ("+ ", "- ", "* "):
        line_type = "ul"
        line = line[1:].lstrip()

    elif initial_digit.match(line):
        line_type = "ol"
        line = initial_digit.sub("",line,1)

    ## paragraph p
    else:
        line_type = "??"
    
    return (line,line_type,[subtype,is_indented])







if __name__ == "__main__":
# def make_md(in_file, out_file):
    try:
        file_name = sys.argv[1]
    except:
        print("No filename specificed; I'll look for test.md")
        file_name = "test.md"
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
        
        tmp = in_file.rfind(".")
        title = in_file[:tmp] if tmp >= 0 else "from markdown file"

    print(f"Using the markdown in {in_file} to output html as {out_file}")

    html_head = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, minimal-ui">
<title>{title}</title>
<meta name="color-scheme" content="light dark">
<!-- <link rel="stylesheet" href="./splendor.css">-->
<link rel="stylesheet" href="./github-markdown-css/github-markdown.css">
<style>
			body {{
				box-sizing: border-box;
				min-width: 200px;
				max-width: 980px;
				margin: 0 auto;
				padding: 45px;
            }}

			@media (prefers-color-scheme: dark) {{
				body {{
					background-color: rgb(13,17,23);
                }}
            }}
		</style>
</head>
<body>
<article class="markdown-body">
"""


    html_tail ="""
</article>
</body>
"""
    ## regex to add inline styling
    r = OrderedDict()
    r['bold1'] = (re.compile('\*\*(.+?)\*\*'), r'<strong>\1</strong>') 
    r['bold2'] = (re.compile('__(.+?)__'), r'<strong>\1</strong>') 
    r['italic1'] = (re.compile('_(.+?)_'), r'<em>\1</em>') 
    r['italic2'] = (re.compile('\*(.+?)\*'), r'<em>\1</em>') 
    r['strikeout'] = (re.compile('~~(.+?)~~'), r'<s>\1</s>') 
    r['inlineCode_dbl'] = (re.compile('``(.+?)``'), r'<code>\1</code>') 
    r['inlineCode'] = (re.compile('`(.+?)`'), r'<code>\1</code>') 
    # r['links'] = (re.compile('[^!]\[(.*?)\]\s*\((.*?)\)'), r'<a href="\2">\1</a>') 
    r['link'] = (re.compile('[^!]\[(.*?)\]\((.+?)\)'), r'<a href="\2">\1</a>') 
    r['img'] = (re.compile('!\[(.*?)\]\((.+?)\)'), r'<img src="\2" alt="\1" />') 
    r['anchor'] = (re.compile('\[\^(.+?)]'), r'<span id="#\1">\1</span>') 
    r['email'] = (re.compile('&amp;lt;(.*?@.*?)&amp;gt;'), r'<a href="mailto:\1">\1</a>') 
    r['urls'] = (re.compile('&amp;lt;(.*?[\.\#].*?)&amp;gt;'), r'<a href="\1">\1</a>') 
    r['nbsp'] = (re.compile('\s\s\s*$'),r'&nbsp;')

    ## regex to remove escaping inside <code> tags
    p = re.compile(r'(?:<code>)(.*?)(?:</code>)')
    p1 = re.compile(r'(.*?<code>).*?(</code>.*?)')
    p2 = re.compile(r'.*</code>(.*?)$')

    initial_digit = re.compile(r'\d+\.\s')
    # initial_gt = re.compile(r'>+\s')  ## this misses blank-line >
    initial_gt = re.compile(r'>\s?')
    initial_hash = re.compile(r'#+\s')
    h_depth = re.compile("#+")
    context = []
    line_type = ""
    prev_lsp = 0
    pre_line = ""
    post_line =""
    output = ""
    was_blank = False

    with open(in_file, 'r') as f:
        for index, raw in enumerate(f):
            # if index < 172: continue
            # if index >= 230: break          ## parse up to codeblocks
            line = raw = raw.rstrip()
            if line:
                ## calculate indent relative to prev (i.e -1, 0 or 1)
                # tmp = re.match(r'\s*', line)
                # leading_sp = len(tmp.group()) if tmp else 0
                # tmp = leading_sp - prev_lsp
                # indent = 1 if tmp>0 else -1 if tmp<0 else 0
                # prev_lsp = leading_sp

                # ## md spec: 4 indents/1 tab delimited by blank = codeblock
                # code_indents = len(re.findall(r'\s{4}|\t',line))

                # line = line.lstrip()

                pre_line = ""
                post_line = ""
                line, line_type, subtype = pre_parse(line)
                subtype.append(was_blank)

                was_blank = False
            else:
                was_blank = True
                continue

            ## put this rule after other paragraph rules as they overlap
            indent = subtype[1]
            blank = subtype[2]
            
            if indent and blank and line_type == "??":
                line_type = "code"


            
            tmp = f"{line_type}-{subtype[0]} [{indent} {blank}]"
            print(f'l.{index:4} {tmp:20} | "{raw[:50]}"')

            prev_indent = indent

            
                # ## codeblocks
                # if context and context[-1] == "codeblock":
                #     if line[0:3] == "```":
                #         subtype = "close"
                #         context.pop()
                #         line = line[3:]
                #         pre_line = "</code></pre>"
                #     else:
                #         line_type = "codeblock"
                #         subtype = "cont"

                # elif line[0:3] == "```":
                #     line_type = "codeblock"
                #     subtype = "open"
                #     context.append("codeblock")
                #     line = line[3:]
                #     pre_line = "<pre><code>"

                # ## SINGLE-LINE ELEMENTS

                # ## horizontal rule
                # elif line[:3] == "***" or line[:3] == "---" or line[:3] == "___":
                #     line_type = "hr"
                #     line = ""
                #     pre_line = "<hr>"

                # ## headings
                # elif line[0] == "#":
                #     ## actually, this can appear inside p & blockquotes, so...
                #     ## maybe make into regex: ^[\s\*\+-\d\.>]*#
                #     level = h_depth.match(line).end()
                #     line_type = f"h{level}"
                #     id_count += 1
                #     subtype = f"h_{id_count}"
                #     line = initial_hash.sub("",line,1)
                #     headings.append((f'h_{id_count}',line))
                #     pre_line = f"<{line_type} id='h_{id_count}'>"
                #     post_line = f"</{line_type}>"

                # ## MULTI-LINE

                # ## details/summary (new)
                # elif line[:2] == ">+" or line[:2] == ">-":
                #     line_type = "details"
                #     status = "show" if line[1] == "+" else "hide"
                #     id_count += 1
                #     subtype = f"open:{status}:s_{id_count}"
                #     context += ("details")
                #     pre_line = f"<details><summary id='s_{id_count}'>"
                #     post_line = f"</summary>"

                
                # ## blockquotes
                # elif line[0] == ">":
                #     ## THIS IS A HACK: need to make this check recursive :(
                #     check_parent = is_embedded("blockquote",context)
                #     if line[1:3].find(">") >= 0:    ## embedded
                #         line_type = "blockquote"
                #         subtype = "embed"
                #         context += ("blockquote","p")
                #         line = line[3:]
                #         pre_line = f"</p><blockquote><p>"
                #     else:
                #         if not context:                 ## must be blockquote
                #             line_type = "blockquote"
                #             subtype = "open"
                #             context += ("blockquote","p")
                #             pre_line = f"<blockquote><p>"
                #         elif context[-1] == "p":        ## blockquote or details
                #             line_type = context[-2]
                #             if line[1:]:                ## blank line = new para
                #                 subtype = "cont"
                #             else:
                #                 subtype = "newpara"
                #                 pre_line = f"</p><p>"
                #     line = initial_gt.sub("",line,1)

                # ## lists (li): bullets (ul) & ol
                # elif line[:2] in ("+ ", "- ", "* ") or initial_digit.match(line) is not None:
                #     line_type = "ol" if line[0].isdigit() else "ul"
                #     prev = ""
                #     is_list,is_same_type = False, False
                #     check_parent = is_embedded(["ol","ul"],context)
                #     if check_parent:
                #         is_list = True
                #         prev = check_parent[-1][0]
                #         is_same_type = (line_type == prev)
                #         # is_same_type = (line_type == check_parent[-1][0])
                #     # print(f"l.{index}>>[{len(check_parent)}]:{check_parent=}|{line_type}, {prev=}")
                #     ## Already inside list
                #     ## nesting: text <li><p>; lists: <li><p>...</p><ul>...
                #     # pre_line = "<p class='list'>"
                #     # post_line = "</p>"
                #     if is_list:
                #         if indent == 0:
                #             if is_same_type:
                #                 subtype = "cont"
                #                 ## no need to update: status quo unchanged
                #                 # context += ("li","p")
                #                 pre_line = "</p></li><li><p>"
                #             else:
                #                 subtype = f"close_prev_open_new:{prev}"
                #                 pre_line = f"</p></li></{prev}><{line_type}><li><p>"
                #                 context = context[:-3]
                #                 context += (prev,"li","p")
                #         ## any type, close <p> & add a deeper level
                #         elif indent == 1:
                #             subtype = "open_new_level"
                #             context.pop()
                #             context += (line_type,"li","p")
                #             pre_line = f"</p><{line_type}><li><p>"
                #         ## any type, revert to higher level so close prev
                #         elif indent == -1:
                #             subtype = f"close_prev:{prev}"
                #             context = context[:-4]
                #             context += ("li","p")
                #             pre_line = f"</p></li></{prev}><li><p>"
                #         ## any type, adding a new level
                #     ## Outside a list, so start a new one
                #     else:
                #         subtype = "open_new_list"
                #         context += (line_type,"li","p")
                #         pre_line = f"<{line_type}><li><p>"

                #     # bullet = "" if line_type == "ol" else line[0]
                #     if line_type == "ul":
                #         line = line[2:].lstrip()
                #     else:
                #         line = initial_digit.sub("",line,1)

                # ## paragraph p
                # else:
                #     if context and context[-1] == "p":
                #         check_parent = is_embedded(["ul","ol","blockquote"],context)
                #         if check_parent:
                #             line_type = check_parent[-1][0]
                #         else:
                #             line_type = "p"
                #         subtype = "cont"
                #     else: 
                #         line_type = "p"
                #         subtype = "open"            ## DON'T NEED THESE?
                #         context.append("p")
                #         pre_line = "<p>"

            # else:
            #     line_type = "blank"
            #     if context:
            #         for tag in context[::-1]:
            #            pre_line += f"</{tag}>" 
            #         context.clear()
            #         # print(f"<debug>...{pre_line}")

                        
            # print(f"l.{index + 1:3}: {indent:2} {line_type:10} {subtype=:10} |{line[:25]}")
            # print(f"l.{index + 1:3}: {indent:2} {line_type:.<15}{subtype:10} {context} | {raw[:30]}")
            # print(f"\t{pre_line}{line[:50]}{post_line}")

            # if line:
            #     line = inline_markup(r,line)
            #     if line_type != "codeblock":
            #         line = subCode(line)

            # output += pre_line + line + post_line + EOL
            # if was_blank: 
            #     was_blank = False

    # with open(out_file, 'w') as f:
        # f.write(html_head + output + html_tail)

    # print(headings)

