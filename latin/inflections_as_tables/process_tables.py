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
from tabulate import tabulate, SEPARATING_LINE

tabulate.PRESERVE_WHITESPACE = True





def get_current_directory():
    return Path( __file__ ).parent.absolute()


def write_json_file(lines, filename="out.json"):
    json_file_address = Path(get_current_directory() / filename)
    with open(json_file_address, "w") as f:
        json.dump(lines,f)


def retrieve_file_by_suffix(suffix="csv"):
    if suffix[0] == ".":
        suffix = suffix[1:]
    current_dir = get_current_directory()
    for full_path in sorted(current_dir.glob(f"*.{suffix}")):
        file_name = Path(current_dir / full_path.name)
        print(f"\n\nOpening <{file_name.name}> to create pedigree...\n")
        return file_name

def retrieve_file_by_name(filename):
    current_dir = get_current_directory()
    file = Path(current_dir / filename)
    return file


def read_in_data(source_file, id_count):
    with source_file.open(mode="r", encoding="utf-8") as f:
        tables = []
        table = {}
        # id_count = 0
        for line_num, curr_line in enumerate(f):
            # if line_num >= 52:
            #     break
            if len(curr_line.strip()) == 0:
                continue
            #     print("Field missing at line:",line)
            elif curr_line.startswith("#"):
                print("comment at line:", line_num)
                continue
            elif curr_line.startswith("@"):
                table["cols"] += 1
                continue
            elif curr_line.startswith("&"):
                if table:
                    tables.append(table.copy())
                word_class, subtype, table_type = curr_line[1:].strip().split(":")

                table = {
                    "id": id_count,
                    # "desc": curr_line[1:].strip(),
                    "word_class": word_class,
                    "subtype": subtype,
                    "table_type": table_type,
                    "titles": [],
                    "cols": 0,
                    "data": []
                }
                id_count += 1
            # elif skip_table:
            #     continue
            elif curr_line.startswith("*"):
                table["titles"].append(curr_line[1:])

            else:
                curr_line = curr_line.replace("  ", "\t")
                curr_line = add_macrons(curr_line)
                table_row = curr_line.strip().split("\t")
                table_row = [" " if el == "%" else el for el in table_row]
                table["data"].append(table_row)
        tables = convert_by_col_to_by_row(tables)
        return (tables, id_count)

def convert_by_col_to_by_row(tables):
    """
    Noun tables are arranged by row, but many verb tables
    are arranged by col. This converts verb tables into
    by-column format.
    """
    for table in tables:
        if table["cols"]:
            cols = table["cols"]
            col_max = int(len(table["data"]) / cols)
            raw_data = [x[0] for x in table["data"]]
            data = [
                # table["data"][int(i * col_max) : int((i + 1) * col_max)]
                raw_data[int(i * col_max) : int((i + 1) * col_max)]
                for i in range(cols)
            ]
            table["data"] = list(zip(*data))
    return tables


def remove_dummies(lines):
    tmp_lines = []
    for line in lines:
        if line[0][0:5] == "dummy":
            continue
        tmp_lines.append(line)
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

def draw_table(table):
    """
    In a standard table, the ["data"] consists of a list
    of undifferentiated rows
    """
    print(f"\nid: {table['id']}")
    for title in table["titles"]:
        print(title)
    # print(tabulate(table["data"], headers="firstrow", tablefmt="fancy_outline", colalign=("right",)))
    print(tabulate(table["data"], headers="firstrow", tablefmt="fancy_outline"))

def draw_labelled_table(table, order="uk"):
    """
    In a labelled table, the ["data"] is a dictionary;
    each entry is a labelled row (e.g. 'nom', 'gender').
    These can then be displayed in any order,
    i.e. UK (nom, voc, acc, ...) vs US (nom, gen, dat)
    """
    order = order.lower()
    if order != "uk":
        order = "us"
    ordering = {
        "uk": ["number", "gender", "nom", "voc", "acc", "gen", "par", "dat", "abl", "misc"],
        "us": ["number", "gender", "nom", "gen", "par", "dat", "acc", "abl", "voc", "misc"],
    }
    print(f"\nid: {table['id']}")
    for title in table["titles"]:
        print(title)
    tmp = []
    for key in ordering[order]:
        row = table["data"].get(key)
        if row:
            for entry in row:
                # if key == "nom":
                #     tmp.append(SEPARATING_LINE)
                tmp.append(entry)
    print(tabulate(tmp, headers="firstrow", tablefmt="fancy_outline", colalign=("right",)))

def label_nouns(tables):
    tmp_tables = []
    label_lookup = {
        "nom": "nom",
        "voc": "voc",
        "acc": "acc",
        "gen": "gen",
        "part": "par",
        "dat": "dat",
        "abl": "abl",
        "mas": "gender",
        "fem": "gender",
        "neu": "gender",
        "sin": "number",
        "plu": "number",
    }
    for table in tables:
        tmp = table.copy()
        tmp["data"] = {}
        backup_label = "misc"
        # count = 0
        for row in table["data"]:
            # print("test:",row[:2], row)
            label = ""
            heading = "".join(row[:2]).strip()
            heading = heading.lower()[:3]
            if heading:
                label = label_lookup.get(heading)
            if label:
                backup_label = label
            else:
                label = backup_label
            if label in tmp["data"]:
                tmp["data"][label].append(row)
            else:
                tmp["data"][label] = [row]
        tmp_tables.append(tmp)
    return tmp_tables







def main():
    files = ["nouns","pronouns", "adjectives", "adverbs", "verbs", "numbers"]
    id_count = 0
    all_tables = []
    for file_name in files:
        tables, id_count = read_in_data(retrieve_file_by_name(f"{file_name}.csv"),id_count)
        write_json_file(tables, f"{file_name}.json")
        for table in tables:
            all_tables.append(table)
    # pprint(all_tables)
    for table in all_tables:
        draw_table(table)

    # for table in tables_labelled:
    #     draw_labelled_table(table)




if __name__ == "__main__":
    main()

