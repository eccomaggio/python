"""
Read in a pedigree .csv file and find the latest generation
Generate pedigree print out in HTML for each cat
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

# def save_json_deck(filename, flashcard_deck):
#     with open(filename,"w") as new_deck:
#         # saved_deck = json.dump(flashcard_deck, new_deck, cls=DateTimeEncoder)
#         saved_deck = json.dump(flashcard_deck, new_deck)
#         print(f"{RED}>> json file ({filename.name}) saved.{RESET}")

# def retrieve_json_file(file):
#     with open(file,"r") as f:
#         return json.load(f)

# def retrieve_json_decks(current_dir):
#     tmp_decks = {}
#     for saved_deck in current_dir.glob("*.json"):
#         tmp_decks.update(retrieve_json_file(saved_deck))
#     return tmp_decks


def create_pedigree_from_file(source_file):
    id_count = 0
    loaded_cats = {}
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
                        id_count : {
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
                        }}
                        # })
                    loaded_cats.update(cat)
                    id_count += 1
                else:
                    print("Field missing at line:",line)
    return loaded_cats


def print_feline(id, cat):
    male = '\u2640'
    female = '\u2642'
    print(f"[{id}] {cat['name']}: {cat['dob']} {male}: {cat['sire']}, {female}: {cat['dam']}")


def print_cats(cats):
    for id, cat in cats.items():
        print_feline(id, cat)


def names_to_ids(cats, id_from_name):
    tmp_cats = cats.copy()
    for id, cat in tmp_cats.items():
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
    cats = create_pedigree_from_file(csv_file)
    id_from_name = {cat['name']: id for id, cat in cats.items()}
    cats = names_to_ids(cats, id_from_name)
    cats = assign_generations(cats)
    ## Logic: cats with ancestors but no heirs must be the latest generation
    latest_generation = {id: cat for id, cat in cats.items()
                         if cat.get('anc') and not cat.get('des')}
    # pprint(latest_generation)
    print_cats(latest_generation)
    # for id, cat in latest_generation.items():
    #     print(id,cat['name'],cat['anc'], cat['des'])


main()
