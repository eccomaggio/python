# !/usr/bin/python

"""
Meant to parse markdown but is very limited. Needs re-writing to allow
for embedding.

'lazy indenting' doesn't work
code blocks must be delimited with three backticks on a sep line
I added in super limited support for details>summary:
    >-

Notes to self:

done: Remove B and I from triggers: they are available as flags
info: tag statuses: + open, - close, % open & close on same line, = context only: no tag output
done: triggers carry  main info (+ - % =) should be on triggers, not context
todo: remove context from individual lines. > Rolling context, BUT mirrors line buffer
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
    NUM = 0      # line number
    INDENT = 1   # indent count
    BR = 2       # break @ EOL (not all versions of MD)
    TRIGGER = 3  # list of triggers
    BLANK = 4    # previous line was blank
    NBLANK = 5   # next line is blank
    REL = 6      # relative indent (i.e. indent depth)
    CONTEXT = 7  # context list
    LINE = 8     # line text
    WRAPPER = 9  # html wrapper (open,close)

class Context:
    def __init__(self, el_list=None):
        if el_list is None:
            self.context_list = []
        else:
            # el_list = [el_list] if not isinstance(el_list, list) else el_list
            el_list = self.normalize(el_list)
            self.context_list = el_list

    def __str__(self):
        # return ",".join([f"{el}" for el in self.context_list])
        self.stringify()

    def normalize(self,el):
        return [el] if not isinstance(el, list) else el

    def reset(self, el_list=None):
        self.__init__(el_list)

    def add_to_end(self, el_list):
        """
        add the string or list to the end
        return the full new list
        """
        # el_list = [el_list] if isinstance(el_list, str) else el_list
        el_list = self.normalize(el_list)
        self.context_list.extend(el_list)
        return self.context_list

    def first_match(self, el):
        """
        return the first match
        """
        try:
            self.result = self.context_list.index(el) + 1
        except ValueError:
            # self.result = -1
            self.result = 0
        return self.result

    def partial_match(self, match):
        """
        return all entries that match the initial letter(s) given
        """
        return [i for i in self.context_list if i[:len(match)] == match]

    def get(self):
        return self.context_list

    def stringify(self):
        return ",".join([f"{el}" for el in self.context_list])

    def drop_last(self, el=None):
        """
        if nothing specified, drop (and return) the last element
        else drop (and return) all elements from the one specified to the end
        """
        self.removed = []
        if el is None:
            self.removed = self.context_list[-1]
            self.context_list = self.context_list[:-1]
        else:
            self.el_pos = self.first_match(el)
            if not self.el_pos:
                self.removed = []
            else:
                self.removed = self.context_list[self.el_pos - 1:]
                self.context_list = self.context_list[:self.el_pos - 1]
        return self.removed

    def empty(self):
        self.removed = self.context_list
        self.context_list = []
        return self.removed


# Buffers & Contexts (they are parallel)
RAW = 0     # latest line; no context added
WIP = 1     # previous line; context available (can look one line ahead)
OUT = 2     # full context available (can look 2 lines ahead)

# G_tab_is_set = False
# G_tab_length = 4
# G_stop = "!"
# G_sep = "."
# G_line_buffer = [[],[],[]]
# G_context = [[],[],[]]

def init_regex_tools():
    r1 = OrderedDict()
    # regex to remove escaping inside <code> tags
    r1['p'] = re.compile(r'(?:<code>)(.*?)(?:</code>)')
    r1['p1'] = re.compile(r'(.*?<code>).*?(</code>.*)')
    r1['p2'] = re.compile(r'.*</code>(.*)$')

    r1['initial_digit'] = re.compile(r'\d+\.\s')
    # initial_gt = re.compile(r'>+\s')  ## this misses blank-line >
    r1['initial_gt'] = re.compile(r'>\s?')
    # initial_hash = re.compile(r'#+\s')
    r1['extract_heading'] = re.compile(r'^\#+([^\#]+)\#*\s*$')
    r1['h_depth'] = re.compile("#+")
    return r1


def init_inline_styles():
    # regex to add inline styling
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
    r['link'] = (re.compile('([^!])\[(.*?)\]\((.+?)\)'),
                 r'\1<a href="\3">\2</a>')
    r['img'] = (re.compile('!\[(.*?)\]\((.+?)\)'),
                r'<img src="\2" alt="\1" />')
    r['anchor'] = (re.compile('\[\^(.+?)]'), r'<span id="#\1">\1</span>')
    r['email'] = (re.compile('&amp;lt;(.*?@.*?)&amp;gt;'),
                  r'<a href="mailto:\1">\1</a>')
    r['urls'] = (re.compile('&amp;lt;(.*?[\.\#].*?)&amp;gt;'),
                 r'<a href="\1">\1</a>')
    r['nbsp'] = (re.compile('\s\s\s*$'), r'&nbsp;')

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
    return (html_head, html_tail)

def pretty_print(wip_line,context):
    if wip_line:
        if wip_line[0] == -1:
            print("\t...")
        else:
            if wip_line[I.BLANK]:
                print(".")
            print(
                f'{wip_line[I.NUM]:0>4}\t' +
                f'{wip_line[I.INDENT]:<1} ' +
                # f'{str(b[I.BR]):<1} ' +
                f'{str(wip_line[I.TRIGGER]):<30} ' +
                f'{str(wip_line[I.BLANK]):.1}' +
                f'{str(wip_line[I.NBLANK]):.1} ' +
                f'{wip_line[I.REL]:<1}' +
                f'\t{wip_line[I.LINE][:30]:<30}  ' +
                # f'{G_contexts[-1].get() if G_contexts[-1] else "empty"}'
                f'{context.get() if context else "empty"}'
                # f'{b[I.CONTEXT]}'
                f'{" " + wip_line[I.WRAPPER] if I.WRAPPER < len(wip_line) else ""}'
            )
    else:
        print("...")



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
        except IndexError:
            tmp = in_file
        out_file = tmp + ".html"

        tmp = in_file.rfind(".")
        title = in_file[:tmp] if tmp >= 0 else "from markdown file"
        print(f"Using the markdown in {in_file} to output html as {out_file}")

    return (in_file, out_file, title)


def calculate_indent(line, prev, prev_was_blank):
    line.replace("\t", "    ")
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
    relative_indent = 0 if prev_was_blank else (indent - prev)
    return (indent, relative_indent, line)


def check_for_final_break(line):
    return bool(re.search(r'\s{2,}$', line))


def inline_markup(line):
    # run all inline patterns against the line
    line = " " + line.replace("<", "&lt;").replace(">",
                                                   "&gt;").replace("&", "&amp;")
    for i in r:
        line = r[i][0].sub(r[i][1], line)
    # inside = r1['p'].findall(line)
    # if inside:
    #     line = subCode(line)
    line = sub_code(line)
    return line


def sub_code(line):
    inside = r1['p'].findall(line)
    # Abort if no codeblocks found
    if not inside:
        return line

    # extract the <code> sections and remove the automatic escaping
    # reintegrate into the regular markdown text
    outside = r1['p1'].findall(line)
    final = r1['p2'].findall(line)
    for i, match in enumerate(inside):
        tmp = match
        tmp = strip_to_pre(tmp)
        inside[i] = tmp
    out = ""
    for i, code in enumerate(outside):
        out += f"{code[0]}{inside[i]}{code[1]}"
    out += f"{''.join(final)}"
    return out


def strip_to_pre(line):
    return line.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')

def parse_line_for_triggers(line, prev_was_blank, indent):
    global G_stop
    # tmp_stack = ['B'] if prev_was_blank else []
    tmp_stack = []
    ## add blank to beginning of current trigger list (i.e. prev_was_blank)
    # if prev_was_blank:
    #     tmp_stack = ["B"]
    trigger = ["dummy"]
    depth = 0
    while trigger:
        line, trigger = get_trigger(line, indent + depth)
        if trigger:
            tmp_stack += trigger[1:] if trigger[0] == G_stop else trigger
            trigger = []
        depth += 1
    # if indent:
    #     tmp_stack = (["I"] * indent) + tmp_stack
    return (line, tmp_stack)


def get_trigger(line, indent):
    global G_tab_length
    # global context
    global G_stop
    global G_sep
    skip = 0
    triggers = []
    local_context = []

    # explict codeblocks
    if re.search(r'```', line):
        skip = 3
        triggers = ["!", "code"]

    # headings <h1, h2...>
    elif tmp := re.search(r'^(#+)\s+', line):
        local_context.append("h")
        skip = len(tmp.group())
        depth = len(tmp.group(1))
        triggers = [G_stop, f'h{G_sep}{depth}']

    # blockquotes <blockquote>
    elif tmp := re.search(r'^(>+)(\s*)', line):
        # This accepts >> as two blockquotes (i.e. even if not separated by spaces)
        blockquote = []
        for i in range(len(tmp.group(1))):
            blockquote += [f"bq{G_sep}{str(indent + i)}"]
        if len(tmp.group(2)) >= G_tab_length:
            skip = len(tmp.group())
            triggers = [*blockquote, ["I"]]
        else:
            triggers = blockquote

    # lists <ul>/<ol><li>
    elif tmp := re.search(r'^(\d+\.|\+|\-|\*)\s+', line):
        list_type = "ol" if "." in tmp.group() else "ul"
        skip = len(tmp.group())
        # triggers = [f"li{G_sep}{list_type}{G_sep}{indent}", f"p{G_sep}{indent}"]
        triggers = [f"li{G_sep}{list_type}{G_sep}{indent}"]

    # definition lists
    elif tmp := re.search(r'^\:\s+', line):
        # NB. requires the PREVIOUS line to marked up as <dl><dt>
        skip = len(tmp.group())
        triggers = ['df']

    # line <hr>
    elif re.search(r'^\s*?--{2,}\s*$', line):
        # result = ("", [G_stop,"hr"])
        triggers = [G_stop,"hr"]

    else:
        tmp = "br"
        # if line.strip() and
        if line.strip() and "h" not in local_context:
            tmp = f"p{G_sep}{indent}"
        triggers = [G_stop, tmp]  # else runs forever
    return (line[skip:], triggers)


def build_context(line_no):
    global G_contexts
    global G_line_buffers
    # G_context[0] = Context(str(line_no))
    G_contexts[0].add_to_end(line_no)
    # print(">>>>>>>>>",G_contexts[0])


def first_pass(line_no, raw, prev_was_blank, prev_indent):
    triggers = []
    # G_context[0] = Context(str(line_no))
    indent, relative_indent, raw = calculate_indent(raw, prev_indent, prev_was_blank)
    has_final_break = check_for_final_break(raw)
    line = raw.strip()
    line, triggers = parse_line_for_triggers(line, prev_was_blank, indent)
    return [
        line_no,
        indent,
        has_final_break,
        triggers,
        prev_was_blank,
        False,
        relative_indent,
        [],
        # context.get(),
        line,
        "nowt yet"
    ]

def increment_buffer():
    ## create empty initial and drop final, i.e. [1,2,3] > [0,1,2]
    global G_line_buffers
    global G_contexts
    # G_line_buffers = [[]] + G_line_buffers[:-1]
    # G_contexts = [Context()] + G_contexts[:-1]
    G_line_buffers = [[]] + G_line_buffers[:OUT]
    G_contexts = [Context()] + G_contexts[:OUT]

def update_RAW_buffer(out_line):
    global G_line_buffers
    G_line_buffers[RAW] = out_line
    G_contexts[RAW].add_to_end(out_line[I.NUM])
    # build_context(out_line[I.NUM])


def update_WIP_buffer(next_is_blank):
    global G_line_buffers
    if not G_line_buffers[WIP]:
        return
    else:
        ln = G_line_buffers[WIP]
        trig = ln[I.TRIGGER]
        # context = Context(ln[I.CONTEXT])
        if next_is_blank:
            ln[I.NBLANK] = True
        prev_was_blank = ln[I.BLANK]
        for i,el in enumerate(trig):
            head, *tail = el.split(G_sep)
            tmp = ""
            if head == "li":
                if not next_is_blank and G_line_buffers[RAW][I.TRIGGER][0][0] == "p":
                    # trig[i] += f"{G_sep}<"
                    tmp = "<"
                    # context.push(el)
                    # ln[I.CONTEXT].append(el)
                ## match all li with immediately preceeding li
                ## earlier line has been processed, so must remove added elements
                elif [match for match in G_line_buffers[OUT][I.TRIGGER] if match[:7] == el]:
                    tmp = "%"
                    if next_is_blank:
                        tmp += G_sep + ">"
                        # context.pop()
                else:
                    tmp = "%" + G_sep + "<"
                    # context.push(el)
                trig[i] += G_sep + tmp

            elif head == "p":
                if prev_was_blank and next_is_blank:
                    tmp = "%"
                elif prev_was_blank:
                    tmp = "<"
                elif next_is_blank:
                    tmp = ">"
                else:
                    tmp = "="
                trig[i] += G_sep + tmp

def update_OUT_buffer():
    global G_line_buffers
    if G_line_buffers[OUT]:
        G_line_buffers[OUT][I.WRAPPER] = "</>"



if __name__ == "__main__":
    in_file, out_file, title = prep_files()
    G_tab_is_set = False
    G_tab_length = 4
    G_stop = "!"
    G_sep = "."
    G_line_buffers = [[],[],[]]
    G_contexts = [Context(),Context(),Context()]

    # out_text = ""
    # EOL = "\n"
    # tab_is_set = False
    # tab_length = 4
    # headings = []
    # id_count = 0
    r = init_inline_styles()
    r1 = init_regex_tools()
    # html_head,html_tail = init_html_outline()
    pretty = '{:<40}{:.50}'

    tab_size = 4
    # context = Context()
    # for parsing purposes, 3 most recent lines kept in memory
    # each line consists of [ [surrounding tags], inner html string ]
    # line_buffer = [[[], ""], [[], ""], [[], ""]]
    # line_buffer = [[],[],[]]
    prev_was_blank = True  # To show beginning of file
    prev_indent = 0
    tmp_start_line = 121
    tmp_duration = 229 - tmp_start_line
    tmp_start_line = (tmp_start_line - 2) if tmp_start_line > 0 else -1

    with open(in_file, 'r') as f:
        for line_no, raw in enumerate(f):
            if tmp_start_line < line_no < (tmp_start_line + tmp_duration):
                if re.search(r'^\s*$', raw):
                    prev_was_blank = True
                    continue
                else:
                    out_line = first_pass( line_no, raw, prev_was_blank, prev_indent)
                    # build_context(line_no)
                    update_RAW_buffer(out_line)
                    update_WIP_buffer(prev_was_blank)
                    update_OUT_buffer()
                    prev_was_blank = False
                    increment_buffer()
                pretty_print(G_line_buffers[OUT], G_contexts[OUT])
            # To empty (& process) remaining buffer items
    for i in range(1, len(G_line_buffers)):
        increment_buffer()
        pretty_print(G_line_buffers[OUT], G_contexts[OUT])
