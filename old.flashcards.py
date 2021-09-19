"""
Takes a text file containing vocab: lemma_pinyin_gloss

Lemma/pinyin/gloss/ID/sequence/set-added/subjective_ranking/official_ranking/
...date-view/count-last/viewed/correctly_answered_count/skipped_count
=13 slots

Subjective ranking: 0 none / 10 too easy (skip) /
20 difficult (prompt more) / 30 very difficult (prompt a lot!) / 
40 irrelevant (skip)

with thanks to https://stackabuse.com/read-a-file-line-by-line-in-python/ 
"""

"""TODO
ABANDONED - strip out dataclass as not crucial and a pain to serialize
change logic: 
    start: load in all_decks.json, then check for any new .csv's, move csv's to folder
    end: overwrite all_decks.json with updated version
"""

import random
from dataclasses import dataclass
import datetime
import time
from pathlib import Path
import json
import string
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Flashcard:
    lemma: str
    pinyin: str
    gloss: str
    ID: int
    seq: int
    added: datetime.datetime
    lastview: datetime.datetime
    title: str
    views: int
    rating: int
    ranking: int
    wrong: int
    skipped: int


def save_json_deck(filename, flashcard_deck):
    with open(filename,"w") as new_deck:
        saved_deck = json.dump(flashcard_deck.to_dict(), new_deck)

def retrieve_json_decks():
    current_dir = Path(".")
    tmp_decks = {}
    for saved_deck in current_dir.glob("*.json"):
        with open(saved_deck, "w") as retrieved_deck:
            tmp = json.load(retrieved_deck)
            tmp_decks[tmp[0].title] = tmp
    return tmp_decks
        
def create_deck_from_file(source_file):
    deck_title = "undef"
    # with open(source_file, "r", encoding="utf-8") as f:
    with source_file.open(mode="r", encoding="utf-8") as f:
        tmp_deck = []
        for line, curr_line in enumerate(f):
            if len(curr_line.strip()) == 0:
                print("empty line")
            elif curr_line[0] == "*":
                deck_title = curr_line[1:].strip()
            elif curr_line[0] == "#":
                print("comment at line:", line)
            elif len(curr_line.strip()) > 0:
                entry = curr_line.split("_")
                if len(entry) == 3:
                    # flashcards[entry[0]] = (entry[1],entry[2].strip())
                    tmp_deck.append(Flashcard(
                            entry[0],
                            entry[1],
                            entry[2].strip(),
                            line,
                            line,
                            datetime.datetime.now(),
                            None,
                            deck_title,
                            0,
                            0,
                            0,
                            0,
                            0))
                            
                    # if line > 10: tmp_deck[-1].ranking = 101
            else:
                print("problem at line:",line)

    save_json_deck(Path.cwd() / f"{deck_title}.json", tmp_deck)
    csv_dir = Path.cwd() / "csv_files"
    if not csv_dir.exists():
        csv_dir.mkdir(mode=0o777,parents=False,exist_ok=False)
    source_file.replace(csv_dir) 

    return tmp_deck

# source_file="vocab.txt"
# flashcards = {}
all_decks = {}
current_dir = Path().cwd()
for f in sorted(current_dir.glob("*.csv")):
    new_deck = create_deck_from_file(f)
    # print(new_deck.title)
    all_decks[new_deck[0].title] = new_deck

more_decks = retrieve_json_decks()
print(more_decks)
exit()
all_decks.append(more_decks)

decks_available = {}
tmp_count = 0
for key in all_decks.keys():
    decks_available[string.ascii_lowercase[tmp_count]] = key
    tmp_count += 1
# Insert decks from .json files here
# print(tmp)
#     print(key)
#     for card in all_decks[key]:
#         print(card.lemma)
        
# exit()

hide_cards = True

session = {
        # "layout": "a",
        "layout": {},
        "set": {},
        "skip": False,
        "shuffle": True,
        "review": True
        }

# session["layout"] = input("What prompt do you want to see?"
tmp = input("What prompt do you want to see?"
        "\nA: Show English first (default)"
        "\nB: Show pinyin first"
        "\nC: Show Chinese\n").lower()
# if session["layout"] not in ["a", "b", "c"]: session["layout"] = "a"
if tmp not in ["a", "b", "c"]: tmp = "a"

layouts = { 
        "a": {"prompt":"gloss", "hint":"pinyin", "key":"lemma"},
        "b": {"prompt":"pinyin", "hint":"gloss", "key":"lemma"},
        "c": {"prompt":"lemma", "hint":"pinyin", "key":"gloss"}}
# layout = layouts[session["layout"]]
session["layout"] = layouts[tmp]

# print(f">> {session['set'][2].lemma}")
# print(f">> {getattr(session['set'][2],session['layout']['prompt'])}")
# exit()
# print(card)
# quit()

# decks_available = all_decks.keys()
display_text = ""
for key in decks_available.keys():
    display_text += f"{key} = {decks_available[key]}  "
print(display_text)
tmp = input("Which set do you want to use? ('a', 'b', etc.)").lower()
while True:
    if tmp in decks_available:
        break
session["set"] = all_decks[decks_available[tmp]]

tmp = input("Do you want to skip marked cards?").lower()
session["skip"] = tmp[0] == "y"
if session["skip"] :
    # session["set"] = [card for card in session["set"] if card.ranking < 100]
    hide_cards = True

tmp = input("Do you want to see the cards in a random order?").lower()
session["shuffle"] = tmp[0] == "y"
if session["shuffle"] :
    random.shuffle(session["set"])

tmp = input("Do you want to review incorrectly answered cards?").lower()
session["review"] = tmp[0] == "y"

card_total = len(session["set"])
count = 0
for card in session["set"]:
    if hide_cards and card.ranking > 100 :
        continue
    count += 1
    card.lastview == datetime.datetime.now()
    card.views += 1

    skip_card = hint_shown = quit_session = False
    # print(f"prompt: {card.lemma}")
    print()
    print(f"{count} out of {card_total}")
    print(f"prompt: {getattr(card,session['layout']['prompt'])}")
    timing = time.perf_counter()
    while True: 
        action = input("Select: press h(int), s(kip), r(eveal answer) or q(uit)").lower()
        if action[0] in ["h","s","r", "q"]:
            if action[0] == "h" and hint_shown == False:
                print(f"(Hint: {getattr(card, session['layout']['hint'])})")
            elif action[0] == "s":
                skip_card = True
                card.skipped += 1
                break
            elif action[0] == "q":
                quit_session = True
                break
            else:
                timing = time.perf_counter() - timing
                print(f"Answer: {getattr(card, session['layout']['key'])}")
                while True:
                    tmp = input("Were you correct? y(es) or n(o)?").lower()
                    if tmp[0] in ["y","n"]:
                        if tmp[0] == "n":
                            card.wrong += 1
                    break
                break

    if skip_card: continue    
    if quit_session: break
    print(f"That took you: {timing:0.1f} seconds.")


    # print(session)

for card in session["set"]:
    print(f"{card.lemma} views: {card.views} [wrong: {card.wrong}, skipped: {card.skipped}] {card.lastview}")
