#!/usr/bin/env python3
"""
add in row dividers where necessary

json markup assumes:
in notes:
single quotes used for apostrophes
double quotes used for quotes
<...> signifies Latin

in tables:
: means 'macron'
empty cells are marked by %
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
    """Colors class:reset all colors with colors.reset; two
    sub classes fg for foreground and bg for background; use as colors.subclass.colorname.
    i.e. colors.fg.red or colors.bg.green also, the generic bold, disable,
    underline, reverse, strike through, and invisible work with the main class i.e. colors.bold
    """

    reset = "\033[0m"
    bold = "\033[01m"
    disable = "\033[02m"
    underline = "\033[04m"
    reverse = "\033[07m"
    strikethrough = "\033[09m"
    invisible = "\033[08m"

    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    orange = "\033[33m"
    blue = "\033[34m"
    purple = "\033[35m"
    cyan = "\033[36m"
    lightgrey = "\033[37m"
    darkgrey = "\033[90m"
    lightred = "\033[91m"
    lightgreen = "\033[92m"
    yellow = "\033[93m"
    lightblue = "\033[94m"
    pink = "\033[95m"
    lightcyan = "\033[96m"

    class bg:
        black = "\033[40m"
        red = "\033[41m"
        green = "\033[42m"
        orange = "\033[43m"
        blue = "\033[44m"
        purple = "\033[45m"
        cyan = "\033[46m"
        lightgrey = "\033[47m"


class Db:
    def __init__(self, vocab, tables, label_lookup={}, lang="uk") -> None:
        self.vocab = vocab
        self.tables = tables
        self.label_lookup = label_lookup
        self.lang = lang
        self.latin_plain = 0
        self.latin_macron = 1
        self.english = 2
        self.chapter = 3


class Result:
    def __init__(self, db):
        self.term = ""
        self.error = ""
        self.matches = []
        self.tables = []
        self.language = 0
        self.prev = self.Prev()
        self.db = db

    def __repr__(self) -> str:
        return f"m:{self.matches}, {self.tables}\npm:{self.prev.matches}, {self.prev.tables}"

    class Prev:
        def __init__(self):
            self.matches = []
            self.tables = []

    def update(self, latest_matches):
        self.prev.matches = self.matches
        self.prev.tables = self.tables
        self.matches = latest_matches
        if latest_matches:
            self.tables = self.get_tables_only(latest_matches)
        else:
            self.error = f"No matches found for <*<*{self.term}*>*>.{col.reset}"
            self.tables = []
        return self

    def show_error(self, err=col.red, hi=col.reset):
        msg = self.error.replace("*<*", hi).replace("*>*", err)
        print(err + msg + hi)

    def set_language(self, lang_code="la"):
        if lang_code.startswith("la"):
            # self.language = 0
            self.language = self.db.latin_plain
        else:
            # self.language = 2
            self.language = self.db.english
        return self

    def get_language(self):
        # if self.language == 0:
        if self.language == self.db.latin_plain:
            return "la"
        else:
            return "en"

    # def count_tables(self, o):
    #     return len(o.matches) - len(o.tables) + 1

    def get_tables_only(self, matches):
        return [x for x in matches if x.startswith("t")]


def get_current_directory():
    return Path(__file__).parent.absolute()


def read_json(filename="latin.json"):
    json_file_address = Path(get_current_directory() / filename)
    with open(json_file_address, "r") as f:
        return json.load(f)


def draw_table(id, db):
    """
    In a standard table, the ["data"] consists of a list
    of undifferentiated rows

    but if the second row contains "nom / acc. dat" then convert it
    into a dictionary with the cases as keys
    to allow display in either uk or us system
    """
    table = db.tables[id]
    draw_table_title(table.get("title"))
    draw_table_notes(table.get("notes_pre"))
    table_data = [[colour_final(td) for td in row] for row in table.get("data")]
    if second_row_begins_with_label(table_data):
        table_data = convert_to_labelled_table(table_data, db)
        draw_labelled_table(table_data, db)
    else:
        invoke_tabulate(table_data)
    draw_table_notes(table.get("notes_post"))


def second_row_begins_with_label(table_rows):
    second_row = "".join(table_rows[1]).strip()
    second_row = (
        second_row.replace("[", "").replace("]", "").replace("%", "").replace(" ", "")
    )
    # tmp = "".join(table_rows[1]).strip()[:3].lower()
    return second_row[:3].lower() in ["nom", "voc", "acc", "gen", "dat"]


def convert_to_labelled_table(table, db):
    tmp = {}
    backup_label = "misc"
    for row in table:
        label = ""
        heading = "".join(row[:2]).strip()
        heading = heading.lower()[:3]
        if heading:
            label = db.label_lookup.get(heading)
        if label:
            backup_label = label
        else:
            label = backup_label
        if label in tmp:
            tmp[label].append(row)
        else:
            tmp[label] = [row]
    return tmp


def draw_labelled_table(table, db):
    """
    In a labelled table, the ["data"] is a dictionary;
    each entry is a labelled row (e.g. 'nom', 'gender').
    These can then be displayed in any order,
    i.e. UK (nom, voc, acc, ...) vs US (nom, gen, dat)
    """
    ordering = {
        "uk": [
            "number",
            "gender",
            "nom",
            "voc",
            "acc",
            "gen",
            "par",
            "dat",
            "abl",
            "misc",
        ],
        "us": [
            "number",
            "gender",
            "nom",
            "gen",
            "par",
            "dat",
            "acc",
            "abl",
            "voc",
            "misc",
        ],
    }
    tmp = []
    for key in ordering[db.lang]:
        row = table.get(key)
        if row:
            for entry in row:
                # if key == "nom":
                #     tmp.append(SEPARATING_LINE)
                tmp.append(entry)
    invoke_tabulate(tmp)


def invoke_tabulate(data):
    print(
        tabulate(
            data, headers="firstrow", tablefmt="fancy_outline", colalign=("right",)
        )
    )


def draw_table_title(title):
    if title:
        prefix = "§ "
        print(" ")
        print(f"{prefix}{col.bold}{col.orange}{title}{col.reset}")
        print("=" * len(prefix + title))


def draw_table_notes(notes):
    for note in notes:
        chunked_note = chunk_note(note)
        for line in chunked_note:
            # print(line)
            print(f"{col.reset}{colour_final(line,False)}{col.reset}")
        print(" ")

def chunk_note(note):
    indent = 4
    chunked_lines = [line for line in chunk(colour_pre(note), 70, indent, [])]
    ## include previous markup status to catch lines
    # that contain no markup because they run on from previous
    prev_status = 0
    for quote_type in [("<",">"), ("{","}")]:
        tmp = []
        for line in chunked_lines:
            line, prev_status = terminate_quote(line, quote_type, prev_status)
            tmp.append(line.rstrip())
        chunked_lines = tmp
    return chunked_lines


def chunk(line, limit=70, indent=6, sublines=[]):
    """
    Takes a long string and then divides it into lines
    at spaces (where possible) with a maximum line length.
    Applies an indent to all but the first line.
    """
    ## Don't indent first line
    end = limit
    spacer = ""
    if sublines:
        end = limit - indent
        spacer = " " * indent
    if len(line) <= end:
        sublines.append(spacer + line)
        return sublines
    subline = line[:end]
    if subline[-1] != " ":
        tmp = subline.rfind(" ")
        if tmp > -1:
            end = tmp
            subline = line[:end]
    sublines.append(spacer + subline)
    line = line[end:].lstrip()
    chunk(line, limit, indent, sublines)
    return sublines


def terminate_quote(line, q, prev_status):
    """
    Strips off any indent spacing (for neatness),
    restores broken quote sequences,
    adds back indent
    """
    acc = line.count(q[0]) - line.count(q[1])
    old_len = len(line)
    line = line.lstrip()
    spacer = " " * (old_len - len(line))
    if acc == -1:
        line = q[0] + line
    elif acc == 1:
        line = line + q[1]
    elif acc == 0 and prev_status == 1:
        line = q[0] + line + q[1]
    return (spacer + line, acc)


def colour_pre(line):
    """
    This works along with colour_final() to convert simple markup
    into colors: "..." is transformed into "{...}" in this first pass
    To prevent the long command line colour codes disturbing
    the line-length count, this translation from " to { or}
    must be done before the lines are split in chunk_line()
    """
    quotes = line.split('"')
    tmp = ""
    for num, quote in enumerate(quotes):
        sub = ["{", "}"] if num % 2 else ["", ""]
        # print(num, num % 2, sub, sub[0] + quote + sub[1])
        tmp += sub[0] + quote + sub[1]
    return tmp


def colour_final(line, are_titles=True, reset=col.reset):
    latin = col.red
    english = col.green
    titles = col.blue
    """
    This continues on from colour_pre() or can stand alone
    """
    if are_titles:
        line = line.replace("[", titles).replace("]", col.reset)
    line = line.replace("<", latin).replace(">", reset)
    line = line.replace("{", english).replace("}", col.reset)
    return line


def print_entry(entry, result, num):
    db = result.db
    if result.language == db.latin_plain:
        lemma = entry[db.latin_macron]
        gloss = colour_final(entry[db.english])
    else:
        lemma = colour_final(entry[db.english])
        gloss = entry[db.latin_macron]
    # gloss = 0 if lemma else 2
    num_prefix = ""
    if num >= 0:
        num_prefix = f"{col.blue}{num + 1}. "
    print(
        f"\t{num_prefix}{col.pink}{lemma} {col.reset}{col.bold}{gloss} {col.darkgrey}from chapter {col.lightblue}{entry[3]}{col.reset}"
    )


def search_db(term, language, db):
    return [id for id, entry in db.vocab.items() if re.search(term, entry[language])]


def build_match_list(result):
    db = result.db
    term = result.term
    prefix = term[:2]
    # if prefix == "e:":
    if prefix in ["e:", "x:"]:
        result.set_language("en")
        term = term[2:]
        if prefix == "x:":
            term = term + "\\b"
    else:
        result.set_language("la")
    search_string = f"\\b{term}"
    matches = search_db(search_string, result.language, db)
    # if not matches:
    #     search_string = term
    #     matches = search_db(search_string, result.language, db)
    if prefix == "x:":
        result.set_language("la")
        matches.extend(search_db(search_string, result.language, db))
    if matches:
        matches.sort()
    return matches


def display_menu(result):
    base_menu = f"\n\n{col.purple}quid est quaerendum? {col.green}(*<*:q*>*[uit], *<*:e*>*[nglish], e*<*:x*>*act word"
    extended_menu = ")"
    menu_choices = ""
    if len(result.prev.matches):
        extended_menu = ", *<*:r*>*[epeat]"
        if len(result.prev.tables) > 1:
            start_index = len(result.prev.matches) - len(result.prev.tables)
            end_index = len(result.prev.matches) - 1
            extended_menu += ", or "
            menu_choices = f"*<*{start_index + 1}"
            if start_index < end_index:
                menu_choices += f"*>* to *<*{end_index + 1}"
        extended_menu = f"{extended_menu}{menu_choices}*>*)"
    msg = f"{base_menu}{extended_menu}*<*".replace("*<*", col.reset).replace(
        "*>*", col.green
    )
    print(msg)
    return menu_choices


def check_numeric_entry(result, menu_choices):
    action = ""
    error = ""
    if result.prev.matches:
        id_in_prev = int(result.term) - 1
        if 0 <= id_in_prev < len(result.prev.matches) and result.prev.matches[
            id_in_prev
        ].startswith("t"):
            table_id = result.prev.matches[id_in_prev]
            action = f"display:{table_id}"
        else:
            error = f"Enter *<*{menu_choices}*>* or a new term."
            action = "continue"
    else:
        error = "Enter a word to search for."
        action = "continue"
    return (action, error)


def check_input(result, menu_choices):
    result.error = ""
    action = ""
    if not result.term:
        result.error = "Quid facis?? Please input a latin word."
        action = "continue"
    elif result.term.isnumeric():
        action, result.error = check_numeric_entry(result, menu_choices)
    else:
        result.term = result.term.lower()
        prefix = result.term[:2]
        if prefix in [":q", "q:", "qq"]:
            action = "quit"
        elif prefix in [":r", "r:", "rr"]:
            action = "repeat"
        # elif prefix in [":e", "e:", "ee"]:
        elif prefix in [":e", "e:", "ee", ":x", "x:", "xx"]:
            prefix = "e:" if "e" in prefix else "x:"
            suffix = result.term[2:]
            if suffix:
                result.term = prefix + suffix
                action = "search"
            else:
                result.error = "Add an English term to search for."
                action = "continue"
        else:
            action = "search"
    return action


def display_results(result):
    if result.matches:
        for num, id in enumerate(result.matches):
            entry = result.db.vocab[id]
            if len(result.tables) == 1 and id == result.tables[0]:
                draw_table(id, result.db)
            else:
                print_entry(entry, result, num)
    else:
        result.show_error()


def update_and_display(matches, result):
    result.update(matches)
    display_results(result)
    result.update([])


def create_db(lang):
    return Db(
        {**read_json("wheelock_vocab.json"), **read_json("table_entries.json")},
        read_json("tables.json"),
        {
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
        },
        lang,
    )


def parse_cmd_line(argv):
    lang = ""
    opts, _ = getopt.getopt(argv, "hl:", ["help", "lang=", "language="])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                """
You can specify the following variables after pedigrees.py
    -h / --help=                <prints this help message>
    -l / --lang= / --language=  <us / uk style of listing noun cases>
                                uk: nom, acc, gen, dat, abl
                                us: nom, gen, dat, acc, abl
                                e.g. -l us OR --lang=us
"""
            )
            sys.exit()
        elif opt in ("-l", "--lang", "--language"):
            lang = arg.lower()
    if not lang.startswith("us"):
        lang = "uk"
    return lang


def main(argv):
    lang = parse_cmd_line(argv)
    db = create_db(lang)
    result = Result(db)
    while True:
        menu_choices = display_menu(result)
        result.term = input().strip()
        match check_input(result, menu_choices):
            case "quit":
                quit()
            case "continue":
                # print(result.error)
                result.show_error()
            case str() as action if action.startswith("display"):
                table_id = action.split(":")[1]
                # draw_table(table_id, db.tables[table_id])
                draw_table(table_id, db)
            case "repeat":
                update_and_display(result.prev.matches, result)
            case "search":
                update_and_display(build_match_list(result), result)
            case _:
                print("Houston, we have a problem...")


if __name__ == "__main__":
    main(sys.argv[1:])
