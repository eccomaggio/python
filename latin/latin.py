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
    db = read_json("wheelock_vocab.json")
    table_entries = read_json("table_entries.json")
    # db.update(table_entries)
    db = {**db, **table_entries}
    tables = read_json("tables.json")
    LATIN_PLAIN = 0
    LATIN_DISPLAY = 1
    ENGLISH = 2
    CHAPTER = 3
    previous_choices = []
    while True:
        matches = []
        menu_choices = ""
        choices_with_table = [x for x in previous_choices if x.startswith("t")]
        if len(choices_with_table):
            # menu_choices = f", :r[epeat], or "
            # options = len(previous_choices) - len(choices_with_table) + 1
            # print(">>",options)
            # if options == 1:
            #     menu_choices += f"{len(previous_choices)}"
            # else:
            #     menu_choices += f"{len(previous_choices) - len(choices_with_table) + 1} to {len(previous_choices)}."
            menu_choices = f", :r[epeat], or {len(previous_choices) - len(choices_with_table) + 1} to {len(previous_choices)}."
        print(f"\n\n{col.fg.lightred}quid est quaerendum?{col.fg.green} (:q[uit], :e[nglish]{menu_choices}){col.reset}")
        search_for = input().strip()
        language = LATIN_PLAIN
        display_search = LATIN_DISPLAY
        display_result = ENGLISH

        if not search_for:
            print("Quid facis?? Please input a latin word.")
        if search_for.isnumeric() and previous_choices:
            chosen_result = int(search_for) - 1
            # print("debug choice", previous_choices, int(search_for), previous_choices[chosen_result])
            if chosen_result >=0 and chosen_result < len(previous_choices):
                table_id = previous_choices[chosen_result]
                # chosen_table = tables[table_id]
                chosen_table = tables.get(table_id)
                if chosen_table:
                    draw_table(table_id, chosen_table)
                    continue
                else:
                    print("Sorry. No table associated with this entry.")
            print("Enter an ID from the previous search or a new term.")
        elif search_for.startswith(":q") or search_for.startswith("qq"):
            break
        elif search_for.startswith(":r"):
            matches = previous_choices

        elif search_for.startswith(":e") or search_for.startswith("e:"):
            language = ENGLISH
            display_search, display_result = display_result, display_search
            search_for = search_for[2:].strip()

        if not matches:
            matches = build_match_list(search_for, language, db)
        if matches:
            for n, id in enumerate(matches):
                entry = db[id]
                if len(matches) == 1 and entry[CHAPTER] == "table":
                    # draw_table(id, entry)
                    draw_table(id, tables[id])
                else:
                    print(f"\t{col.fg.blue}{n + 1}. {col.fg.pink}{entry[display_search]} {col.reset}{col.bold}{entry[display_result]} {col.fg.darkgrey}from chapter {col.fg.lightblue}{entry[CHAPTER]}{col.reset}")
            previous_choices = matches
        else:
            print(f"No matches for <{search_for}>")



if __name__ == "__main__":
    main()

