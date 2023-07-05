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
done: tag statuses: + open, - close, % open & close on same line, = context only: no tag output
done: triggers carry  main info (+ - % =) should be on triggers, not context
done: remove context from individual lines. > Rolling context, BUT mirrors line buffer
done: refactor to make more OOPy
done: colorized the debugging output
done: procrastinated magnificently...
todo: work out why i can't assign to Line()
todo: create html (including implementing context)
"""

import sys
import os.path
import re
from collections import OrderedDict
from dataclasses import dataclass
import math
from tokenize import group
from colorama import init, Fore, Back, Style

# Initializes Colorama
init(autoreset=True)

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

@dataclass
class Globals:
    tab_is_set = False
    tab_length = 4
    stop = "!"
    sep = "."
    pretty = "{:<40}{:.50}"
    inline_styles = OrderedDict()
    regex_tools = OrderedDict()
    html_outline = ""
    raw = 0     # latest line; no context added
    wip = 1     # previous line; context available (can look one line ahead)
    out = 2     # full context available (can look 2 lines ahead)

@dataclass
class Line:
    num: int = -1
    indent: bool = 0
    br: bool = False
    trigger = []
    blank: bool = False
    nblank: bool = False
    rel: int = 0
    text: str = ""

@dataclass
class Document:
    start_line: int = 0 # if 0, disregard end_line & show ALL lines
    end_line: int  = 0
    buffers = [Line(), Line(), Line()] # for parsing, 3 most recent lines kept in memory
    contexts = [Context(),Context(),Context()]
    prev_was_blank: bool = True  # To show beginning of file
    prev_indent: int = 0


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


def pretty_print(wip_line,context, wrapper=["<?>","</?>"]):
    if wip_line:
        if wip_line.num == -1:
            print("\t...")
        else:
            if wip_line.blank:
                print(".")
            print(
                f'{wip_line.num:0>4}\t' +
                f'{wip_line.indent:<1} ' +
                # f'{str(wip_line.br):<1} ' +
                Fore.CYAN +
                f'{str(wip_line.trigger):<30} ' +
                Style.RESET_ALL +
                f'{str(wip_line.blank):.1}' +
                f'{str(wip_line.nblank):.1} ' +
                f'{wip_line.rel:<1}' +
                Fore.YELLOW +
                f'\t{wip_line.text[:30]:<30}  ' +
                Style.RESET_ALL +
                f'{context.get() if context else "empty"}' +
                Fore.MAGENTA +
                f' {wrapper[0]}' +
                Fore.YELLOW +
                f'{wip_line.text[:3330]}...' +
                Fore.MAGENTA +
                f'{wrapper[1]}' +
                Style.RESET_ALL
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
    global g
    tmp = re.search(r'^(\s+?)\S', line)
    if tmp:
        if not g.tab_is_set:
            g.tab_length = len(tmp.group(1))
            g.tab_is_set = True
        indent = math.ceil(len(tmp.group(1)) / g.tab_length)
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
    global g
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
            tmp_stack += trigger[1:] if trigger[0] == g.stop else trigger
            trigger = []
        depth += 1
    return (line, tmp_stack)


def get_trigger(line, indent):
    global g
    skip = 0
    triggers = []
    local_context = []

    # explict codeblocks
    if tmp := re.search(r'(```)', line):
        # skip = 3
        skip = len(tmp.group())
        triggers = ["!", "code"]

    # headings <h1, h2...>
    elif tmp := re.search(r'^(#+)\s+', line):
        local_context.append("h")
        skip = len(tmp.group())
        depth = len(tmp.group(1))
        triggers = [g.stop, f'h{g.sep}{depth}']

    # blockquotes <blockquote>
    elif tmp := re.search(r'^(>+)(\s*)', line):
        # This accepts >> as two blockquotes (i.e. even if not separated by spaces)
        blockquote = []
        for i in range(len(tmp.group(1))):
            blockquote += [f"bq{g.sep}{str(indent + i)}"]
        if len(tmp.group(2)) >= g.tab_length:
            skip = len(tmp.group())
            # triggers = [*blockquote, ["I"]]
            triggers = [*blockquote, "I"]
        else:
            triggers = blockquote

    # lists <ul>/<ol><li>
    elif tmp := re.search(r'^(\d+\.|\+|\-|\*)\s+', line):
        list_type = "ol" if "." in tmp.group() else "ul"
        skip = len(tmp.group())
        triggers = [f"li{g.sep}{list_type}{g.sep}{indent}"]

    # definition lists
    elif tmp := re.search(r'^\:\s+', line):
        # NB. requires the PREVIOUS line to marked up as <dl><dt>
        skip = len(tmp.group())
        triggers = ['df']

    # line <hr>
    elif re.search(r'^\s*?--{2,}\s*$', line):
        triggers = [g.stop,"hr"]

    else:
        tmp = "br"
        if line.strip() and "h" not in local_context:
            tmp = f"p{g.sep}{indent}"
        triggers = [g.stop, tmp]  # else runs forever
    return (line[skip:], triggers)


def build_context(line_no):
    global doc
    doc.contexts[0].add_to_end(line_no)


def initial_parse(line_no, raw, prev_was_blank, prev_indent):
    triggers = []
    indent, relative_indent, raw = calculate_indent(raw, prev_indent, prev_was_blank)
    has_final_break = check_for_final_break(raw)
    line = raw.strip()
    line, triggers = parse_line_for_triggers(line, prev_was_blank, indent)
    tmp = Line()
    tmp.num = line_no
    tmp.indent = indent
    tmp.br = has_final_break
    tmp.trigger = triggers
    tmp.blank = prev_was_blank
    tmp.nblank = False
    tmp.text = line
    # tmp = Line(
    #     line_no,
    #     indent,
    #     has_final_break,
    #     triggers,
    #     prev_was_blank,
    #     False,
    #     relative_indent,
    #     line
    # )
    return tmp

def increment_buffer():
    ## create empty initial and drop final, i.e. [1,2,3] > [0,1,2]
    global g
    global doc
    doc.buffers = [Line()] + doc.buffers[:g.out]
    doc.contexts = [Context()] + doc.contexts[:g.out]

def add_line_to_buffer(line: Line):
    if line:
        global g
        global doc
        # make room for new line
        increment_buffer()
        doc.buffers[g.raw] = line
        doc.contexts[g.raw].add_to_end(line.num)

def update_wip_buffer():
    global g
    global doc
    if doc.buffers[g.wip]:
        next_is_blank = doc.prev_was_blank
        ln = doc.buffers[g.wip]
        # ln.trigger = ln.trigger
        if next_is_blank:
            ln.nblank = True
        prev_was_blank = ln.blank
        if not ln.trigger:
            return
        for i,el in enumerate(ln.trigger):
            # if not isinstance(el,str):
            #     raise Exception(f"not a string: {el}, {ln.trigger}")
            head, *tail = el.split(g.sep)
            tmp = ""
            if head == "li":
                if not next_is_blank and doc.buffers[g.raw].trigger[0][0] == "p":
                    tmp = "<"
                ## match all li with immediately preceeding li
                ## earlier line has been processed, so must remove added elements
                elif [match for match in doc.buffers[g.out].trigger if match[:7] == el]:
                    tmp = "%"
                    if next_is_blank:
                        tmp += g.sep + ">"
                else:
                    tmp = "%" + g.sep + "<"
                ln.trigger[i] += g.sep + tmp

            elif head == "p":
                if prev_was_blank and next_is_blank:
                    tmp = "%"
                elif prev_was_blank:
                    tmp = "<"
                elif next_is_blank:
                    tmp = ">"
                else:
                    tmp = "="
                ln.trigger[i] += g.sep + tmp

def update_out_buffer():
    pass
    # global G_line_buffers
    # if G_line_buffers[OUT]:
    #     pass

def build_html_wrapper(line: Line):
    # html_open = html_close = ""
    html_open = f"<{line.num}>"
    html_close = f"</{line.num}>"
    return [html_open, html_close]

def process_line(line: Line):
    global g
    global doc
    # increment_buffer()
    add_line_to_buffer(line)
    # update_wip_buffer(doc.prev_was_blank)
    update_wip_buffer()
    update_out_buffer()
    doc.prev_was_blank = False
    pretty_print(doc.buffers[g.out], doc.contexts[g.out],build_html_wrapper(doc.buffers[g.out]))

if __name__ == "__main__":
    g = Globals()
    g.inline_styles = init_inline_styles()
    g.regex_tools = init_regex_tools
    g.html_outline = init_html_outline

    in_file, out_file, title = prep_files()
    # doc = Document(0)
    doc = Document(10,20)
    if doc.start_line:
        print(f"Showing document, lines {doc.start_line} to {doc.end_line}")
    else:
        print("Showing complete document")

    # EOL = "\n"
    # tab_is_set = False
    # tab_length = 4
    # headings = []
    # id_count = 0

    with open(in_file, 'r') as f:
        for line_no, raw in enumerate(f):
            if doc.start_line:
                if line_no < doc.start_line or line_no > doc.end_line:
                    continue
            if re.search(r'^\s*$', raw):
                doc.prev_was_blank = True
                # continue
            else:
                # process_line(initial_parse( line_no, raw, doc.prev_was_blank, doc.prev_indent))
                line: Line = initial_parse( line_no, raw, doc.prev_was_blank, doc.prev_indent)
                process_line(line)
    # To empty (& process) remaining buffer items
    for i in range(1, len(doc.buffers)):
        process_line(doc.buffers[g.out])