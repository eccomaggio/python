"""
todo:
make a class Result:
.search_term
.matches
.prev_matches
.language .search_lang .result_lang
.matched_tables
.prev_matched_tables
.error_msg

and

class Db:
.vocab
.tables

and

add in row dividers where necessary
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

def draw_table(id, table):
    """
    In a standard table, the ["data"] consists of a list
    of undifferentiated rows
    """
    # print(f"\nid: {id}", table)
    print(table.get("title"))
    for note in table["notes"]:
        print(note)
    # print(tabulate(table["data"], headers="firstrow", tablefmt="fancy_outline", colalign=("right",)))
    print(tabulate(table["data"], headers="firstrow", tablefmt="fancy_outline"))

def draw_labelled_table(id, table, order="uk"):
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
    # print(f"\nid: {id}")
    print(table["title"])
    for title in table["notes"]:
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


def search_db(term, language, db):
    return [id for id,entry in db.items() if re.search(term, entry[language])]

def build_match_list(term, language, db):
    term = term.lower()
    search = f"\b{term}"
    matches = search_db(search, language, db)
    if not matches:
        search = f"{term}"
        matches = search_db(search, language, db)
    return matches



def main():
    LATIN_PLAIN = 0
    LATIN_DISPLAY = 1
    ENGLISH = 2
    CHAPTER = 3
    green = col.fg.green
    pink = col.fg.pink
    blue = col.fg.blue
    lblue = col.fg.lightblue
    dgrey = col.fg.darkgrey
    bold = col.bold
    x = col.reset

    db = read_json("wheelock_vocab.json")
    table_entries = read_json("table_entries.json")
    db = {**db, **table_entries}
    tables = read_json("tables.json")

    prev_results = []
    while True:
        menu = f"\n\n{col.fg.lightred}quid est quaerendum? {green}({x}:q{green}[uit], {x}:e{green}[nglish]"
        # range = ""
        # have_tables = len(prev_results) - len([x for x in prev_results if x.startswith("t")]) + 1
        prev_result_tables = [x for x in prev_results if x.startswith("t")]
        had_tables = len(prev_results) - len(prev_result_tables) + 1
        end_range = len(prev_results)
        if had_tables <= end_range:
            menu = f"{menu}, {x}:r{green}[epeat], or "
            if had_tables == end_range:
                choices = f"{x}{end_range}{green}"
            else:
                choices = f"{x}{had_tables}{green} to {x}{end_range}{green}"
            menu = f"{menu}{choices}"
        print(f"{menu}){x}")
        # print(matches,prev_results)
        search_for = input().strip()
        language = LATIN_PLAIN
        display_search = LATIN_DISPLAY
        display_result = ENGLISH

        matches = []
        error_msg = ""
        if not search_for:
            # error_msg = "Quid facis?? Please input a latin word."
            print("Quid facis?? Please input a latin word.")
            continue
        if search_for.isnumeric():
            if prev_results:
                id_in_prev = int(search_for) - 1
                if id_in_prev >= 0 and id_in_prev < end_range:
                    table_id = prev_results[id_in_prev]
                    table = tables.get(table_id)
                    if table:
                        draw_table(table_id, table)
                        continue
                error_msg = f"{green}Enter {choices} or a new term."
            else:
                error_msg = "Enter a word to search for."
            print(error_msg)
            continue
        else:
            prefix = search_for[:2]
            if prefix in [":q", "q:", "qq"]:
                break
            elif prefix in [":r", "r:", "rr"]:
                matches = prev_results
            elif prefix in [":e", "e:", "ee"]:
                language = ENGLISH
                display_search, display_result = display_result, display_search
                search_for = search_for[2:].strip()

        if not matches:
            matches = build_match_list(search_for, language, db)
        if matches:
            result_tables = [x for x in matches if x.startswith("t")]
            # print("debug:", result_tables, len(result_tables), result_tables[0])
            for n, id in enumerate(matches):
                entry = db[id]
                # if len(matches) == 1 and entry[CHAPTER] == "table":
                if len(result_tables) == 1 and id == result_tables[0]:
                    draw_table(id, tables[id])
                else:
                    print(f"\t{blue}{n + 1}. {pink}{entry[display_search]} {x}{bold}{entry[display_result]} {dgrey}from chapter {lblue}{entry[CHAPTER]}{x}")
            prev_results = matches
        else:
            if not error_msg:
                error_msg = f"No matches for <{search_for}>"
        if error_msg:
            print(error_msg)



if __name__ == "__main__":
    main()

