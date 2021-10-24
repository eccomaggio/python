"""
Takes a text file containing vocab: lemma_pinyin_gloss
parses it and adds extra information
saves it as a json file (expands to a 2-level dictionary:
decks > cards

Once the csv files have been added to the .json file, 
their names are added to an exclude file
this way, they won't be parsed next time. 
Delete ALL json files and clear the exclusion files to reload.

& the json files are used instead (unless fresh .csv files are added)

Subjective ranking: 0 none / 10 too easy (skip) /
20 difficult (prompt more) / 110 very difficult (prompt a lot!) / 
101  irrelevant (skip)

with thanks to https://stackabuse.com/read-a-file-line-by-line-in-python/ 

TODO
- make the recap work
- add in color
- make work with better display? (e.g. webserver or tkinter)
- make the skip work

ABANDONED - strip out dataclass as not crucial and a pain to serialize
change logic: 
    start: load in all_decks.json, then check for any new .csv's, move csv's to folder
    end: overwrite all_decks.json with updated version
"""

import random
from dataclasses import dataclass
import datetime as dt
import time
# import dateutil.parser
from pathlib import Path
import json
from json import JSONEncoder
import string
import math


"""
class Flashcard:
    lemma: str
    pinyin: entry[1],
    gloss: entry[2],
    ID: count,
    seq: count,
    added: datetime.datetime
    lastview: datetime.datetime
    title: str
    views: int
    rating: int
    ranking: int
    wrong: int
    skipped: int
"""

# OR import colorama for command line colors?
# class bcolors:
#     HEADER = '\033[95m'
#     BLUE = '\033[94m'
#     OKCYAN = '\033[96m'
#     OKGREEN = '\033[92m'
#     WARNING = '\033[93m'
#     FAIL = '\033[91m'
#     ENDC = '\033[0m'
#     BOLD = '\033[1m'
#     UNDERLINE = '\033[4m'


reset = "\u001b[0m"
blue = "\u001b[34m"
green = "\u001b[32m"
red = "\u001b[31m"

def save_json_deck(filename, flashcard_deck):
    with open(filename,"w") as new_deck:
        # saved_deck = json.dump(flashcard_deck, new_deck, cls=DateTimeEncoder)
        saved_deck = json.dump(flashcard_deck, new_deck)
        print(f"{red}>> json file ({filename.name}) saved.{reset}")

def retrieve_json_file(file):
    with open(file,"r") as f:
        return json.load(f)

def retrieve_json_decks(current_dir):
    tmp_decks = {}
    for saved_deck in current_dir.glob("*.json"):
        tmp_decks.update(retrieve_json_file(saved_deck))
        # with open(saved_deck, "r") as retrieved_deck:
            # tmp = json.load(retrieved_deck, object_hook=DecodeDateTime)
            # tmp = json.load(retrieved_deck)
            # first_card = list(tmp.keys())[0]
            # print(tmp[first_card])
            # print(tmp[first_card]["title"])
            # exit()
            # tmp_decks[tmp[first_card]["title"]] = tmp
            # tmp_decks.update(tmp)
    # for key in tmp_decks.keys():
    #     print (f">> {key}")
    return tmp_decks
        
def populate_exclusion_list(current_dir,files_to_exclude):
    tmp_set = set()
    with files_to_exclude.open(mode="r", encoding="utf-8") as f:
        for line in f:
            if line[0] == "#":
                # print("bit of a comment there...")
                pass
            elif len(line.strip()) == 0:
                # print("empty line")
                pass
            else:
                tmp = line.strip()
                if Path(current_dir / tmp).is_file():
                    # print(f"File <{tmp}> exists, the penguin be praised!")
                    tmp_set.add(tmp)
                else:
                    print(f"File <{tmp}> to exclude doesn't exist.")
    return tmp_set


def create_deck_from_file(source_file):
    # from a file, create as many decks as there are title lines (i.e. beginning with *
    # is_default_deck = True
    loaded_decks = {}
    deck_title = "undef"
    loaded_decks[deck_title] = {}
    # with open(source_file, "r", encoding="utf-8") as f:
    with source_file.open(mode="r", encoding="utf-8") as f:
        # tmp_deck = {}
        for line, curr_line in enumerate(f):
            if len(curr_line.strip()) == 0:
                # print("empty line")
                pass
            elif curr_line[0] == "*":
                deck_title = curr_line[1:].strip()
                loaded_decks[deck_title] = {}
            elif curr_line[0] == "#":
                # print("comment at line:", line)
                pass
            elif len(curr_line.strip()) > 0:
                entry = curr_line.split("_")
                if len(entry) == 3:
                    # print(entry)
                    # flashcards[entry[0]] = (entry[1],entry[2].strip())
                    # tmp_deck[entry[0]] = {
                    loaded_decks[deck_title][entry[0]] = {
                            "lemma": entry[0],
                            "pinyin": entry[1],
                            "gloss": entry[2].strip(),
                            "ID": line,
                            "seq": line,
                            "added": dt.datetime.now(dt.timezone.utc).isoformat(),
                            "lastview": "",
                            "title": deck_title,
                            "views": 0,
                            "rating": 0,
                            "ranking": 0,
                            "wrong": 0,
                            "skipped": 0
                            }
                           
                    # if line > 10: tmp_deck[-1].ranking = 101
                    # print(tmp_deck[entry[0]])
            else:
                print("Field missing at line:",line)

    # save_json_deck(Path.cwd() / f"{deck_title}.json", loaded_decks)
    # csv_dir = Path.cwd() / "csv_files"
    # if not csv_dir.exists():
    #     csv_dir.mkdir(mode=0o777,parents=False,exist_ok=False)
    # This line moves the files successfully (but temp disabled to help debugging)
    # source_file.replace(source_file.parent.joinpath("csv_files", source_file.name))

    # return [deck_title, tmp_deck]
    return loaded_decks

def main():
    all_decks = {}
    # current_dir = Path().cwd()
    current_dir = Path( __file__ ).parent.absolute()
    exclude_file = Path(current_dir / "exclude_these.txt")
    json_file = Path(current_dir / "all_decks.json")
    exclude_these = populate_exclusion_list(current_dir, exclude_file)
    user = "paul"

    # print (f">>>Files to exclude: {exclude_these}.")

    more_decks = retrieve_json_decks(current_dir)
    if more_decks: all_decks.update(more_decks)

    files_read = []
    for full_path in sorted(current_dir.glob("*.csv")):
        file_name = Path(full_path).name
        if file_name in exclude_these:
            # print(f"Cards in file <{file_name}> already loaded.")
            pass
        else:
            csv_decks = create_deck_from_file(full_path)
            files_read.append(file_name)
            tmp_decks = {key:val for key, val in csv_decks.items() if len(csv_decks[key]) > 0}
            all_decks.update(tmp_decks)

    ## Add newly read files to exclusion files
    ## They are now stored in the .json file
    if files_read:
        with open(exclude_file, "a") as f:
            for entry in files_read:
                f.write(f"{entry}\n")

    for deck in all_decks.keys():
        print(f"{deck} has {len(all_decks[deck])} entries.")

    ## Resave json file          
    save_json_deck(json_file,all_decks)

    hide_cards = True

    session = {
            # "layout": "a",
            "layout": {},
            "set": {},
            "skip": False,
            "shuffle" : False,
            "review": True,
            "user": user,
            }

    ## Decide layout of flashcards for this session
    query = (f"{blue}\n>\u001b[34m What prompt do you want to see? "
            f"{green}\nA: Show English first (default)"
            f"{green}\nB: Show pinyin first"
            f"{green}\nC: Show Chinese\n{reset}")
    choice = input(query).lower()
    if choice not in ["a", "b", "c"]: choice = "a"

    layouts = { 
            "a": {"prompt":"gloss", "hint":"pinyin", "key":"lemma"},
            "b": {"prompt":"pinyin", "hint":"gloss", "key":"lemma"},
            "c": {"prompt":"lemma", "hint":"pinyin", "key":"gloss"}}
    session["layout"] = layouts[choice]

    decks = sorted([*all_decks.keys()])
    displ_cols = 2
    displ_rows = math.ceil(len(decks) / displ_cols)
    displ_table = []
    tmp_row = []
    i = 0
    for r in range(displ_rows):
        for c in range(displ_cols):
            try:
                tmp_row.append(f"{i}: {decks[i]} ({len(all_decks[decks[i]])})")
            except:
                tmp_row.append("")
            i += 1
        displ_table.append(tmp_row)
        tmp_row = []
    

    f_string = "{: <30} " * displ_cols
    for r in displ_table:
        print(f_string.format(*r))
    tmp = input(f"{blue}\n> Which set do you want to use? {reset}")
    choice = 0
    try:
        choice = int(tmp)
    except:
        pass
    if choice >= len(decks):
        choice = len(decks) - 1

    session["set"] = all_decks[decks[choice]]

    choice = input(f"{blue}\n> Do you want to skip marked cards?{reset} ").lower() or "y"
    session["skip"] = choice[0] == "y"


    choice = input(f"{blue}\n> Do you want to see the cards in a random order?{reset} ").lower() or "y"
    session["shuffle"] = choice[0] == "y"


    choice = input(f"{blue}\n> Do you want to review incorrectly answered \
cards?{reset} ").lower() or "y"
    session["review"] = choice[0] == "y"

    ## Create the running list according to specifications
    running_list = []
    if session["skip"]:
        deck = session["set"]
        running_list = [deck[card]["lemma"] for card in deck if deck[card]["ranking"] < 100]
    else:
        running_list = [*session["set"].keys()]
    if session["shuffle"]:
        random.shuffle(running_list)
    card_total = len(running_list)
    running_list_count = 0
    count = 0


    while running_list_count < len(running_list):
        lemma = running_list[running_list_count]
        
        card = session["set"][lemma]
        card["lastview"] = dt.datetime.now().isoformat()
        card["views"] += 1

        skip_card = hint_shown = quit_session = False
        print()
        print(f"{blue}{running_list_count + 1} out of {len(running_list)} \
(card no.{card['seq']}){reset}")
        print(f"{blue}prompt:{reset} {card[session['layout']['prompt']]}")
        timing = time.perf_counter()
        while True: 
            action = input(f"{blue}Select: press h(int), s(kip), r(eveal \
answer) or q(uit){reset} ").lower()
            if action == "":
                action = "r"
            if action[0] in ["h","s","r", "q"]:
                if action[0] == "h" and hint_shown == False:
                    print(f"{blue}(Hint: \
                            {card[session['layout']['hint']]}){reset}")
                elif action[0] == "s":
                    skip_card = True
                    card["skipped"] += 1
                    break
                elif action[0] == "q":
                    quit_session = True
                    break
                else:
                    timing = time.perf_counter() - timing
                    print(f'\n{green}Answer:{reset} {card["lemma"]} ({card["pinyin"]}) = \
{card["gloss"]}{reset}')
                    while True:
                        choice = input(f"{blue}Were you correct? y/(n)?{reset} ").lower() or "y"
                        if choice[0] == "n":
                            card["wrong"] += 1
                            if session["review"]:
                                running_list.append(lemma)
                        break
                    break

        if skip_card: continue    
        if quit_session: break
        print(f"{green}That took you: {timing:0.1f} seconds.{reset}")

        running_list_count += 1

    save_json_deck(json_file,all_decks)


    # for lemma in session["set"]:
    #     card = session["set"][lemma]
    #     print(f'{card["lemma"]} views: {card["views"]} [wrong: {card["wrong"]}, skipped: {card["skipped"]}]')

    titles = ["lemma", "views", "wrong", "skipped"]
    report = [titles]
    deck = session["set"]
    for key in deck.keys():
        card = deck[key]
        row = []
        for field in titles:
            row.append(card[field])
        report.append(row)

        # report.append([card["lemma"], card["views"], card["wrong"], card["skipped"]])

    for row in report:
        print(f"  {green}{row[0]:<10} {blue}{row[1]:<10} {row[2]:>10} "
        f"{row[3]:>10}{reset}") 

main()
