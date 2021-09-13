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

import random
from dataclasses import dataclass
import datetime

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
            elif curr_line[0] != "#" or len(curr_line.strip()) > 0:
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

session = {
        "layout": "a",
        "set": flashcards,
        "skip": False,
        "shuffle": True,
        "review": True
        }

session["layout"] = input("What prompt do you want to see?"
        "\nA: Show English first (default)"
        "\nB: Show pinyin first"
        "\nC: Show Chinese\n").lower()
if session["layout"] not in ["a", "b", "c"]: session["layout"] = "a"

layouts = { 
        "a": {"prompt":"gloss", "hint":"pinyin", "key":"lemma"},
        "b": {"prompt":"pinyin", "hint":"gloss", "key":"lemma"},
        "c": {"prompt":"lemma", "hint":"pinyin", "key":"gloss"}}
layout = layouts[session["layout"]]

# print(card)
# quit()

tmp = input("Which set do you want to use?")
session["set"] = flashcards

tmp = input("Do you want to skip marked cards?").lower()
session["skip"] = tmp[0] == "y"
if session["skip"] :
    session["set"] = [card for card in session["set"] if card.ranking < 100]

tmp = input("Do you want to see the cards in a random order?").lower()
session["shuffle"] = tmp[0] == "y"
if session["shuffle"] :
    random.shuffle(session["set"])

tmp = input("Do you want to review incorrectly answered cards?").lower()
session["review"] = tmp[0] == "y"

for card in session["set"]:
    # print(f"prompt: {card.lemma}")
    print(f"prompt: {getattr(card,layout['prompt'])}")
# print(session)

# print(flashcards)
