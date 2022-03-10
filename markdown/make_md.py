# !/usr/bin/python

"""
Meant to parse markdown but is very limited. Needs re-writing to allow
for embedding.

'lazy indenting' doesn't work 
code blocks must be delimited with three backticks on a sep line
I added in super limited support for details>summary:
    >-

Notes to self:
    l.79: code2 overgeneralizing :() -- FIXED
    fixed (maybe...) blockquotes and embedding
    multi-line li lists don't parse. Need to look at the context, not the pl :( 
    l.227 embedded code isn't recognized as there is no standard tab size

"""

import sys
import os.path
import re
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class Line:
    text: str
    level: int
    type: str
    subtype: str
    parent: str


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
    r['link'] = (re.compile('[^!]\[(.*?)\]\((.+?)\)'), r'<a href="\2">\1</a>') 
    r['img'] = (re.compile('!\[(.*?)\]\((.+?)\)'), r'<img src="\2" alt="\1" />') 
    r['anchor'] = (re.compile('\[\^(.+?)]'), r'<span id="#\1">\1</span>') 
    r['email'] = (re.compile('&amp;lt;(.*?@.*?)&amp;gt;'), r'<a href="mailto:\1">\1</a>') 
    r['urls'] = (re.compile('&amp;lt;(.*?[\.\#].*?)&amp;gt;'), r'<a href="\1">\1</a>') 
    r['nbsp'] = (re.compile('\s\s\s*$'),r'&nbsp;')

    return r



def init_html_outline():
    return( "markdown", 
    "<p>No content</p>", 
    f"""
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
{body}
</article>
</body>
""")


def prep_files():
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

    return (in_file,out_file,title)



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
    inside = r1['p'].findall(line)
    ## Abort if no codeblocks found
    if not inside:
        return line

    ## extract the <code> sections and remove the automatic escaping
    ## reintegrate into the regular markdown text
    outside = r1['p1'].indall(line)
    final = r1['p2'].findall(line)
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



def context(context_stack):
    return context_stack[-1].split(":")[0] if context_stack else ""



def parse_triggers(line):
    line_type = subtype = ""
    line = line.expandtabs(4)
    global id_count

    global tab_size
    global tab_is_set
    ## Establish the size for tabs in this file
    if not tab_is_set and line[:2].isspace():
       tmp = re.match(r' +',line) 
       tab_size = len(tmp.group()) if tmp else 4
       tab_is_set = True

    if bool(re.match(r' {2}|\t',line)):
    # if bool(re.match(' '*tab_size,line)):
        line_type = "indent"
        # line = line.lstrip()
        line = line[tab_size:]
    else:

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
            level = r1['h_depth'].match(line).end()
            line_type = f"h{level}"
            id_count += 1
            subtype = f"h_{id_count}"
            # line = initial_hash.sub("",line,1)
            line = r1['extract_heading'].match(line).group(1).strip()
            headings.append((f'h_{id_count}',line))

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
            # line = line[1:].lstrip()
            line = line[1:]

        ## lists (li): bullets (ul) & ol
        elif line[:2] in ("+ ", "- ", "* "):
            line_type = "list:ul"
            # line = line[1:].lstrip()
            line = line[1:]

        elif r1['initial_digit'].match(line):
            line_type = "list:ol"
            line = r1['initial_digit'].sub("",line,1)

        ## no explicit trigger
        else:
            line_type = "??"
    
    return (line,line_type,subtype)


def parse_openers(cl,pl,cs):

    if cl.type == "codeblock":
        if context(cs) != "codeblock":
        # if pl.type == "blank":
            cl.subtype = "start"
            cs.append(cl.type)
        else:
            cl.subtype = "end"
            context_stack.pop()
    
    elif context(cs) == "codeblock":
            cl.type = "code"
            cl.subtype = "cont"

    elif (cl.type == "??" and pl.type == "blank" 
            and cl.parent == "indent"
            and pl.subtype not in ("list:ul","list:ol","blockquote")):
        cl.type = "code2"
        cl.subtype = "start"
        cs.append("code2")
    elif cl.type == "??" and context(cs) == "code2" and cl.level == pl.level:
        cl.type = "code2"
        cl.subtype = "cont"
    elif cl.type == "blank" and context(cs) == "code2":
        cl.subtype = "code:end"
        cs.pop()


    elif cl.type == "blank":
        cl.subtype = pl.type
        cl.level = pl.level

    elif (cl.type in ("details","blockquote")):
        embedding = is_embedded(cl.type,cs)
        embed_level = (len(embedding) - 1)
        if context(cs) == cl.type:
            if cl.level > embed_level:
                cl.subtype = "embed:start"
                cs.append(cl.type)
            elif cl.level < embed_level:
                cl.subtype = "embed:end"
                cs.pop()
            ## This catches 'lazy blockquotes' w/o indented paras
            ## Simply restarts the blockquote so no need to reset stack
            elif pl.type == "blank":
                cl.subtype = "restart"
            else:
                cl.subtype = "cont"
        else:
            cl.subtype = "start"
            cs.append(cl.type)
            
    elif (cl.type[:4] == "list"):
        both_lists = cl.type[:4] == pl.type[:4]
        same_type = cl.type == pl.type
        prev_higher = pl.level > cl.level
        prev_lower = pl.level < cl.level
        same_level = pl.level == cl.level
        if (pl.type[:4] != "list"):
            cl.subtype = "start"
        else:
            if (not same_type or (same_type and prev_lower)):
                cl.subtype = "start"
            elif (prev_higher):
                cl.subtype = "endprev:cont"
            else:
                cl.subtype = "cont"
        
    elif cl.type == "??" and pl.type in ("??","list:ol", "list:ul", "blockquote", "p", "empty"):
        cl.type = "p"
        cl.subtype = "cont"

    elif pl.type == "blank" and cl.type == "??":
        cl.type = "p"
        cl.subtype = "start"
        # cs.append(cl.type)
        
    elif cl.type[:4] == "list":
        if pl.type == "blank":
            cl.subtype = "start"
            ## etc.

    return(cl.type,cl.subtype,cs)


def parse_closers(cl,pl,cs):
    if cl.type == "blank" and context(cs) == "blockquote":
        cl.subtype = "blockquote:end"
        cs.pop()

    return(cl.type,cl.subtype,cs)


def pretty_debug():
    if cl.type == "blank":
        # print(f'{"="*10}BLANK: {cl.subtype + ", " + str(cl.level):32}.')
        print(f'{"="*10}BLANK'
                # f'{" "*14 + cl.subtype + ", " + str(cl.level):32}'
                f'{" (" + cl.subtype + ", " + str(cl.level) + ")":42}'
                f'.')
    else:
        tmp = f"{cl.type + '-' + cl.subtype}"
        tmp2 = f'<{pl.level}, {pl.type}> {cl.level == pl.level}'
        if level == 0:
            print(f'l.{line_no:4}:{level}  '
                    f'{tmp:21} '
                    f'{tmp2:18}  '
                    f'[{len(context_stack):3}]'
                    f'| {raw[:30]}')
        else:
            print(f'{" "* 4}...{level}  '
                    # f'{tmp:18}{" "*20}'
                    f'{tmp:25} '
                    f'{"@" + cl.parent:18}  '
                    f' |')




if __name__ == "__main__":
    in_file, out_file, title = prep_files()

    out_text = ""
    EOL = "\n"
    tab_is_set = False
    headings = []
    id_count = 0
    r = init_inline_styles()
    r1 = init_regex_tools()


    tab_size = 4
    context_stack = []
    body = ""
    # prev_pass_level = 0
    cl = Line("",-1,"blank","","")
    pl = Line("",-1,"blank","","")

    with open(in_file, 'r') as f:
        for line_no, raw in enumerate(f):
            # if line_no < 72 or line_no > 120:
            #     continue
            raw = raw.rstrip()      ## remove trailing space & EOL 
            level = 0
            pl.text = ""
            pl.type = cl.type
            pl.subtype = cl.subtype
            pl.level = cl.level
            pl.parent = cl.parent
            parent = ""
            cl = Line(raw,level,"unprocessed","",parent)
            
            while cl.type in ("unprocessed","blockquote","indent"):
                # cl.parent = parent
                # print(f">>>>>>>>>>>>>>>>>>>{cl.parent}")
                if cl.text:
                    cl.text, cl.type, cl.subtype = parse_triggers(cl.text)
                    cl.level = level
                    cl.parent = parent
                else:
                    if level == 0:
                        cl.type = "blank"
                    else:
                        cl.type = "empty"
                        cl.parent = parent
                        # cl.level = level
                        cl.subtype = pl.type
                        cl.level = (level - 1)

                if cl.type == "indent":
                    ## contents will be parsed on the next pass
                    pass
                else:
                    cl.type, cl.subtype,context_stack = parse_openers(cl,pl,context_stack)
                    ## normalize both forms of codeblock
                    # if cl.type == "code2":
                    #     cl.type = "code"

                    cl.type,cl.subtype,context_stack = parse_closers(cl,pl,context_stack)

                pretty_debug()

                ## This pass completed
                parent = cl.type
                level += 1


    # with open(out_file, 'w') as f:
        # f.write(html_head + output + html_tail)
        # f.write(body)

    print(headings)

