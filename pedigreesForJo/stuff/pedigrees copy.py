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

def html_template(body, css_file=""):
    css_link = f"\n<link rel='stylesheet' type='text/css' href='{css_file}'>\n" if css_file else ""
    template = f"""
<html>
<head>
<title>pedigree</title>{css_link}
</head>
<body>
{body}
</body>
</html>
"""
    return template

def get_current_directory():
    return Path( __file__ ).parent.absolute()

def write_html_pedigree(html_string):
    html_file_address = Path(get_current_directory() / "out.html")
    with open(html_file_address, "w") as html_file:
        html_file.write(html_string)


def retrieve_file_by_suffix(suffix="csv"):
    if suffix[0] == ".":
        suffix = suffix[1:]
    # current_dir = Path( __file__ ).parent.absolute()
    current_dir = get_current_directory()
    # for full_path in sorted(current_dir.glob("*.csv")):
    for full_path in sorted(current_dir.glob(f"*.{suffix}")):
        file_name = Path(current_dir / full_path.name)
        print(f"\n\nOpening <{file_name.name}> to create pedigree...\n")
        return file_name

def add_unknown():
    return {
        -1 : {
        "name": "unknown dam",
        "gems": "",
        "sex": "f",
        "gccf": "",
        "regnum": "",
        "dob": "",
        "cstatus": "",
        "sire": "",
        "dam": "",
        "breeder": "",
        "owner": "",
        "anc": 0,
        "des": 0,},

        -2 : {
        "name": "unknown sire",
        "gems": "",
        "sex": "m",
        "gccf": "",
        "regnum": "",
        "dob": "",
        "cstatus": "",
        "sire": "",
        "dam": "",
        "breeder": "",
        "owner": "",
        "anc": 0,
        "des": 0,}
    }

def create_pedigree_from_file(source_file):
    id_count = 1
    loaded_cats = {}
    # num_of_fields = 8
    num_of_fields = 11
    with source_file.open(mode="r", encoding="utf-8") as f:
        # tmp_deck = {}
        for line, curr_line in enumerate(f):
            if len(curr_line.strip()) == 0:
                print("Field missing at line:",line)
            elif curr_line[0] == "#":
                print("comment at line:", line)
            else:
                # entry = curr_line.split(",")
                entry = [field.strip() for field in curr_line.split(",")]
                if entry[0].lower() == "name":
                    continue
                if len(entry) == num_of_fields:
                    # loaded_cats.append({
                    cat = {
                        id_count : {
                        "name": entry[0],
                        "gems": entry[1],
                        "sex": entry[2],
                        "gccf": entry[3],
                        "regnum": entry[4],
                        "dob": entry[5],
                        "cstatus": entry[6],
                        "sire": entry[7],
                        "dam": entry[8],
                        "breeder": entry[9],
                        "owner": entry[10],
                        "anc": 0,
                        "des": 0,
                        }}
                        # })
                    loaded_cats.update(cat)
                    id_count += 1
                else:
                    print("Field missing at line:",line)
    loaded_cats.update(add_unknown())
    return loaded_cats


def print_feline(id, cat):
    male = '\u2640'
    female = '\u2642'
    print(f"[{id}] {cat['name']}: {cat['dob']} {male}: {cat['sire']}, {female}: {cat['dam']}")


def print_cats(cats):
    for id, cat in cats.items():
        print_feline(id, cat)


def sub_names_to_ids(cats, id_from_name):
    tmp_cats = cats.copy()
    for id, cat in tmp_cats.items():
        if id < 0:
            continue
        sire_id = id_from_name.get(cat['sire'].strip())
        dam_id = id_from_name.get(cat['dam'].strip())
        cat['sire'] = sire_id
        cat['dam'] = dam_id
        # if not (sire_id and dam_id):
        #     cat['anc'] = 0
    return tmp_cats


def expand_ids_to_names(pedigree, cats):
    return {key:
            [cats[cat_id].get('name') for cat_id in val if cat_id >= 0]
            for key, val in pedigree.items()}


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


def get_latest_generation(cats):
    ## Logic: cats with ancestors but no heirs must be the latest generation
    latest_generation = {id: cat for id, cat in cats.items() if cat.get('anc') and not cat.get('des')}
    print(">>> Latest generation=")
    pprint([f"{cat['name']} ({id})" for id, cat in latest_generation.items()])
    print("")
    return latest_generation


# def recurse_pedigree(cat_id, cats, curr_generation=0, pedigree={}, completed=[]):
#     pedigree = update_dict(curr_generation, cat_id, pedigree)
#     completed.append(cat_id)
#     cat = cats[cat_id]
#     dam_id = cat['dam']
#     sire_id = cat['sire']
#     if dam_id:
#         if dam_id in completed:
#             update_dict(curr_generation + 1, dam_id, pedigree)
#         else:
#             recurse_pedigree(dam_id, cats, curr_generation + 1, pedigree, completed)
#     # else:
#     #     update_dict(curr_generation + 1, -1, pedigree)
#     if sire_id:
#         if sire_id in completed:
#             update_dict(curr_generation + 1, sire_id, pedigree)
#         else:
#             recurse_pedigree(sire_id, cats, curr_generation + 1, pedigree, completed)
#     # else:
#     #     update_dict(curr_generation + 1, -1, pedigree)
#     return pedigree

def update_dict(key,val, dict):
    if dict.get(key):
        dict[key].append(val)
    else:
        dict.update({key: [val]})
    return dict


# def recurse_pedigree(cat_id, cats, curr_generation=0, pedigree={}):
#     max_generations = 5
#     if curr_generation > max_generations:
#         return pedigree
#     pedigree = update_dict(curr_generation, cat_id, pedigree)
#     cat = cats[cat_id]
#     for ancestor_id, dummy_id in [[cat['dam'],-1],[cat['sire'], -2]]:
#         if ancestor_id:
#             recurse_pedigree(ancestor_id, cats, curr_generation + 1, pedigree)
#         elif curr_generation < max_generations:
#             recurse_pedigree(dummy_id, cats, curr_generation + 1, pedigree)
#             # update_dict(curr_generation + 1, dummy_id, pedigree)
#     return pedigree

def recurse_pedigree(cat_id, cats, curr_generation=0, pedigree={}):
    max_generations = 5
    if curr_generation > max_generations:
        return pedigree
    pedigree = update_dict(curr_generation, cat_id, pedigree)
    cat = cats[cat_id]
    for recorded_id, backup_id in [[cat['dam'],-1],[cat['sire'], -2]]:
        ancestor_id = recorded_id if recorded_id else backup_id
        recurse_pedigree(ancestor_id, cats, curr_generation + 1, pedigree)
    return pedigree

def build_header(cat_id, cats, sex_lookup):
    print("...header...", cat_id)
    return build_generic(cat_id, cats, sex_lookup)


def build_gen1(cat_id, cats, sex_lookup):
    return build_generic(cat_id, cats, sex_lookup)


def build_gen2(cat_id, cats, sex_lookup):
    return build_generic(cat_id, cats, sex_lookup)


def build_gen3(cat_id, cats, sex_lookup):
    return build_generic(cat_id, cats, sex_lookup)


def build_gen5(cat_id, cats, sex_lookup):
    return build_gen4(cat_id, cats, sex_lookup)


def build_gen4(cat_id, cats, sex_lookup):
    # print("gen 4:", cat)
    cat = cats[cat_id]
    is_dam = sex_lookup[cat_id] == "f"
    sex_icon = '\u2642' if is_dam else '\u2640'
    # sex = "Dam" if is_dam else "Sire"
    has_awards = cat['cstatus']
    awards = f"{has_awards} " if has_awards else ""
    awards_class = " champion" if has_awards else ""
    # gccf = f" <span class='gccf'>{cat['gccf']}</span>" if cat['gccf'] else ""
    profile = f"""
<div class='cat'>
    <p class="name{awards_class}">{awards}{cat['name']} {sex_icon}</p>
    <p class="desc">{cat['regnum']} {cat['gems']}</p>
</div>
"""
    return profile
    # return build_generic(cat, cats, sex_lookup)

def build_generic(cat_id, cats, sex_lookup):
    cat = cats[cat_id]
    is_dam = sex_lookup[cat_id] == "f"
    # sex_icon = '\u2642' if is_dam else '\u2640'
    sex = "Dam" if is_dam else "Sire"
    has_awards = cat['cstatus']
    awards = f"{has_awards} " if has_awards else ""
    awards_class = " champion" if has_awards else ""
    gccf = f" <span class='gccf'>{cat['gccf']}</span>" if cat['gccf'] else ""
    profile = f"""
<div class="cat">
    <p class="sex">{sex}</p>
    <p class="name{awards_class}">{awards}{cat['name']}</p>
    <p class="reg"><span class="feature">Reg no: </span>{cat['regnum']}<span</p>
    <p class="gems"><span class="feature">GEMS: </span>{cat['gems']}{gccf}</span></p>
    <p class="expand">tba</p>
</div>
"""
    return profile
    # return f"\n\t\t<li>{sex_icon} {cats[cat]['name'].title()}</li>"


def select_html_template(case, cat, cats, sex_lookup):
    if case < 0 or case > 4:
        case = 100
    switch = {
        0: build_header,
        1: build_gen1,
        2: build_gen2,
        3: build_gen3,
        4: build_gen4,
        5: build_gen5,
        100: build_generic
    }
    func = switch.get(case)
    return func(cat,cats, sex_lookup)


# def build_html_pedigree(pedigree, cats, sex_lookup):
#     html = ""
#     for individual in pedigree:
#         g_html = ""
#         for g_id, generation in individual.items():
#             print("g_id=",g_id)
#             g_class = "generation" if g_id else "header"
#             cat_html = ""
#             for cat in generation:
#                 cat_html += select_html_template(g_id, cat, cats, sex_lookup)
#             g_html += f"\t<div id='gen_{g_id}' class='{g_class}'><h2>{g_id}</h2>\n{cat_html}\n\t\n\t</div>\n"
#         html += f"<div id='cat_{individual.get(0)}' class='pedigree'>{g_html}\n</div>"
#     # print("\nHTML:")
#     # print(html)
#     return html

def build_html_pedigree(pedigree, cats, sex_lookup):
    html = ""
    for individual in pedigree:
        g_html = ""
        for g_id, generation in individual.items():
            print("g_id=",g_id)
            g_class = "generation" if g_id else "header"
            cat_html = ""
            for cat in generation:
                cat_html += select_html_template(g_id, cat, cats, sex_lookup)
            g_html += f"\t<div id='gen_{g_id}' class='{g_class}'><h2>{g_id}</h2>\n{cat_html}\n\t\n\t</div>\n"
        html += f"<div id='cat_{individual.get(0)}' class='pedigree'>{g_html}\n</div>"
    # print("\nHTML:")
    # print(html)
    return html

def cat_sex_lookup(cats):
    lookup = {}
    for id, cat in cats.items():
        if cat['dam']:
            lookup[cat['dam']] = "f"
        if cat['sire']:
            lookup[cat['sire']] = "m"
        if cat['sex']:
            lookup[id] = cat['sex']
    # pprint(lookup)
    # print(">>>>>>", cats[1])
    return lookup


def main():
    cats_to_print_by_id = [1]
    cats = create_pedigree_from_file(retrieve_file_by_suffix())
    id_from_name = {cat['name']: id for id, cat in cats.items()}
    cats = assign_generations(sub_names_to_ids(cats, id_from_name))
    sex_lookup = cat_sex_lookup(cats)
    latest_generation = get_latest_generation(cats)
    # cats.update(add_unknown())
    # pedigrees_by_name = []
    pedigrees = []
    for id, cat in latest_generation.items():
        if cats_to_print_by_id and id not in cats_to_print_by_id:
            continue
        tmp = recurse_pedigree(id, cats)
        # pedigrees_by_name.append(expand_ids_to_names(tmp, cats))
        pedigrees.append(tmp)
    pprint(pedigrees)
    # pprint([expand_ids_to_names(cat, cats) for cat in pedigrees])
    html_body = build_html_pedigree(pedigrees, cats, sex_lookup)
    write_html_pedigree(html_template(html_body,"pedigree.css"))



main()
