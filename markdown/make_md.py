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





def parse_triggers(line,in_codeblock):
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

    # if not in_codeblock and bool(re.match(r' {2}|\t',line)):
    if not in_codeblock and bool(re.match(' '*tab_size,line)):
    # if bool(re.match(' '*tab_size,line)):
        line_type = "indent"
        # line = line.lstrip()
        line = line[tab_size:]
        
    else:

        ## codeblocks
        if line[0:3] == "```":
            line_type = "codeblock"
            if in_codeblock:
                subtype = "end"
                in_codeblock = False
            else:
                subtype = "start"
                in_codeblock = True
            line = line[3:]
        elif in_codeblock:
            line_type = "codeblock"
            subtype = "cont"

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
            line = line[2:]

        ## lists (li): bullets (ul) & ol
        elif line[:2] in ("+ ", "- ", "* "):
            line_type = "ul"
            line = line[1:]

        elif r1['initial_digit'].match(line):
            line_type = "ol"
            line = r1['initial_digit'].sub("",line,1)

        ## no explicit trigger
        else:
            line_type = "??"
    
    return (line,line_type,subtype, in_codeblock)


def parse_openers(cl,pl,cs):

    if cl.type == "codeblock":
        pass
        # if context(cs) != "codeblock":
        #     cl.subtype = "start"
        # else:
        #     cl.subtype = "end"
    
    # elif context(cs) == "codeblock":
        #     cl.type = "code"
            # cl.subtype = "cont"

    elif (cl.type == "??" and pl.type == "blank" 
            and cl.parent == "indent"
            and pl.subtype not in ("ul","ol","blockquote")):
        cl.type = "code2"
        cl.subtype = "start"
    elif cl.type == "??" and context(cs) == "code2" and cl.level == pl.level:
        cl.type = "code2"
        cl.subtype = "cont"
    elif cl.type == "blank" and context(cs) == "code2":
        cl.subtype = "code2:end"
    elif context(cs) == "code2":
        cl.type = "code2"
        cl.subtype = "cont"
        


    elif cl.type == "hr" and pl.type == "p":
        cl.subtype = "end:p"

    elif cl.type in ("details","blockquote"):
        embedding = is_embedded(cl.type,cs)
        embed_level = (len(embedding) - 1)
            
        if pl.parent == "blockquote" and (cl.level > pl.level):
            cl.subtype = "embed:start"
        elif context(cs) == cl.type:
            if cl.level > embed_level:
                cl.subtype = "embed:start"
            elif cl.level < embed_level:
                cl.subtype = "embed:end"
            ## This catches 'lazy blockquotes' w/o indented paras
            ## Simply restarts the blockquote so no need to reset stack
            elif pl.type == "blank":
                cl.subtype = "restart"
            else:
                cl.subtype = "cont"
        else:
            cl.subtype = "start"
            
    elif cl.type in ("ol", "ul"):
        both_lists = cl.type[:4] == pl.type[:4]
        same_type = cl.type == pl.type
        prev_higher = pl.level > cl.level
        prev_lower = pl.level < cl.level
        same_level = pl.level == cl.level
        if not both_lists:
            if pl.type == "p":
                cl.subtype = "new:li"
            else:
                # cl.subtype = "1:start"
                cl.subtype = "start"
        else:
            # if (not same_type or (same_type and prev_lower)):
            if prev_lower:
                cl.subtype = "embed:start"
            elif prev_higher:
                cl.subtype = "embed:end"
            else:
                if same_type:
                    cl.subtype = "new:li"
                else:
                    # cl.subtype = "2:start"
                    cl.subtype = "start"
        
    elif cl.type == "??":
        if pl.type in ("??","ol", "ul", "blockquote", "p", "empty"):
            cl.type = "p"
            cl.subtype = "cont"
        else:
            cl.type = "p"
            cl.subtype = "start"
        
    elif cl.type == "empty" and context(cs) == "blockquote":
        cl.subtype = "end-p:open-p"

    elif cl.type == "blank":
        cl.subtype = pl.type
        if context(cs) == "blockquote":
            cl.subtype = "blockquote:end"
            cs.pop()
        elif (context(cs) in ("ol", "ul")
                or cl.subtype in ("ol", "ul")):
            cl.subtype = f"{cl.subtype}:end"
            cl.hint = "ignore_if_blockquote_follows"
        elif cl.subtype == "p":
            cl.subtype = "end:p"
        else:
            cl.subtype = pl.type
            cl.level = pl.level

    return(cl.type,cl.subtype,cs)



def update_context(cl,pl,cs):
    if cl.hint:
        if cl.type == "blank" and cl.subtype != "blockquote":
            ## shouldn't need this next check: shows summat's  wrong with the stack
            # if context(cs)[:4] == "list":
            if context(cs) in ("ol","ul"):
                cl.subtype = "all:end"
                tmp = ["</p></li>"]
                for tag in close_tags_to("all",cs):
                    tmp.append(f"</{tag}>")
                cl.hint = "".join(tmp)
                cs.clear()
            ## add </li></{pl.hint[:2]}> to pre-line html string

    elif cl.type in ("codeblock", "code2", "details", "blockquote", "ul", "ol"):
        ## to catch both ‘start/end’ and ‘embed:start/end"
        if cl.subtype[-5:] == "start":
            cs.append(cl.type)
        elif cl.subtype[-3:] == "end":
            cs.pop()

    elif cl.type == "blank":
        if cl.subtype == "code2:end":
            cs.pop()
        elif cl.type in ("ul","ol"):
            cs.pop()
        elif context(cs) in ("ul","ol"):
            cs.pop()

    return(cl.type,cl.subtype,cl.hint,cs)



def build_html(cl):
    head = tail = ""
    tag = cl.type
    type = cl.type
    # if type[:4] == "list":
    if type in ("ul", "ol"):
        type = "list"
    #     tag = tag[5:]
    if type[0] == "h":
        type = "heading"
    elif type[:4] == "code":
        type = tag = "codeblock"

    match (type,cl.subtype):
        case ("indent"):
            pass
        case ("p","start"):
            head = "<p>"
        case ("p", "cont"):
            pass
        case("blank", "end:p"):
            head = "</p>" + EOL
        case ("empty", "p"):        ## l.114
            pass
        case ("empty","end-p:open-p"):
            # head = "</p>" + EOL + "<p>"
            head = "</p><p>"

        case ("heading",_):
            head = f"<{tag}>"
            tail = f"</{tag}>"

        case ("hr", "end:p"):
            head = "</p>" + EOL + "<hr>"
        case ("hr",_):
            head = "<hr>"
        
        case ("blockquote","start"):
            head = "<blockquote><p>"
        case ("blockquote","embed:start"):
            head = "</p><blockquote><p>"
        case ("blockquote","cont"):
            pass
        case ("blockquote","embed:end") \
            | ("blockquote","end") \
            | ("blank", "blockquote:end"):
            head = "</p></blockquote>"
        # case ("blockquote",""):
            
        case ("codeblock", "start"):
            head = "<pre><code>"
        case ("codeblock", "cont"):
            pass
        case ("codeblock", "end") | ("blank","code2:end"):
            tail = "</code></pre>"

        case ("list","start"):
            head = f"<{tag}><li><p>"
        case ("list","embed:start"):
            head = f"</p></li><{tag}><li><p>"
        case ("list","new:li"):
            head = "</p></li>" + EOL + "<li><p>"
        case ("list","embed:end"):
            head = f"</p></li></{tag}>" + EOL + f"<li><p>"
        case ("list","end"):
            head = f"</p></li></{tag}>"
        case ("empty", "list"):     ## l.112
            pass
        case ("blank","all:end"):
            head = cl.hint
            cl.hint = ""
            # print(f"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ {head}")
        
        # case ():
        # case ():
        # case ():

        case ("blank",_):
            pass
        case _:
            print(f"Ooooops! This slipped through: ({type,cl.subtype})")
    
    return (head,tail)
    



def pretty_debug():
    if cl.type == "blank":
        print(f'{"="*10} BLANK *{cl.subtype}, {cl.level}'
                f'{str(context_stack):24}  '
                # f'{" (" + cl.subtype + ", " + str(cl.level) + ", " + cl.hint + ")":55}'
                # f'{" (" + cl.subtype + ", " + str(cl.level) + ", " + cl.hint + ")":25}'
                f'{" (" + cl.hint + ")":25}'
                f'.')
    else:
        # tmp = f"{cl.type + '*' + cl.subtype} prnt={cl.parent}"
        tmp = f"{cl.type + '*' + cl.subtype}"
        tmp2 = f'pl={pl.type}_{pl.level}, pt={pl.parent}'
        if level == 0:
            print(f'l.{line_no:4}:{level}  '
                    f'{tmp:29} '
                    # f'{tmp2:24}  '
                    f'{str(context_stack):24}  '
                    f'[{len(context_stack):2}]'
                    f'| {raw[:30]}')
        else:
            print(f'{" "* 4}...{level}  '
                    f'{tmp:26} '
                    # f'{"...prnt=" + cl.parent:30}  '
                    f'{"":30}  '
                    f' |')
                    # f' | {cl.text[:30]}')




if __name__ == "__main__":
    in_file, out_file, title = prep_files()

    out_text = ""
    EOL = "\n"
    tab_is_set = False
    headings = []
    id_count = 0
    r = init_inline_styles()
    r1 = init_regex_tools()
    html_head,html_tail = init_html_outline()


    tab_size = 4
    context_stack = []
    in_codeblock = False
    body = ""
    # prev_pass_level = 0
    cl = Line("",-1,"blank","","","")
    pl = Line("",-1,"blank","","","")

    with open(in_file, 'r') as f, \
            open(out_file,'w') as o:
        o.write(html_head)
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
            pl.hint = cl.hint
            parent = ""
            cl = Line(raw,level,"unprocessed","",parent,"")
            
            while cl.type in ("unprocessed","blockquote","indent"):
                # cl.parent = parent
                if cl.text:
                    cl.text, cl.type, cl.subtype, in_codeblock = parse_triggers(cl.text, in_codeblock)
                    cl.level = level
                    cl.parent = parent
                else:
                    if level == 0:
                        cl.type = "blank"
                    else:
                        cl.type = "empty"
                        cl.parent = parent
                        cl.subtype = pl.type
                        cl.level = (level - 1)

                if cl.type in ("indent"):
                    ## contents will be parsed on the next pass
                    pass
                else:
                    pass
                    cl.type, cl.subtype,context_stack = parse_openers(cl,pl,context_stack)
                    ## normalize both forms of codeblock
                    # if cl.type == "code2":
                        # cl.type = "codeblock"

                    cl.type,cl.subtype,cl.hint,context_stack = update_context(cl,pl,context_stack)
                    head,tail = build_html(cl)
                    ## To prevent blockquote lines being processed twice
                    in_line = ""
                    # if cl.type == "codeblock":
                    # print(f"    >> {cl.type}")
                    if cl.type[:4] == "code":
                        in_line = cl.text.replace('<','&lt;').replace('>','&gt;').replace('amp;','')
                        # in_line = "**" + in_line
                    elif not (cl.type == "blockquote" and cl.level == 0):
                        in_line = inline_markup(r,cl.text)
                    # in_line = inline_markup(r,cl.text) 
                    line = head + in_line + tail + EOL
                    # body += (line + EOL)
                    # o.write(f"        {line}")
                    o.write(f"{line}")

                pretty_debug()

                ## This pass completed
                parent = cl.type
                level += 1

        o.write(html_tail)


    # with open(out_file, 'w') as f:
        # f.write(html_head + output + html_tail)
        # f.write(body)

    print()
    print(headings)

