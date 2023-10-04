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
- make work with better display? (e.g. webserver or tkinter)
- make the skip work

ABANDONED - strip out dataclass as not crucial and a pain to serialize
change logic:
    start: load in all_decks.json, then check for any new .csv's, move csv's to folder
    end: overwrite all_decks.json with updated version
"""
from pprint import pprint
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


RESET = "\u001b[0m"
BLUE = "\u001b[34m"
GREEN = "\u001b[32m"
RED = "\u001b[31m"

def save_json_deck(filename, flashcard_deck):
    with open(filename,"w") as new_deck:
        # saved_deck = json.dump(flashcard_deck, new_deck, cls=DateTimeEncoder)
        saved_deck = json.dump(flashcard_deck, new_deck)
        print(f"{RED}>> json file ({filename.name}) saved.{RESET}")

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


def create_pedigree_from_file(source_file):
    id_count = 0
    loaded_cats = []
    with source_file.open(mode="r", encoding="utf-8") as f:
        # tmp_deck = {}
        for line, curr_line in enumerate(f):
            if len(curr_line.strip()) == 0:
                print("Field missing at line:",line)
            elif curr_line[0] == "#":
                print("comment at line:", line)
            else:
                entry = curr_line.split(",")
                if len(entry) == 8:
                    # loaded_cats.append({
                    cat = {
                        "id": id_count,
                        "name": entry[0].strip(),
                        "gems": entry[1].strip(),
                        "gccf": entry[2].strip(),
                        "regnum": entry[3].strip(),
                        "dob": entry[4].strip(),
                        "cstatus": entry[5].strip(),
                        "sire": entry[6].strip(),
                        "dam": entry[7].strip(),
                        "anc": 0,
                        "des": 0,
                        }
                        # })
                    loaded_cats.append(cat)
                    id_count += 1
                else:
                    print("Field missing at line:",line)
    return loaded_cats


def print_feline(cat):
    male = '\u2640'
    female = '\u2642'
    print(f"[{cat['id']}] {cat['name']}: {cat['dob']} {male}: {cat['sire']}, {female}: {cat['dam']} ({cat['anc']}, {cat['des']})")


def print_cats(cats):
    for cat in cats:
        print_feline(cat)


def names_to_ids(cats, id_from_name):
    tmp_cats = cats.copy()
    for cat in tmp_cats:
        sire_id = id_from_name.get(cat['sire'].strip())
        dam_id = id_from_name.get(cat['dam'].strip())
        cat['sire'] = sire_id
        cat['dam'] = dam_id
        # if not (sire_id and dam_id):
        #     cat['anc'] = 0
    return tmp_cats


def make_id_key(all_cats):
    return {cat['id']: {key: cat[key] for key in cat if key != "id"} for cat in all_cats}


def assign_generations (cats_by_id):
    tmp_cats = cats_by_id.copy()
    for id,cat in tmp_cats.items():
        ## for now: assume if there isn't a dam, there isn't a sire
        sire = cat.get('sire')
        dam = cat.get('dam')
        if dam:
            cat['anc'] = 1
            tmp_cats[dam]['des'] = 1
        if sire:
            cat['anc'] = 1
            tmp_cats[sire]['des'] = 1
    return tmp_cats





def main():
    current_dir = Path( __file__ ).parent.absolute()
    csv_file = Path(current_dir / "2023_KITTEN PEDIGREE.csv")
    
    all_cats = create_pedigree_from_file(csv_file)
    id_from_name = {cat['name'].strip(): cat['id'] for cat in all_cats}
    # name_from_id = {cat['id']: cat['name'].strip() for cat in all_cats}
    all_cats = names_to_ids(all_cats, id_from_name)
    cats_by_id = make_id_key(all_cats)
    cats_by_id = assign_generations(cats_by_id)
    latest_generation = {id: cat for id, cat in cats_by_id.items()
                         if cat.get('anc') and not cat.get('des')}
    # pprint(latest_generation)
    for id, cat in latest_generation.items():
        print(id,cat['name'],cat['anc'], cat['des'])


main()
