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
playing fast and loose with the flashcards
need to update the info in them, so...
- take ID out of flashcard (they could be put in diff decks, anyway)
- work on the original set
"""

import random
from dataclasses import dataclass
import datetime
import time

@dataclass
class Flashcard:
    lemma: str
    pinyin: str
    gloss: str
    ID: int
    seq: int
    added: datetime.datetime
    lastview: datetime.datetime
    deck: str
    views: int
    rating: int
    ranking: int
    wrong: int
    skipped: int



def list_entries_in_file(source_file):
    with open(source_file, "r", encoding="utf-8") as f:
        tmp_deck = []
        deck_title = "undef"
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
                            0)
                            )
                    if line > 10: tmp_deck[-1].ranking = 101
            else:
                print("problem at line:",line)
    return tmp_deck

source_file="vocab.txt"
# flashcards = {}
flashcards = list_entries_in_file(source_file)
hide_cards = True

session = {
        # "layout": "a",
        "layout": {},
        "set": flashcards,
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

tmp = input("Which set do you want to use?")
session["set"] = flashcards

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
