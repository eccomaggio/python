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

def build_match_list(term, language, db):
    return [id for id,entry in db.items() if re.search(term, entry[language])]

def main():
    db = read_json("wheelock_vocab.json")
    LATIN_PLAIN = 0
    LATIN_DISPLAY = 1
    ENGLISH = 2
    CHAPTER = 3
    while True:
        print(f"\n\n{col.fg.lightred}quid vultis quaerere?{col.fg.green} (:q - quit, :e - English){col.reset}")
        search_for = input()
        language = LATIN_PLAIN
        display_search = LATIN_DISPLAY
        display_result = ENGLISH

        if search_for.startswith(":q") or search_for.startswith("qq"):
            break
        elif search_for.startswith(":e") or search_for.startswith("e:"):
            language = ENGLISH
            display_search, display_result = display_result, display_search
            search_for = search_for[2:].strip()
        matches = []
        term = f"^{search_for.lower()}"
        matches = build_match_list(term, language, db)
        if not matches:
            term = f"{search_for.lower()}"
            matches = build_match_list(term, language, db)
        # print(">>>>", term, language)

        for n, id in enumerate(matches):
            entry = db[id]
            print(f"\t{col.fg.blue}{n + 1}. {col.fg.pink}{entry[display_search]} {col.reset}{col.bold}{entry[display_result]} {col.fg.darkgrey}from chapter {col.fg.lightblue}{entry[CHAPTER]}{col.reset}")



if __name__ == "__main__":
    main()

