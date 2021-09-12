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
        curr_deck = "undef"
        for line, curr_line in enumerate(f):
            if len(curr_line.strip()) == 0:
                print("empty line")
            elif curr_line[0] == "*":
                curr_deck = curr_line[1:].strip()
            elif curr_line[0] != "#" or len(curr_line.strip()) > 0:
                entry = curr_line.split("_")
                if len(entry) == 3:
                    # flashcards[entry[0]] = (entry[1],entry[2].strip())
                    flashcards[entry[0]] = Flashcard(
                            entry[0],
                            entry[1],
                            entry[2].strip(),
                            line,
                            line,
                            datetime.datetime.now(),
                            None,
                            curr_deck,
                            0,
                            0,
                            0,
                            0,
                            0
                            )
                else:
                    print("problem at line:",line)

source_file="vocab.txt"
flashcards = {}
list_entries_in_file(source_file)

session = {}
session["set"] = input("Which set do you want to use?")
session["skip"] = input("Do you want to skip any cards?")
session["shuffle"] = input("Do you want to see the cards in a random order?")
session["review"] = input("Do you want to review incorrectly answered cards?")

print(session)

# print(flashcards)
