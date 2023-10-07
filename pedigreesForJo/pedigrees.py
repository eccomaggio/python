"""
Read in a pedigree .csv file and find the latest generation
Generate pedigree print out in HTML for each cat
"""
from pprint import pprint
# import random
from dataclasses import dataclass
# import datetime as dt
# import time
# import dateutil.parser
from pathlib import Path
# import json
# from json import JSONEncoder
# import string
# import math


def make_gems_lookup():
    return {
        "TOS n 31": "Brown BCR Tonkinese",
        "TOS f 31": "Brown Tortoiseshell BCR Tonkinese",
        "TOS n 21 31": "Brown Tabby BCR Tonkinese",
        "TOS f 21 31": "Brown Tortie-Tabby BCR Tonkinese",
        "TOS a 31": "Blue BCR Tonkinese",
        "TOS g 31": "Blue Tortoiseshell BCR Tonkinese",
        "TOS a 21 31": "Blue Tabby BCR Tonkinese",
        "TOS g 21 31": "Blue Tortie-Tabby BCR Tonkinese",
        "TOS b 31": "Chocolate BCR Tonkinese",
        "TOS h 31": "Chocolate Tortoiseshell BCR Tonkinese",
        "TOS b 21 31": "Chocolate Tabby BCR Tonkinese",
        "TOS h 21 31": "Chocolate Tortie-Tabby BCR Tonkinese",
        "TOS c 31": "Lilac BCR Tonkinese",
        "TOS j 31": "Lilac Tortoiseshell BCR Tonkinese",
        "TOS c 21 31": "Lilac Tabby BCR Tonkinese",
        "TOS j 21 31": "Lilac Tortie-Tabby BCR Tonkinese",
        "TOS a 31 121": "Caramel blue based BCR Tonkinese",
        "TOS g 31 121": "Caramel blue based Tortoiseshell BCR Tonkinese",
        "TOS a 21 31 121": "Caramel blue based Tabby BCR Tonkinese",
        "TOS g 21 31 121": "Caramel blue based Tortie-Tabby BCR Tonkinese",
        "TOS c 31 121": "Caramel lilac based BCR Tonkinese",
        "TOS j 31 121": "Caramel lilac based Tortoiseshell BCR Tonkinese",
        "TOS c 21 31 121": "Caramel lilac based Tabby BCR Tonkinese",
        "TOS j 21 31 121": "Caramel lilac based Tortie-Tabby BCR Tonkinese",
        "TOS p 31 121": "Caramel fawn based BCR Tonkinese",
        "TOS r 31 121": "Caramel fawn based Tortoiseshell BCR Tonkinese",
        "TOS p 21 31 121": "Caramel fawn based Tabby BCR Tonkinese",
        "TOS r 21 31 121": "Caramel fawn based Tortie-Tabby BCR Tonkinese",
        "TOS o 31": "Cinnamon BCR Tonkinese",
        "TOS q 31": "Cinnamon Tortoiseshell BCR Tonkinese",
        "TOS o 21 31": "Cinnamon Tabby BCR Tonkinese",
        "TOS q 21 31": "Cinnamon Tortie-Tabby BCR Tonkinese",
        "TOS p 31": "Fawn BCR Tonkinese",
        "TOS r 31": "Fawn Tortoiseshell BCR Tonkinese",
        "TOS p 21 31": "Fawn Tabby BCR Tonkinese",
        "TOS r 21 31": "Fawn Tortie-Tabby BCR Tonkinese",
        "TOS d 31": "Red BCR Tonkinese",
        "TOS d 21 31": "Red Tabby BCR Tonkinese",
        "TOS e 31": "Cream BCR Tonkinese",
        "TOS e 21 31": "Cream Tabby BCR Tonkinese",
        "TOS e 31 121": "Apricot BCR Tonkinese",
        "TOS e 21 31 121": "Apricot Tabby BCR Tonkinese",
        "TOS n 32": "Brown TCR Tonkinese",
        "TOS f 32": "Brown Tortoiseshell TCR Tonkinese",
        "TOS n 21 32": "Brown Tabby TCR Tonkinese",
        "TOS f 21 32": "Brown Tortie-Tabby TCR Tonkinese",
        "TOS a 32": "Blue TCR Tonkinese",
        "TOS g 32": "Blue Tortoiseshell TCR Tonkinese",
        "TOS a 21 32": "Blue Tabby TCR Tonkinese",
        "TOS g 21 32": "Blue Tortie-Tabby TCR Tonkinese",
        "TOS b 32": "Chocolate TCR Tonkinese",
        "TOS h 32": "Chocolate Tortoiseshell TCR Tonkinese",
        "TOS b 21 32": "Chocolate Tabby TCR Tonkinese",
        "TOS h 21 32": "Chocolate Tortie-Tabby TCR Tonkinese",
        "TOS c 32": "Lilac TCR Tonkinese",
        "TOS j 32": "Lilac Tortoiseshell TCR Tonkinese",
        "TOS c 21 32": "Lilac Tabby TCR Tonkinese",
        "TOS j 21 32": "Lilac Tortie-Tabby TCR Tonkinese",
        "TOS a 32 121": "Caramel blue based TCR Tonkinese",
        "TOS g 32 121": "Caramel blue based Tortoiseshell TCR Tonkinese",
        "TOS a 21 32 121": "Caramel blue based Tabby TCR Tonkinese",
        "TOS g 21 32 121": "Caramel blue based Tortie-Tabby TCR Tonkinese",
        "TOS c 32 121": "Caramel lilac based TCR Tonkinese",
        "TOS j 32 121": "Caramel lilac based Tortoiseshell TCR Tonkinese",
        "TOS c 21 32 121": "Caramel lilac based Tabby TCR Tonkinese",
        "TOS j 21 32 121": "Caramel lilac based Tortie-Tabby TCR Tonkinese",
        "TOS p 32 121": "Caramel fawn based TCR Tonkinese",
        "TOS r 32 121": "Caramel fawn based Tortoiseshell TCR Tonkinese",
        "TOS p 21 32 121": "Caramel fawn based Tabby TCR Tonkinese",
        "TOS r 21 32 121": "Caramel fawn based Tortie-Tabby TCR Tonkinese",
        "TOS o 32": "Cinnamon TCR Tonkinese",
        "TOS q 32": "Cinnamon Tortoiseshell TCR Tonkinese",
        "TOS o 21 32": "Cinnamon Tabby TCR Tonkinese",
        "TOS q 21 32": "Cinnamon Tortie-Tabby TCR Tonkinese",
        "TOS p 32": "Fawn TCR Tonkinese",
        "TOS r 32": "Fawn Tortoiseshell TCR Tonkinese",
        "TOS p 21 32": "Fawn Tabby TCR Tonkinese",
        "TOS r 21 32": "Fawn Tortie-Tabby TCR Tonkinese",
        "TOS d 32": "Red TCR Tonkinese",
        "TOS d 21 32": "Red Tabby TCR Tonkinese",
        "TOS e 32": "Cream TCR Tonkinese",
        "TOS e 21 32": "Cream Tabby TCR Tonkinese",
        "TOS e 32 121": "Apricot TCR Tonkinese",
        "TOS e 21 32 121": "Apricot Tabby TCR Tonkinese",
        "TOS n 33": "Brown CPP Tonkinese",
        "TOS f 33": "Brown Tortoiseshell CPP Tonkinese",
        "TOS n 21 33": "Brown Tabby CPP Tonkinese",
        "TOS f 21 33": "Brown Tortie-Tabby CPP Tonkinese",
        "TOS a 33": "Blue CPP Tonkinese",
        "TOS g 33": "Blue Tortoiseshell CPP Tonkinese",
        "TOS a 21 33": "Blue Tabby CPP Tonkinese",
        "TOS g 21 33": "Blue Tortie-Tabby CPP Tonkinese",
        "TOS b 33": "Chocolate CPP Tonkinese",
        "TOS h 33": "Chocolate Tortoiseshell CPP Tonkinese",
        "TOS b 21 33": "Chocolate Tabby CPP Tonkinese",
        "TOS h 21 33": "Chocolate Tortie-Tabby CPP Tonkinese",
        "TOS c 33": "Lilac CPP Tonkinese",
        "TOS j 33": "Lilac Tortoiseshell CPP Tonkinese",
        "TOS c 21 33": "Lilac Tabby CPP Tonkinese",
        "TOS j 21 33": "Lilac Tortie-Tabby CPP Tonkinese",
        "TOS a 33 121": "Caramel blue based CPP Tonkinese",
        "TOS g 33 121": "Caramel blue based Tortoiseshell CPP Tonkinese",
        "TOS a 21 33 121": "Caramel blue based Tabby CPP Tonkinese",
        "TOS g 21 33 121": "Caramel blue based Tortie-Tabby CPP Tonkinese",
        "TOS c 33 121": "Caramel lilac based CPP Tonkinese",
        "TOS j 33 121": "Caramel lilac based Tortoiseshell CPP Tonkinese",
        "TOS c 21 33 121": "Caramel lilac based Tabby CPP Tonkinese",
        "TOS j 21 33 121": "Caramel lilac based Tortie-Tabby CPP Tonkinese",
        "TOS p 33 121": "Caramel fawn based CPP Tonkinese",
        "TOS r 33 121": "Caramel fawn based Tortoiseshell CPP Tonkinese",
        "TOS p 21 33 121": "Caramel fawn based Tabby CPP Tonkinese",
        "TOS r 21 33 121": "Caramel fawn based Tortie-Tabby CPP Tonkinese",
        "TOS o 33": "Cinnamon CPP Tonkinese",
        "TOS q 33": "Cinnamon Tortoiseshell CPP Tonkinese",
        "TOS o 21 33": "Cinnamon Tabby CPP Tonkinese",
        "TOS q 21 33": "Cinnamon Tortie-Tabby CPP Tonkinese",
        "TOS p 33": "Fawn CPP Tonkinese",
        "TOS r 33": "Fawn Tortoiseshell CPP Tonkinese",
        "TOS p 21 33": "Fawn Tabby CPP Tonkinese",
        "TOS r 21 33": "Fawn Tortie-Tabby CPP Tonkinese",
        "TOS d 33": "Red CPP Tonkinese",
        "TOS d 21 33": "Red Tabby CPP Tonkinese",
        "TOS e 33": "Cream CPP Tonkinese",
        "TOS e 21 33": "Cream Tabby CPP Tonkinese",
        "TOS e 33 121": "Apricot CPP Tonkinese",
        "TOS e 21 33 121": "Apricot Tabby CPP Tonkinese",
        "BUR c": "Lilac Burmese",
        "BUR a": "Blue Burmese",
        "BUR b": "Chocolate Burmese",
        "BUR h": "Chocolate Tortoiseshell Burmese",
        "BUR n": "Brown Burmese",
        "SIA a": "Blue Point Siamese",
        "SIA b": "Chocolate Point Siamese",
        "SIA c": "Lilac Point Siamese",
        "SIA n": "Seal Point Siamese",
    }

# def html_template(body, css_file="", title="pedigree"):
#     css_link = f"\n<link rel='stylesheet' type='text/css' href='{css_file}'>\n" if css_file else ""
def html_template(body, css_files=[], title="pedigree"):
    css_link = ""
    if css_files:
        for file in css_files:
            css_link += f"\n<link rel='stylesheet' type='text/css' href='{file}'>"
    template = f"""
<html>
<head>
<title>{title}</title>{css_link}
</head>
<body>
{body}
</body>
</html>
"""
    return template

def get_current_directory():
    return Path( __file__ ).parent.absolute()

def write_html_pedigree(html_string, filename="out.html"):
    html_file_address = Path(get_current_directory() / filename)
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
    # print(">>> Latest generation=")
    # pprint([f"{cat['name']} ({id})" for id, cat in latest_generation.items()])
    # print("")
    return latest_generation


def update_dict(key,val, dict):
    if dict.get(key):
        # dict[key].append(val)
        dict[key].insert(0,val)
    else:
        dict.update({key: [val]})
    return dict

# def build_pedigree(cat_id, cats, max_generations):


def recurse_pedigree(cat_id, cats, max_generations, curr_generation=0, pedigree={}):
    # max_generations = 5
    if curr_generation > max_generations:
        return pedigree
    if curr_generation == 0:
        pedigree = {0:[cat_id]}
    else:
        pedigree = update_dict(curr_generation, cat_id, pedigree)
    cat = cats[cat_id]
    for recorded_id, backup_id in [[cat['dam'],-1],[cat['sire'], -2]]:
        ancestor_id = recorded_id if recorded_id else backup_id
        recurse_pedigree(ancestor_id, cats, max_generations, curr_generation + 1, pedigree)
    return pedigree


def recurse_for_grid(cat_id, cats, max_generations, curr_generation=0, pedigree=None):
    # max_generations = 5
    if curr_generation > max_generations:
        return pedigree
    if curr_generation == 0:
        pedigree = [[cat_id,curr_generation]]
    #     # flat.append([cat_id, 0])
    #     pass
    else:
        # flat.insert(1, cat_id)
        pedigree.append([cat_id,curr_generation])
    cat = cats[cat_id]
    # for recorded_id, backup_id in [[cat['dam'],-1],[cat['sire'], -2]]:
    for recorded_id, backup_id in [[cat['sire'],-2],[cat['dam'], -1]]:
        ancestor_id = recorded_id if recorded_id else backup_id
        recurse_for_grid(ancestor_id, cats, max_generations, curr_generation + 1, pedigree)
    return pedigree

def build_grid(flat_pedigrees, cats, sex_lookup, gems_lookup, max_generations_depth):
    # pprint(flat_pedigrees, depth=5, width=80, compact=True)
    # pprint(flat_pedigrees)
    for pedigree in flat_pedigrees:
        print(f"Printing grid for {cats[pedigree[0][0]]['name']} ({pedigree[0][0]})")
        grid_html = ""
        header_html = ""
        target_id = None
        for cat_id, g_id in pedigree:
            if g_id == 0:
                target_id = cat_id
                header_html = build_header(target_id, cats, sex_lookup, gems_lookup)
                continue
            # grid_html += f"<div class='g{gen}'>{cats[cat_id]['name']} ({cat_id})</div>\n"
            grid_html += f"<div class='g{g_id}'>{build_html_cat(g_id, cat_id, cats, sex_lookup, gems_lookup)}</div>\n"
        grid_html = f"<div id='container'>\n{grid_html}\n</div>"

        target_name = cats[target_id]['name']
        grid_css_file = f"grid{max_generations_depth}.css"
        html = html_template(header_html + grid_html + build_footer(), ["pedigree.css", grid_css_file], f"Pedigree for {target_name}")
        write_html_pedigree(html, f"{target_id}-{target_name.replace(' ', '-')}.html")



def build_header(cat_id, cats, sex_lookup, gems_lookup):
    i = get_display_info(cat_id, cats, sex_lookup, gems_lookup)
    return f"""
<table class="header">
    <tr>
        <td rowspan="2">
        <p class="feature">Breeder:</p>
        <p class="breeder">LONGNAP</p>
        <p class="feature">
        Ms J Sturgess<br>
        5 Catharine Close Radley ABINGDON<br>
        OX14 3AR
        </p>
        </td>
        <td class="banner">Name: <span class="name">{i["name"]}</span></td>
    </tr>
    <tr>
        <td class="cat-info">
            <p class="feature"><b>Reg no: </b>{i["regnum"]} {i["gccf"]}<span</p>
            <p class="feature"><b>Date of birth: </b>{i["cat"]["dob"]}</p>
            <p class="feature"><b>Microchip: </b></p>
            <p class="feature"><b>Sex: </b>{i["sex"]}</p>
            <p class="feature"><b>GEMS: </b>{i["gems"]} {i["catsplain"]}</p>
            <p class="feature"><b>Status: </b>NonActive</p>
            <p class="feature bold">Owner: </b></p>
        </td>
    </tr>
</table>

"""


def build_footer():
    return """
<div class="footer">
<p>For cats marked (IMP)* details are as supplied by the governing body of the country of origin.</p>
<p>I certify that this pedigree is accurate, to the best of my knowledge and belief.</p>
<p class="signature">SIGNED: ................................................................
&nbsp;&nbsp; DATE:..................</p>
"""


def build_gen1(cat_id, cats, sex_lookup, gems_lookup):
    return build_generic(cat_id, cats, sex_lookup, gems_lookup)


def build_gen2(cat_id, cats, sex_lookup, gems_lookup):
    return build_generic(cat_id, cats, sex_lookup, gems_lookup)


def build_gen3(cat_id, cats, sex_lookup, gems_lookup):
    i = get_display_info(cat_id, cats, sex_lookup, gems_lookup)
    return f"""
<div class="cat">
    <p class="nameline{i["awards_class"]}">{i["awards"]}
    <span class="name">{i["name"]}</span>
    <span class="cat_id"> ({cat_id})</span></p>
    <p class="reg"><span class="feature">Reg no: </span>{i["regnum"]}<span</p>
    <p class="gems"><span class="feature">GEMS: </span>{i["gems"]} {i["gccf"]}</span></p>
    <p class="expand">{i["catsplain"]}</p>
</div>
"""


def build_gen4(cat_id, cats, sex_lookup, gems_lookup):
    i = get_display_info(cat_id, cats, sex_lookup, gems_lookup)
    return f"""
<div class="cat">
    <p class="nameline{i["awards_class"]}">{i["awards"]}
        <span class="name">{i["name"]}</span>
        <span class="cat_id"> ({cat_id}) </span>{i["sex_icon"]}</p>
    <p class="desc">{i["regnum"]} {i["gems"]}</p>
</div>
"""


def build_gen5(cat_id, cats, sex_lookup, gems_lookup):
    # return build_gen4(cat_id, cats, sex_lookup)
    i = get_display_info(cat_id, cats, sex_lookup, gems_lookup)
    return f"""
<div class='cat'>
    <p class="nameline">{i["awards"]}<span class='name{i["awards_class"]}'>{i["name"]}</span>
    <span class="cat_id"> ({cat_id})<span>{i["sex_icon"]}
    {i["regnum"]} {i["gems"]}</p>
</div>
"""


def build_generic(cat_id, cats, sex_lookup, gems_lookup):
    i = get_display_info(cat_id, cats, sex_lookup, gems_lookup)
    return f"""
<div class="cat">
    <p class="sex">{i["sex"]}</p>
    <p class="nameline{i["awards_class"]}">{i["awards"]}
        <span class="name">{i["name"]}</span>
        <span class="cat_id"> ({cat_id})</span></p>
    <p class="reg"><span class="feature">Reg no: </span>{i["regnum"]}<span</p>
    <p class="gems"><span class="feature">GEMS: </span>{i["gems"]} {i["gccf"]}</span></p>
    <p class="expand">{i["catsplain"]}</p>
</div>
"""


def get_display_info(cat_id, cats, sex_lookup, gems_lookup):
    cat = cats[cat_id]
    is_dam = sex_lookup[cat_id] == "f"
    # sex = "Dam" if is_dam else "Sire"
    has_awards = cat['cstatus']
    gccf = cat['gccf']
    gems = cat['gems']
    return {
        "cat": cat,
        "gccf": gccf,
        "name": cat['name'],
        "regnum": cat['regnum'],
        "gems": gems,
        "is_dam": is_dam,
        "sex_icon": '\u2642' if is_dam else '\u2640',
        "sex": "Dam" if is_dam else "Sire",
        # "sex": sex,
        "has_awards": has_awards,
        "awards": f"{has_awards} " if has_awards else "",
        "awards_class": " champion" if has_awards else "",
        "gccf_text": f" <span class='gccf'>{gccf}</span>" if gccf else "",
        "catsplain": gems_lookup.get(gems, "")
    }


def select_html_template(case, cat, cats, sex_lookup, gems_lookup):
    if case < 0 or case > 5:
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
    return func(cat,cats, sex_lookup, gems_lookup)


def build_html(pedigrees, cats, sex_lookup, gems_lookup):
    ## pedigrees = [  [{0: [[1]]},{1: [[6, 5]]},{2: [[14, 13], [8, 7]]}],  [pedigree2 (etc.)]  ]
    # pedigree_html = ""
    for pedigree in pedigrees:
        gen_wrapper_html = ""
        for generation_dict in pedigree:
            header_html = build_header(generation_dict[0][0][0], cats, sex_lookup, gems_lookup)
            generation_html = ""
            for g_id, generation in generation_dict.items():
                if g_id == 0:
                    continue
                pair_html = ""
                for pair in generation:
                    cat_html = ""
                    for cat_id in pair:
                        # print("cat:", cat_id, cats[cat_id]['name'])
                        cat_html += build_html_cat(g_id, cat_id, cats, sex_lookup, gems_lookup)
                    pair_html += build_html_pairs(cat_html)
                generation_html += build_html_generation(g_id, pair_html)
            gen_wrapper_html = build_html_gen_wrapper(generation_html)
        target_id = pedigree[0][0][0][0]
        target_name = cats[target_id]['name']
        html = html_template(header_html + gen_wrapper_html, ["pedigree.css"], f"Pedigree for {target_name}")
        # write_html_pedigree(html, f"{target_id}-{target_name.replace(' ', '-')}.OLD.html")
    # return pedigree_html



def build_html_pedigree(target_id, gen_wrapper_html, cats):
    tmp = f"""
<article id='catID:{target_id}' title='{cats[target_id]['name']}'>
    {gen_wrapper_html}
</article>
    """
    return tmp

def build_html_gen_wrapper(generation_html):
    tmp = f"""
<div class="gen_wrapper">
    {generation_html}
</div>
    """
    return tmp


def build_html_generation(g_id, pair_html):
    g_class = "generation" if g_id else "header"
    tmp = f"""
<div id='gen_{g_id}' class='{g_class}'>
    {pair_html}
</div>"""
    return tmp


def build_html_pairs(cat_html):
    tmp = f"\n<div class='pair'>{cat_html}</div>\n"
    return tmp


def build_html_cat(g_id, cat_id, cats, sex_lookup, gems_lookup):
    tmp = select_html_template(g_id, cat_id, cats, sex_lookup, gems_lookup)
    return tmp



def make_sex_lookup(cats):
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

def reverse_order(pedigrees):
    # print(pedigrees)
    tmp = []
    for pedigree in pedigrees:
        for i in pedigree:
            # print(">>", i,pedigrees[i])
            tmp.append({i:pedigree[i][::-1]})
        # print(tmp)
    # return tmp
    return pedigrees

def pair_and_reverse(pedigrees):
    ## This divides ancestors into pairs (sire,dam) & reverses the presentation order
    ## pedigrees = [  [{0: [1]},{1: [6, 5]},{2: [14, 13, 8, 7]}],  [pedigree2 (etc.)]  ]
    tmp = [[{k:
            [v[i:i+2] for i in range(0, len(v), 2)][::-1]
            for k,v in g.items()}
        for g in p]
        for p in pedigrees]
    return tmp

def pair_ancestors(pedigrees):
    ## This divides ancestors into pairs (sire,dam)
    ## pedigrees = [  [{0: [1]},{1: [6, 5]},{2: [14, 13, 8, 7]}],  [pedigree2 (etc.)]  ]
    tmp = [[{k:
            [v[i:i+2] for i in range(0, len(v), 2)]
            for k,v in g.items()}
        for g in p]
        for p in pedigrees]
    return tmp


def main():
    # cats_to_print_by_id = [1]
    cats_to_print_by_id = [1,2,3,4]
    max_generations_depth = 5
    cats = create_pedigree_from_file(retrieve_file_by_suffix())
    id_from_name = {cat['name']: id for id, cat in cats.items()}
    cats = assign_generations(sub_names_to_ids(cats, id_from_name))
    sex_lookup = make_sex_lookup(cats)
    gems_lookup = make_gems_lookup()
    ## latest_generation finds top level cats (i.e. have not yet sired)
    # latest_generation = get_latest_generation(cats)
    pedigrees = []
    grid_pedigrees = []
    for cat_id in cats_to_print_by_id:
        cat = cats[cat_id]
        print("recursing for:", cat_id, cat['name'])
        tmp = recurse_pedigree(cat_id, cats, max_generations_depth)
        pedigrees.append([tmp])
        tmp1 = recurse_for_grid(cat_id, cats, max_generations_depth)
        grid_pedigrees.append(tmp1)
        # flat_pedigrees.append({cat_id: tmp1})
    # print("grid version:", grid_pedigrees)
    # pprint(pedigrees, depth=4, width=80, compact=True)
    pedigrees = pair_ancestors(pedigrees)
    ## Actually, pedigrees is no longer used but its layout is more human reader friends, so I've kept it for ref.
    # build_html(pedigrees, cats, sex_lookup, gems_lookup)
    build_grid(grid_pedigrees, cats, sex_lookup, gems_lookup, max_generations_depth)


main()
