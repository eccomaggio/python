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
import math
from tokenize import group


@dataclass
class I:
    NUM = 0
    INDENT = 1
    BR = 2
    STACK = 3
    BLANK = 4
    REL = 5


G_tab_is_set = False
G_tab_length = 4


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
        # file_name = "test.md"
        file_name = "github_test.md"
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


# def is_embedded(taglist,the_list, result=[], count=0):
#     '''Returns list of all matching tags + their pos: [[<tag>,pos],...]'''
#     if count == 0:
#         result.clear()
#     if not isinstance(taglist, list):
#         taglist = [taglist]
#     if the_list:
#         pos = 0
#         for i, tag in enumerate(the_list[::-1]):
#             for target in taglist:
#                 if target == tag:
#                     pos = (len(the_list) - i) - 1
#                     result.insert(0,[tag,pos])
#                     break
#         is_embedded(taglist,the_list[:pos],result,count + 1)
#     return result


# def close_tags_to(tag, list):
#     ## returns nothing if tag is empty | not in list
#     ## returns all tags (in reverse order)  up to tag (inclusive)
#     ## returns entire list in reverse order if tag == "all"
#     if tag == "all":
#         tag = list[0]
#         # print(tag)
#     tmp = []
#     try:
#         list.index(tag)
#         for x in list[::-1]:
#             tmp.append(x)
#             if x == tag:
#                 break
#     except:
#         pass
#     return tmp


class Context:
    def __init__(self, el_list=None):
        if el_list is None:
            el_list = []
        self.context_list = el_list

    def new(self, el_list=None):
        if el_list is None:
            self.context_list = []
        else:
            el_list = [el_list] if isinstance(el_list, str) else el_list
            self.context_list = el_list
        return self.context_list

    def add(self, el_list):
        el_list = [el_list] if isinstance(el_list, str) else el_list
        self.context_list += el_list
        return self.context_list

    def contains(self, el):
        try:
            self.result = self.context_list.index(el)
        except IndexError:
            self.result = -1
        #self.result = self.context_list[self.result:] if self.result >= 0 else []
        return self.result

    def get(self):
        return self.context_list

    def pop(self, el=None):
        self.removed = []
        if el is None:
            self.removed = self.context_list[-1]
            self.context_list = self.context_list[:-1]
        else:
            el_pos = self.contains(el)
            if el_pos == -1:
                self.removed = []
            else:
                self.removed = self.context_list[el_pos:]
                self.context_list = self.context_list[:el_pos]
        return (self.context_list, self.removed)

    def close(self):
        self.removed = self.context_list
        self.context_list = []
        return self.removed

# def inline_markup(r,line):
def inline_markup(line):
    ## run all inline patterns against the line
    line = " " + line.replace("<","&lt;").replace(">", "&gt;").replace("&","&amp;")
    for i in r:
        line = r[i][0].sub(r[i][1],line)
    # inside = r1['p'].findall(line)
    # if inside:
    #     line = subCode(line)
    line = sub_code(line)
    return line


def sub_code(line):
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


# def context(context_stack):
#     return context_stack[-1].split(":")[0] if context_stack else ""


# def push_context(tag):
#     pass 

# def pop_context(tag):
#     pass



def parse_line_for_triggers(line, prev_was_blank, indent):
    # tmp_stack = ['B'] if prev_was_blank else []
    tmp_stack = []
    ## Inform both pre- and proceeding lines of blank
    if prev_was_blank:
        tmp_stack = ["B"]
        try:
            line_buffer[1][0][3] += ["B"]
        except IndexError:
            pass

        # line_buffer[2][1] += ["B"]

    trigger = ["dummy"]
    depth = 0
    while trigger:
        line, trigger = get_trigger(line, indent + depth)
        if trigger:
            if trigger[0][0] == "!":
                trigger[0] = trigger[0][1:]
                tmp_stack += trigger
                trigger = []
            else:
                tmp_stack += trigger
        depth += 1
        # else:
        #     tmp_stack.append("ø")
    return (line, tmp_stack)



def get_trigger(line, indent):
    global G_tab_length
    sep = "."
    stop_processing = "!"
    result = None

    # if not line:
    #     result = (line, False)
    
    ## explict codeblocks
    # elif re.search(r'```', line):
    if re.search(r'```', line):
        result = (line[3:], [f"{stop_processing}cb"])
    
    ## headings <h1, h2...>
    elif tmp := re.search(r'^(#+)\s+', line):
        result = (line[len(tmp.group()):], [f'{stop_processing}h{sep}{len(tmp.group(1))}'])
    
    ## blockquotes <blockquote>
    elif tmp := re.search(r'^(>+)(\s*)', line):
        # This accepts >> as two blockquotes (i.e. even if not separated by spaces)
        blockquote = []
        for i in range(len(tmp.group(1))):
            blockquote += [f"bq{sep}{str(indent + i)}"]
        line = line[len(tmp.group()):]
        result = (line, [*blockquote, "I"]) if len(tmp.group(2)) >= G_tab_length else (line, blockquote)
    
    ## ordered lists <ol><li>
    elif tmp := re.search(r'^\d+\.\s+', line):
        result = (line[len(tmp.group()):], [f"li{sep}{indent}{sep}o"])
    
    ## unordered lists <ul><li>
    elif tmp := re.search(r'^[\+\-\*]\s+', line):
        result = (line[len(tmp.group()):], [f"li{sep}{indent}{sep}u"])
    
    ## definition lists
    elif tmp := re.search(r'^\:\s+', line):
        # NB. requires the PREVIOUS line to marked up as <dl><dt>
        result = (line[len(tmp.group()):], ['df'])

    ## line <hr>
    elif re.search(r'^\s*?--{2,}\s*$', line):
        result = ("", ["!hr"])
    
    else:
        # result = (line, False)
        result = (line, [f"{stop_processing}p{sep}{indent}"]) ## runs forever 

    return result

def update_buffer(line_buffer):
    return [[[], ""]] + line_buffer[:-1]

def calculate_indent(line, prev):
    line.replace("\t","    ")
    global G_tab_is_set
    global G_tab_length
    tmp = re.search(r'^(\s+?)\S', line)
    if tmp:
        if not G_tab_is_set:
            G_tab_length = len(tmp.group(1))
            G_tab_is_set = True
        indent = math.ceil(len(tmp.group(1)) / G_tab_length)
    else:
        indent = 0
    # relative_indent = indent - buffer[1][0][I.INDENT]
    relative_indent = indent - prev
    return (indent, relative_indent, line)

def check_for_final_break(line):
    return bool(re.search(r'\s{2,}$', line))

def make_inferences(line):
    if line == ["I","B"]:
        pass

    return [line[0],inline_markup(line[1])]

def pretty_print(line_buffer):
    if len(line_buffer[0]):
        b = line_buffer[0]
        if b[0] == -1:
            print("\t...")
        else:
            if b[I.BLANK]:
                print(".")
            print(
            f'{b[I.NUM]:0>4}\t' +
            f'{b[I.INDENT]:<1} ' +
            # f'{str(b[I.BR]):<1} ' +
            f'{str(b[I.STACK]):<30} ' +
            f'{str(b[I.BLANK]):.1}' +
            f'{b[I.REL]:<1}' +
            f'\t{line_buffer[1]:.50}'
            )
    else:
        print("...")


if __name__ == "__main__":
    in_file, out_file, title = prep_files()

    # out_text = ""
    # EOL = "\n"
    # tab_is_set = False
    # tab_length = 4
    # headings = []
    # id_count = 0
    r = init_inline_styles()
    r1 = init_regex_tools()
    # html_head,html_tail = init_html_outline()
    # pretty = '{:<40}{:<50}'
    pretty = '{:<40}{:.50}'


    tab_size = 4
    context_stack = []
    # body = ""
    # buffer = [["",""],["",""],["",""]]
    line_buffer = [[[],""],[[],""],[[],""]]
    prev_was_blank = True # To show beginning of file
    prev_indent = 0

    with open(in_file, 'r') as f:
        for line_no, raw in enumerate(f):
            tmp_start_line = 0
            tmp_duration = 500
            tmp_start_line = (tmp_start_line - 2) if tmp_start_line > 0 else -1
            if tmp_start_line < line_no < (tmp_start_line + tmp_duration):
                if re.search(r'^\s*$',raw):
                    prev_was_blank = True
                    continue
                else:
                    line_buffer = update_buffer(line_buffer)
                    out_line = ["",""]
                    local_stack = []
                    indent, relative_indent, raw = calculate_indent(raw, prev_indent)
                    prev_indent = indent
                    has_final_break = check_for_final_break(raw)
                    line = raw.strip()
                    # line, local_stack = parse_line_for_triggers(line,prev_was_blank,relative_indent)
                    line, local_stack = parse_line_for_triggers(line,prev_was_blank,indent)
                    local_stack = (["I"] * indent) + local_stack
                    # out_line = [[line_no,indent,has_final_break,context_stack], process(line)]
                    out_line = [[line_no,indent,has_final_break,local_stack,prev_was_blank,relative_indent],line]
                    prev_was_blank = False
                    out_line = make_inferences(out_line)

                line_buffer[0] = out_line
                pretty_print(line_buffer[-1])
            ## To empty (& process) remaining buffer items
        for i in range(1,len(line_buffer)):
            line_buffer = update_buffer(line_buffer)
            pretty_print(line_buffer[-1])
                




