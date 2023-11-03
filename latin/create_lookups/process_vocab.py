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
import csv


def get_current_directory():
    return Path( __file__ ).parent.absolute()


def write_json_file(lines, filename="latin.json"):
    file_address = Path(get_current_directory() / filename)
    with open(file_address, "w") as f:
        json.dump(lines,f)

def read_csv_file(filename):
    tmp = []
    file_address = Path(get_current_directory() / filename)
    print(f"\n\nOpening <{file_address.name}> to create pedigree...\n")
    with open(file_address, "r") as f:
        csv_reader = csv.reader(f, delimiter='\t')
        for row in csv_reader:
            # print("csv:",row)
            tmp.append(row)
    return tmp



def write_csv_file(data, filename):
    file_address = Path(get_current_directory() / filename)
    with open(file_address, "w") as f:
        # csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer = csv.writer(f, delimiter="\t")
        csv_writer.writerows(data)



def retrieve_file_by_suffix(suffix="csv"):
    if suffix[0] == ".":
        suffix = suffix[1:]
    current_dir = get_current_directory()
    for full_path in sorted(current_dir.glob(f"*.{suffix}")):
        file_address = Path(current_dir / full_path.name)
        print(f"\n\nOpening <{file_address.name}> to create pedigree...\n")
        return file_address


# def parse_cmd_line(argv):
#     ids = ""
#     ## Change these three variables according to needs
#     id_list = [1,2,3,4]
#     depth = 5
#     basefont = 12

#     opts, _ = getopt.getopt(argv,"hi:d:s:",["help","ids=", "depth=", "size="])
#     for opt, arg in opts:
#         if opt in ("-h", "--help"):
#             print ("""
# You can specify the following variables after pedigrees.py
#     -h / --help=    <prints this help message>
#     -i / --ids=     <comma-separated list of cat ids (NO SPACES)>
#                         e.g. -i 2,27 OR --ids=2,27
#     -d / --depth=   <depth of generations (4 or 5 is best)>
#                         e.g -d 5 OR --depth=5
#     -s / --size=    <font size of grid in points (12 is default)>
#                         e.g. -s 11 OR --size=11

# To print out, use your browser to save or export this file as a pdf.
# N.B. There must be ONE .csv file (cat database) in the same folder as this script.
# """)
#             sys.exit()
#         elif opt in ("-i", "--ids"):
#             ids = arg
#             id_list = [int(id) for id in ids.split(",")]
#         elif opt in ("-d", "--depth"):
#             depth = int(arg)
#         elif opt in ("-s", "--size"):
#             basefont = int(arg)
#     return(id_list, basefont, depth)


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
            elif curr_line[0] == "*":
                print("comment at line:", line)
                continue
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
    """
    The Wheelock website codes vocab like this:
    lemma 1
    lemma 2
    gloss 1
    gloss 2

    This function unscrambles and creates two consecutive entries:
    lemma 1, gloss 1
    lemma 2, gloss 2
    """
    tmp_lines = []
    to_add = []
    unit_num = 0
    for line in lines:
        if line[0] == "#":
            unit_num = line[7:]
            # print(".........", unit_num)
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

def convert_to_dict(lines):
    return {line[0] : [line[1], line[2], line[3], line[4]] for line in lines}


# def main(argv):
def main():
    """
    Assumes
        EITHER
    ONE .txt file in the messy order created by
    cutting and pasting from the wheelock website
        OR
    'wheelock_vocab.csv in this format:
    accented latin, english gloss, chapter no => 'mē', 'me, myself', '1'

    """
    base_name = "vocab"
    csv_file = f"{base_name}.csv"
    # json_file = f"{base_name}.json"
    out_file = "wheelock_vocab.json"
    if Path(get_current_directory() / csv_file).exists():
        lines = read_csv_file(csv_file)
    else:
        lines = read_in_data(retrieve_file_by_suffix("txt"))
        lines = group_lines(lines)
        lines = associate_lines_correctly(lines)
        lines = remove_dummies(lines)
        write_csv_file(lines, csv_file)
    # print(lines)
    lines = add_ids(lines)
    lines = remove_stress_markers(lines)
    # lines = macrons_to_colons(lines)
    lines = add_plaintext_lemma(lines)
    # print(lines)
    # write_json_file({"data": lines})
    db = convert_to_dict(lines)
    write_json_file(db, out_file)
    # pprint(db)
    # print(add_macrons(db[42]))




if __name__ == "__main__":
    # main(sys.argv[1:])
    main()

