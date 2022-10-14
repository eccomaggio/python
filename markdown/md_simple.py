# !/usr/bin/python

"""
Meant to parse markdown but is very limited. Needs re-writing to allow
for embedding.

'lazy indenting' doesn't work 
code blocks must be delimited with three backticks on a sep line
I added in super limited support for details>summary:
    >-

Notes to self:
    + l.79: code2 overgeneralizing :() -- FIXED
    + fixed (maybe...) blockquotes and embedding
    + multi-line li lists don't parse. Need to look at the context, not the pl :( 
    + l.227 embedded code isn't recognized as there is no standard tab size -- FIXED
    + lists with multi-line paras still a problem -- tentatively fixed
    + CONTEXT_STACK seems to be behaving
    - l.218 space before blockquote = problem: for every blank, need to add effect in 'hint'
    - non-backtick-delimited codeblocks still a pain (incorporate levels)
    - lists embedded in blockquotes a problem (e.g. l.111)
    + CLOSE LISTS with BLANK -- FIXED
    - !! line 196: 
    if: (this will solve code2 problems)
line 1 = indent + p (i.e. inside blockquote/list)
line 2 = blank
line 3 = indent + p
> line 3 is a continuation of the blockquote/list NOT a codeblock
i.e. need to make blank a promise

"""

import sys
import os.path
import re
from collections import OrderedDict
from dataclasses import dataclass
import enum


class Tags(enum.Enum):
    p = 1
    ul = 2
    ol = 3
    blockquote = 4
    codeblock = 5



@dataclass
class Line:
    text: str
    level: int
    type: str
    subtype: str
    parent: str
    hint: str


def init_regex_tools():
    r1 = OrderedDict()
    ## regex to remove escaping inside <code> tags
    r1['p'] = re.compile(r'(?:<code>)(.*?)(?:</code>)')
    r1['p1'] = re.compile(r'(.*?<code>).*?(</code>.*?)')
    r1['p2'] = re.compile(r'.*</code>(.*?)$')

    r1['initial_digit'] = re.compile(r'\d+\.\s')
    # initial_gt = re.compile(r'>+\s')  ## this misses blank-line >
    r1['initial_gt'] = re.compile(r'>\s?')
    # initial_hash = re.compile(r'#+\s')
    r1['extract_heading'] = re.compile(r'^\#+([^\#]+)\#*\s*$')
    r1['h_depth'] = re.compile("#+")
    return r1


def init_inline_styles():
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
    # r['link'] = (re.compile('[^!]\[(.*?)\]\((.+?)\)'), r'<a href="\2">\1</a>') 
    r['link'] = (re.compile('([^!])\[(.*?)\]\((.+?)\)'), r'\1<a href="\3">\2</a>') 
    r['img'] = (re.compile('!\[(.*?)\]\((.+?)\)'), r'<img src="\2" alt="\1" />') 
    r['anchor'] = (re.compile('\[\^(.+?)]'), r'<span id="#\1">\1</span>') 
    r['email'] = (re.compile('&amp;lt;(.*?@.*?)&amp;gt;'), r'<a href="mailto:\1">\1</a>') 
    r['urls'] = (re.compile('&amp;lt;(.*?[\.\#].*?)&amp;gt;'), r'<a href="\1">\1</a>') 
    r['nbsp'] = (re.compile('\s\s\s*$'),r'&nbsp;')

    return r


def init_html_outline():
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

    html_tail = f"""
</article>
</body>

"""
    return (html_head,html_tail)

def prep_files():
    try:
        file_name = sys.argv[1]
    except IndexError:
        print("No filename specified; I'll look for test.md")
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

    return (in_file,out_file,title)


def is_embedded(taglist,the_list, result=[], count=0):
    '''Returns list of all matching tags + their pos: [[<tag>,pos],...]'''
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


def close_tags_to(tag, list):
    ## returns nothing if tag is empty | not in list
    ## returns all tags (in reverse order)  up to tag (inclusive)
    ## returns entire list in reverse order if tag == "all"
    if tag == "all":
        tag = list[0]
        # print(tag)
    tmp = []
    try:
        list.index(tag)
        for x in list[::-1]:
            tmp.append(x)
            if x == tag:
                break
    except:
        pass
    return tmp


def inline_markup(r,line):
    ## run all inline patterns against the line
    line = " " + line.replace("<","&lt;").replace(">", "&gt;").replace("&","&amp;")
    for i in r:
        line = r[i][0].sub(r[i][1],line)
    # inside = r1['p'].findall(line)
    # if inside:
    #     line = subCode(line)
    line = subCode(line)
    return line


def subCode(line):
    inside = r1['p'].findall(line)
    ## Abort if no codeblocks found
    if not inside:
        return line

    ## extract the <code> sections and remove the automatic escaping
    ## reintegrate into the regular markdown text
    outside = r1['p1'].findall(line)
    final = r1['p2'].findall(line)
    for i, match in enumerate(inside):
        tmp = match
        tmp = strip_to_pre(tmp)
        inside[i] = tmp
    out = ""
    for i,code in enumerate(outside):
        out += f"{code[0]}{inside[i]}{code[1]}"
    out += f"{''.join(final)}"
    return out


def strip_to_pre(line):
    return line.replace('&lt;','<').replace('&gt;','>').replace('&amp;','&')


def context(context_stack):
    return context_stack[-1].split(":")[0] if context_stack else ""








def get_trigger(line):
    tmp = re.search(r'```', line)
    if tmp:
        return ('codeblock', line[3:])
    tmp = re.search(r'^(#)+\s+', line)
    if tmp:
        return (f'h{len(tmp.group(1))}', line[len(tmp.group()):])
    tmp = re.search(r'^(>)+\s+', line)
    if tmp:
        return (f'blockquote({len(tmp.group(1))})', line[len(tmp.group()):])
    tmp = re.search(r'^\d+\.\s+', line)
    if tmp:
        return (f'ol',line[len(tmp.group()):])
    tmp = re.search(r'^[\+\-\*]\s+', line)
    if tmp:
        return (f'ul', line[2:])
    tmp = re.search(r'^\:\s+', line)
    if tmp: 
        # NB. requires the PREVIOUS line to marked up as <dl><dt>
        return ('definition', line[len(tmp.group()):])
    return ('',line)

def process(line):
    return line

def update_buffer(buffer):
    # buffer[2] = buffer[1]
    # buffer[1] = buffer[0]
    # buffer[0] = ""
    for i in reversed(range(len(buffer) - 1)):
        buffer[i + 1] = buffer[i]
    buffer[0] = -1
    return buffer


if __name__ == "__main__":
    in_file, out_file, title = prep_files()

    # out_text = ""
    # EOL = "\n"
    # tab_is_set = False
    # headings = []
    # id_count = 0
    # r = init_inline_styles()
    # r1 = init_regex_tools()
    # html_head,html_tail = init_html_outline()


    tab_size = 4
    # context_stack = []
    # body = ""
    buffer = ["","",""]

    with open(in_file, 'r') as f:
        for line_no, raw in enumerate(f):
            buffer = update_buffer(buffer)
            out_line = ""
            context_stack = []
            if re.search(r'^\s*$',raw):
                # print("\t--blank--")
                out_line = "\t--blank--"
                # continue
            else:
                tmp = re.search(r'^(\s+?)\S', raw)
                indent = len(tmp.group(1)) if tmp else 0
                tmp = re.search(r'\s{2,}$', raw)
                has_br = bool(re.search(r'\s{2,}$', raw))
                line = raw.strip()
                trigger = "dummy"
                while trigger:
                    trigger,line = get_trigger(line)
                    if trigger:
                        context_stack.append(trigger)
                    else:
                        context_stack.append("ø")
                # print(line_no,'\t',indent,has_br, context_stack, f'|{line}')
                out_line = f"{line_no}\t{indent} {has_br} {context_stack} |{line}"
            buffer[0] = process(out_line)
            if buffer[2]:
                print(buffer[2])
            else:
                print("...")
        ## To empty (& process) remaining buffer items
        for i in range(1,len(buffer)):
            buffer = update_buffer(buffer)
            out_line = process(buffer[2])
            print(out_line)
            




