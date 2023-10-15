"""
    go through .txt
    identify unit numbers (#)
    add as prefix to all relevant lines
    group & associate correctly
    deal with macrons (i.e. create lookup without them; use ":" internally? strip out if ignoring macros; replace with macros for display?)

"""
from pprint import pprint
from dataclasses import dataclass
from pathlib import Path
import sys
import getopt
import json
import re

class col:
    '''Colors class:reset all colors with colors.reset; two
    sub classes fg for foreground and bg for background; use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.green also, the generic bold, disable,
    underline, reverse, strike through, and invisible work with the main class i.e. colors.bold
    '''
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strikethrough = '\033[09m'
    invisible = '\033[08m'

    class fg:
            black = '\033[30m'
            red = '\033[31m'
            green = '\033[32m'
            orange = '\033[33m'
            blue = '\033[34m'
            purple = '\033[35m'
            cyan = '\033[36m'
            lightgrey = '\033[37m'
            darkgrey = '\033[90m'
            lightred = '\033[91m'
            lightgreen = '\033[92m'
            yellow = '\033[93m'
            lightblue = '\033[94m'
            pink = '\033[95m'
            lightcyan = '\033[96m'

    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        lightgrey = '\033[47m'


def get_current_directory():
    return Path( __file__ ).parent.absolute()


def read_json(filename="latin.json"):
    json_file_address = Path(get_current_directory() / filename)
    with open(json_file_address, "r") as f:
        return json.load(f)


# def retrieve_file_by_suffix(suffix="csv"):
#     if suffix[0] == ".":
#         suffix = suffix[1:]
#     current_dir = get_current_directory()
#     for full_path in sorted(current_dir.glob(f"*.{suffix}")):
#         file_name = Path(current_dir / full_path.name)
#         print(f"\n\nOpening <{file_name.name}> to create pedigree...\n")
#         return file_name


# def create_db_from_file(source_file):
#     raw_cats = create_pedigree_from_file(source_file)
#     id_from_name = {cat['name']: id for id, cat in raw_cats.items()}
#     return(sub_names_to_ids(raw_cats, id_from_name), id_from_name)

# def create_list_from_file(source_file):
#     id_count = 1
#     loaded_cats = {}
#     num_of_fields = 11
#     with source_file.open(mode="r", encoding="utf-8") as f:
#         # tmp_deck = {}
#         for line, curr_line in enumerate(f):
#             if len(curr_line.strip()) == 0:
#                 print("Field missing at line:",line)
#             elif curr_line[0] == "#":
#                 print("comment at line:", line)
#             else:
#                 # entry = curr_line.split(",")
#                 entry = [field.strip() for field in curr_line.split(",")]
#                 if entry[0].lower() == "name":
#                     continue
#                 if len(entry) == num_of_fields:
#                     # loaded_cats.append({
#                     cat = {
#                         id_count : {
#                         "name": entry[0],
#                         "gems": entry[1],
#                         "sex": entry[2],
#                         "gccf": entry[3],
#                         "regnum": entry[4],
#                         "dob": entry[5],
#                         "cstatus": entry[6],
#                         "sire": entry[7],
#                         "dam": entry[8],
#                         "breeder": entry[9],
#                         "owner": entry[10],
#                         }}
#                         # })
#                     loaded_cats.update(cat)
#                     id_count += 1
#                 else:
#                     print("Field missing at line:",line)
#     loaded_cats.update(add_unknown())
#     return loaded_cats


# def update_dict(key,val, dict):
#     if dict.get(key):
#         # dict[key].append(val)
#         dict[key].insert(0,val)
#     else:
#         dict.update({key: [val]})
#     return dict


# def select_html_template(case, cat_id, pedigree, info):
#     if case < 0 or case > 5:
#         case = 5
#     switch = {
#         0: build_header,
#         1: build_gen1,
#         2: build_gen2,
#         3: build_gen3,
#         4: build_gen4,
#         5: build_gen5,
#         100: build_generic
#     }
#     func = switch.get(case)
#     return func(cat_id, pedigree, info)




# class Db:
#     def __init__(self):
#         self.lemmas = create_list_from_file(retrieve_file_by_suffix())

def read_in_data(source_file):
    with source_file.open(mode="r", encoding="utf-8") as f:
        lines = []
        for line, curr_line in enumerate(f):
            # if line >= 1500:
            #     break
            if len(curr_line.strip()) == 0:
                continue
            #     print("Field missing at line:",line)
            # elif curr_line[0] == "#":
            #     print("comment at line:", line)
            else:
                # curr_line = curr_line.strip()
                # curr_line = curr_line.replace("\n", " ")
                # curr_line = curr_line.replace("  ", " ")
                # curr_line = curr_line.replace("\"", "'")
                curr_line = curr_line \
                    .replace("\n", " ") \
                    .replace("  ", " ") \
                    .replace("\"", "'")
                # curr_line = curr_line.replace("á", "a")
                lines.append(curr_line.strip())
        return lines

def group_lines(lines, max_group_index=3):
    tmp_lines = []
    group = ""
    countdown = max_group_index
    for line in lines:
        group += line + "@"
        if countdown == 0:
            # print(">>", group[:-1])
            tmp_lines.append(group[:-1])
            group = ""
            countdown = max_group_index
            continue
        countdown -= 1
    return tmp_lines

def associate_lines_correctly(lines):
    tmp_lines = []
    to_add = []
    unit_num = 0
    for line in lines:
        if line[0] == "#":
            unit_num = line[7:]
        else:
            lemma1, lemma2, gloss1, gloss2 = line.split("@")
            to_add = [[lemma1, gloss1, unit_num], [lemma2, gloss2, unit_num]]
            tmp_lines.extend(to_add)
    return tmp_lines

def remove_dummies(lines):
    tmp_lines = []
    for line in lines:
        if line[0][0:5] == "dummy":
            continue
        tmp_lines.append(line)
    return tmp_lines


def add_ids(lines):
    tmp_lines = []
    for id, line in enumerate(lines):
        tmp = [id]
        tmp.extend(line)
        tmp_lines.append(tmp)
    return tmp_lines

def remove_stress_markers(lines):
    stress = {
"á": "a",
"é": "e",
"ú": "u",
"ó": "o",
"ḗ": "ē",
}
    tmp_lines = []
    for line in lines:
        # print(line)
        tmp_line = line.copy()
        tmp_line[1] = transform_macrons(tmp_line[1], stress)
        tmp_lines.append(tmp_line)
    return tmp_lines

def macrons_to_colons(lines):
    expand_macrons = {
"ā": "a:",
"ē": "e:",
"ī": "i:",
"ō": "o:",
"ū": "u:",
    }
    tmp_lines = []
    for line in lines:
        # print(line)
        tmp_line = line.copy()
        tmp_line[1] = transform_macrons(tmp_line[1], expand_macrons)
        tmp_lines.append(tmp_line)
    return tmp_lines

def add_plaintext_lemma(lines):
    kill_macrons = {
"ā": "a",
"ē": "e",
"ī": "i",
"ō": "o",
"ū": "u",
    }
    tmp_lines = []
    for line in lines:
        tmp_line = line.copy()
        tmp_lemma = line[1].replace(":","").replace(",", "")
        tmp_lemma = transform_macrons(tmp_lemma,kill_macrons)
        tmp_line.insert(1, tmp_lemma)
        tmp_lines.append(tmp_line)
    return tmp_lines

def transform_macrons(line, lookup):
    tmp_line = ""
    for char in line:
        new_char = ""
        replacement = lookup.get(char)
        if replacement:
            new_char = replacement
        else:
            new_char = char
        tmp_line += new_char
    return tmp_line

def add_macrons(line):
    contract_macrons = {
"a": "ā",
"e": "ē",
"i": u"ī",
"o": "ō",
"u": "ū",
    }
    tmp = ""
    tmp_line = line.split(":")
    for part in tmp_line:
        if part[-1:] in ["a", "e", "i", "o", "u"]:
            part = part[:-1] + contract_macrons[part[-1:]]
        tmp += part
    return tmp

def parse_cmd_line(argv):
    ids = ""
    ## Change these three variables according to needs
    id_list = [1,2,3,4]
    depth = 5
    basefont = 12

    opts, _ = getopt.getopt(argv,"hi:d:s:",["help","ids=", "depth=", "size="])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print ("""
You can specify the following variables after pedigrees.py
    -h / --help=    <prints this help message>
    -i / --ids=     <comma-separated list of cat ids (NO SPACES)>
                        e.g. -i 2,27 OR --ids=2,27
    -d / --depth=   <depth of generations (4 or 5 is best)>
                        e.g -d 5 OR --depth=5
    -s / --size=    <font size of grid in points (12 is default)>
                        e.g. -s 11 OR --size=11

To print out, use your browser to save or export this file as a pdf.
N.B. There must be ONE .csv file (cat database) in the same folder as this script.
""")
            sys.exit()
        elif opt in ("-i", "--ids"):
            ids = arg
            id_list = [int(id) for id in ids.split(",")]
        elif opt in ("-d", "--depth"):
            depth = int(arg)
        elif opt in ("-s", "--size"):
            basefont = int(arg)
    return(id_list, basefont, depth)

def main(argv):
    # settings = dict(zip(("to_print", "font_size", "depth"), parse_cmd_line(argv)))
    # db = Db()
    db = read_json()
    # search_for = argv[0:1]
    LATIN_PLAIN = 0
    LATIN_DISPLAY = 1
    ENGLISH = 2
    CHAPTER = 3
    while True:
        print("\nquid vultis quaerere? (:q - quit, :e - English)")
        search_for = input()
        language = LATIN_PLAIN
        if search_for.startswith(":q"):
            break
        elif search_for.startswith(":e"):
            language = ENGLISH
            search_for = search_for[2:].strip()
        matches = []
        term = f"^{search_for.lower()}.*"
        print(">>>>", term)
        matches = [id for id,entry in db.items() if re.search(term, entry[language])]
        if not matches:
            term = f"{search_for.lower()}.*"
            matches = [id for id,entry in db.items() if re.search(term, entry[language])]

        for n, id in enumerate(matches):
            entry = db[id]
            # print(f"\t{col.fg.blue}{n + 1}. {col.fg.pink}{entry[1]} {col.reset}<{entry[2]}> {col.fg.darkgrey}from unit {col.fg.lightblue}{entry[3]}{col.reset}")
            print(f"\t{n + 1}. {entry[1]} <{entry[2]}> from unit {entry[3]}")



if __name__ == "__main__":
    main(sys.argv[1:])

