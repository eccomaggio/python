"""
Read in a pedigree .csv file
(find the latest generation)
Generate pedigree print out in HTML for each cat specified
Stand-alone HTML generated

Requirements:
    .csv (only one!) in same directory as python file
    python 3

Variables (in main() ):
    list of ids of cats to print out
    depth of generations to include in pedigree
    base font size of grid

"""
from pprint import pprint
from dataclasses import dataclass
from pathlib import Path
import sys
import getopt


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

def css_styles_template(depth, base_font_size=12):
    return f"""
<style>
    :root {{
        --line-weight: 1px;
    }}

    * {{
        margin: 0;
        padding: 0;
    }}

    body {{
        font-family: Arial, Helvetica, sans-serif;
        font-size: {base_font_size}pt;
        padding: 5px;
    }}
""" + """

    .header {
        margin-bottom: 3px;
        width: 100%;
        font-size: 11pt;
    }

    .banner {
        font-weight: bold;
        font-size: larger;
    }

    .banner .name {
        font-weight: normal;
        font-size: x-large;
    }

    .breeder {
        font-weight: bold;
        padding: 5px 0;
    }

    table, td {
        border: var(--line-weight) solid black;
        border-collapse: collapse;
        padding: 6px;
    }

    .cat-info p {
        padding-bottom: 3px;
    }

    .footer {
        padding-top: 9px;
        font-size: smaller;
    }

    .footer p {
        padding-bottom: 3px;
    }

    .signature {
        text-align: right;
    }

    .gen_wrapper {
        display: flex;
        flex-direction: row;
        align-items: stretch;
    }

    .generation {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }

    /*#gen_3, #gen_4, .g3, .g4 {*/
    .g3, .g4 {
        font-size: 0.75em;
    }

    /*#gen_5, .g5, #gen_6, .g6, #gen_7, .g7, #gen_8, .g8, #gen_9, .g9, #gen_10, .g10 {*/
    .g5, .g6, .g7, .g8, .g9, .g10 {
        font-size: 0.7em;
    }

    .m {
        /*border-bottom: 1px dashed black;*/
    }

    .pair, .header {
        border: var(--line-weight) solid black;
    }

    .pair {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }

    .cat {
        padding: 3px;
        flex-grow: 1;
    }

    /*.cat:first-child {
        border: none;
    }*/

    .cat, .details {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .details {
        padding-top: 6px;
    }

    .details p {
        padding-bottom: 3px;
    }

    .champion {
        color: red;
    }

    .name {
        font-weight: bold;
    }

    /*.nameline {
    }*/

    .gccf {
        font-size: smaller;
    }

    .expand {
        font-style: italic;
    }

    .feature {
        font-size: x-small;
        color: grey;
    }

    td .feature {
        font-size: smaller;
        color: black;
    }

    .cat-info {
        border: none;
    }

    #info-table {
        border: none;
        width: 100%;
    }

    #info-table th {
        text-weight: bold;
        width: 10%;
        text-align:right;
    }

    #info-table td {
        width: 20%;
        text-align: left;
        padding: 3px;
        border: none;
    }

    .g1 .cat, .g2 .cat {
        padding: 0 9px;
    }

    .g1 .cat p {
        padding-bottom: 10px;
    }

    .reg, .gems, .expand, .desc, .sex {
        padding-bottom: 2px;
    }

    .sex {
        padding-bottom: 5px;
    }

    .cat_id, .sex_icon {
        display: none;
    }


""" + css_build_grid(depth) + "</style>"


def css_build_grid(depth=5):
    rows = 2 ** depth
    css = f"""
/* FOR CSS GRID */

/*:root {{
--line-weight: 1px;
}}*/

#container {{
    display: grid;
    grid-auto-flow: column;
    grid-template-columns: repeat({depth}, auto);
    grid-template-rows: repeat({rows}, 1fr);

    border: 1px solid black;
    grid-gap: 1px;
    background-color: black;
}}

#container div {{
    display: flex;
    align-items: stretch;
    background-color: white;
}}

"""

    for i in range(1, depth):
        css += f"""
.g{i} {{
    grid-row: span {2 ** (depth - i)};
}}

"""
    return css


def html_template(body, inheader_css, title="pedigree"):
    template = f"""
<html>
<head>
<title>{title}</title>
{inheader_css}
</head>
<body>
{body}
</body>
</html>
"""
    return template


def html_template_css_link(body, css_files=[], title="pedigree"):
    ## NO LONGER IN USE: css now in header to make standalone html
    css_link = ""
    if css_files:
        for file in css_files:
            css_link += f"\n<link rel='stylesheet' type='text/css' href='{file}'>"
    template = f"""
<html>
<head>
<title>{title}</title>
{css_link}
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
    current_dir = get_current_directory()
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
        },

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
        },
    }

def create_db_from_file(source_file):
    raw_cats = create_pedigree_from_file(source_file)
    id_from_name = {cat['name']: id for id, cat in raw_cats.items()}
    return(sub_names_to_ids(raw_cats, id_from_name), id_from_name)

def create_pedigree_from_file(source_file):
    id_count = 1
    loaded_cats = {}
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
                        }}
                        # })
                    loaded_cats.update(cat)
                    id_count += 1
                else:
                    print("Field missing at line:",line)
    loaded_cats.update(add_unknown())
    return loaded_cats


def sub_names_to_ids(cats, id_from_name):
    tmp_cats = cats.copy()
    for id, cat in tmp_cats.items():
        if id < 0:
            continue
        sire_id = id_from_name.get(cat['sire'].strip())
        dam_id = id_from_name.get(cat['dam'].strip())
        cat['sire'] = sire_id
        cat['dam'] = dam_id
    return tmp_cats


def expand_ids_to_names(pedigree, cats):
    return {key:
            [cats[cat_id].get('name') for cat_id in val if cat_id >= 0]
            for key, val in pedigree.items()}


def make_id_key(all_cats):
    return {cat['id']: {key: cat[key] for key in cat if key != "id"} for cat in all_cats}


def get_heirless(cats):
    tmp_cats = cats.copy()
    for id,cat in tmp_cats.items():
        for heir_id in [cat.get('sire'), cat.get('dam')]:
            if heir_id:
                tmp_cats[heir_id]['has_heirs'] = True
    no_heirs = [id for id,cat in tmp_cats.items() if (cat.get("sire") or cat.get("dam")) and not cat.get("has_heirs")]
    return no_heirs

def update_dict(key,val, dict):
    if dict.get(key):
        # dict[key].append(val)
        dict[key].insert(0,val)
    else:
        dict.update({key: [val]})
    return dict


def recurse_pedigree(cat_id, cats, max_generations, curr_generation=0, pedigree={}):
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

def recurse_and_pair(cat_id, cats, max_generations, curr_generation=0, pedigree={}):
    tmp_pedigree = recurse_pedigree(cat_id, cats, max_generations, curr_generation, pedigree)
    return pair_parents(tmp_pedigree)


# def recurse_for_grid(cat_id, cats, max_generations, curr_generation=0, pedigree=None):
## Produces flat list of pairs [ [id, gen], ...] following same order as 'css grid-auto-flow: row'
## (But impossible for humans to parse!)
#     if curr_generation > max_generations:
#         return pedigree
#     if curr_generation == 0:
#         pedigree = [[cat_id,curr_generation]]
#     else:
#         pedigree.append([cat_id,curr_generation])
#     cat = cats[cat_id]
#     for recorded_id, backup_id in [[cat['sire'],-2],[cat['dam'], -1]]:
#         ancestor_id = recorded_id if recorded_id else backup_id
#         recurse_for_grid(ancestor_id, cats, max_generations, curr_generation + 1, pedigree)
#     return pedigree


def build_grid(pedigrees):
    for pedigree in pedigrees:
        grid_html = ""
        header_html = ""
        target_id = None
        ## This works if css grid uses the default "grid-auto-flow: row;"
        # for cat_id, g_id in pedigree.flat:
        #     if g_id == 0:
        #         target_id = cat_id
        #         header_html = build_header(cat_id, pedigree)
        #         continue
        #     grid_html += f"<div class='g{g_id}'>{build_html_cat(g_id, cat_id, pedigree)}</div>\n"
        # grid_html = f"<div id='container'>\n{grid_html}\n</div>"
        for g_id, cat_ids in pedigree.by_gen.items():
            if g_id == 0:
                # target_id = cat_id
                target_id = cat_ids[0][0]
                header_html = build_header(target_id, pedigree)
                continue
            for pairs in cat_ids:
                for cat_id in pairs:
                    grid_html += f"<div class='g{g_id} {pedigree.db.sex[cat_id]}'>{build_html_cat(g_id, cat_id, pedigree)}</div>\n"
        grid_html = f"<div id='container'>\n{grid_html}\n</div>"

        target_name = pedigree.db.cats[target_id]['name']
        html = html_template(header_html + grid_html + build_footer(), css_styles_template(pedigree.depth, pedigree.font_size), f"Pedigree for {target_name}")
        write_html_pedigree(html, f"{target_id}-{target_name.replace(' ', '-')}.html")

def build_header(cat_id, pedigree):
    i = get_display_info(cat_id, pedigree)
    return f"""
<table class="header">
    <tr>
        <td rowspan="2">
        <p class="feature">Breeder:</p>
        <p class="breeder">LONGNAP</p>
        <p class="feature">
        Ms J Sturgess<br>
        5 Catharine Close<br>
        Radley<br>
        ABINGDON<br>
        OX14 3AR
        </p>
        </td>
        <td class="banner">Name: <span class="name">{i["name"]}</span></td>
    </tr>
    <tr>
        <td class="cat-info">
            <table id="info-table" class="feature">
                <tr>
                    <th>Reg no:</th>
                    <td>{i["regnum"]} {i["gccf"]}</td>
                    <th>Date of birth:</th>
                    <td>{i["cat"]["dob"]}</td>
                    <th>Microchip:</th>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <th>Sex:</th>
                    <td>{i["sex"]}</td>
                    <th rowspan="2">GEMS:</th>
                    <td>{i["gems"]}</td>
                    <th>Owner:</th>
                    <td>&nbsp;</td>
                </tr>
                <tr>
                    <th>Status:</th>
                    <td>NonActive</td>
                    <!--<th>&nbsp;</th>-->
                    <td><i>{i["catsplain"]}</i></td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                </tr>
        </table>
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

def build_generic(cat_id, pedigree):
    i = get_display_info(cat_id, pedigree)
    return f"""
<div class="cat">
    <p class="sex">{i["sex"]}</p>
    <p class="nameline{i["awards_class"]}">{i["awards"]}
        {i['name']}
        {i["curr_id"]}
    </p>
    <div class="details">
        <p class="reg"><span class="feature">Reg no: </span>{i["regnum"]}<span</p>
        <p class="gems"><span class="feature">GEMS: </span>{i["gems"]} {i["gccf"]}</span></p>
        <p class="expand">{i["catsplain"]}</p>
    </div>
</div>
"""

def build_gen1(cat_id, pedigree):
    return build_generic(cat_id, pedigree)


def build_gen2(cat_id, pedigree):
    return build_generic(cat_id, pedigree)


def build_gen3(cat_id, pedigree):
    i = get_display_info(cat_id, pedigree)
    return f"""
<div class="cat">
    <p class="nameline{i["awards_class"]}">{i["awards"]}
        {i['name']}
        {i["curr_id"]}
    </p>
    <div class="details">
        <p class="reg"><span class="feature">Reg no: </span>{i["regnum"]}<span</p>
        <p class="gems"><span class="feature">GEMS: </span>{i["gems"]} {i["gccf"]}</span></p>
        <p class="expand">{i["catsplain"]}</p>
    </div>
</div>
"""


def build_gen4(cat_id, pedigree):
    i = get_display_info(cat_id, pedigree)
    return f"""
<div class="cat">
    <p class="nameline{i["awards_class"]}">{i["awards"]}
        {i['name']}
        {i["curr_id"]}
        {i["sex_icon"]}
    </p>
    <p class="desc">{i["regnum"]} {i["gems"]}</p>
</div>
"""


def build_gen5(cat_id, pedigree):
    i = get_display_info(cat_id, pedigree)
    return f"""
<div class='cat'>
    <p class="nameline">{i["awards"]}
        {i['name']}
        {i["curr_id"]}
        {i["sex_icon"]}
        {i["regnum"]} {i["gems"]}
    </p>
</div>
"""


def get_display_info(cat_id, pedigree):
    cat = pedigree.db.cats[cat_id]
    is_dam = pedigree.db.sex[cat_id] == "f"
    sex_icon = "♀" if is_dam else "♂"
    has_awards = cat['cstatus']
    awards_class = " champion" if has_awards else ""
    gccf = cat['gccf']
    gems = cat['gems']
    return {
        "cat": cat,
        "gccf": gccf,
        # "name": cat['name'],
        "name": f"<span class='name{awards_class}' title='id={cat_id}'>{cat['name']}</span>" if cat_id > 0 else f"<i>{cat['name']}</i>",
        "regnum": cat['regnum'],
        "gems": gems,
        "is_dam": is_dam,
        "sex_icon": f"<span class='sex_icon'>{sex_icon}</span>",
        "curr_id": f"<span class='cat_id'>{cat_id}</span>",
        # "sex_icon": '\u2642' if is_dam else '\u2640',
        # "sex_icon": '&#2642;' if is_dam else '&#2640;',
        "sex": "Dam" if is_dam else "Sire",
        "has_awards": has_awards,
        "awards": f"{has_awards} " if has_awards else "",
        "awards_class": awards_class,
        "gccf_text": f" <span class='gccf'>{gccf}</span>" if gccf else "",
        "catsplain": pedigree.db.gems.get(gems, "")
    }


def select_html_template(case, cat_id, pedigree):
    if case < 0 or case > 5:
        case = 5
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
    return func(cat_id, pedigree)


def build_html_cat(g_id, cat_id, pedigree):
    tmp = select_html_template(g_id, cat_id, pedigree)
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
    return lookup

# def reverse_order(pedigrees):
#     tmp = []
#     for pedigree in pedigrees:
#         for i in pedigree:
#             # print(">>", i,pedigrees[i])
#             tmp.append({i:pedigree[i][::-1]})
#         # print(tmp)
#     # return tmp
#     return pedigrees


def pair_parents(pedigree):
    ## This divides ancestors into pairs (sire,dam)
    ## pedigrees = [  [{0: [1]},{1: [6, 5]},{2: [14, 13, 8, 7]}],  [pedigree2 (etc.)]  ]
    tmp = {k:
            [v[i:i+2] for i in range(0, len(v), 2)]
            for k,v in pedigree.items()}
    return tmp

def parse_cmd_line(argv):
    ids = ""
    ## Change these three variables according to needs
    id_list = [1,2,3,4]
    depth = 5
    basefont = 12

    opts, _ = getopt.getopt(argv,"hi:d:s:",["help","ids=", "depth=", "size="])
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print ("""
You can specify the following variables after pedigrees.py
    -h / --help=    <prints this help message>
    -i / --ids=     <comma-separated list of cat ids (NO SPACES)>
                        e.g. -i 2,27 OR --ids=2,27
    -d / --depth=   <depth of generations (4 or 5 is best)>
                        e.g -d 5 OR --depth=5
    -s / --size=    <font size of grid in points (12 is default)>
                        e.g. -s 11 OR --size=11

To print out, use your browser to save or export this file as a pdf.
N.B. There must be ONE .csv file (cat database) in the same folder as this script.
""")
            sys.exit()
        elif opt in ("-i", "--ids"):
            ids = arg
            id_list = [int(id) for id in ids.split(",")]
        elif opt in ("-d", "--depth"):
            depth = int(arg)
        elif opt in ("-s", "--size"):
            basefont = int(arg)
    return(id_list, basefont, depth)


class Db:
    def __init__(self):
        self.cats, self.names = create_db_from_file(retrieve_file_by_suffix())
        self.sex = make_sex_lookup(self.cats)
        self.heirless = get_heirless(self.cats)
        self.gems = make_gems_lookup()


class Pedigree:
    def __init__(self, cat_id, database, settings):
        """
        This does the hard work of recursing through the database
        - by_gen is a human readable version of ancestor pairs by generation
        - flat is the flat list of [id, generation] in the order they were recursed
        since this also happens to be the same order as the css grid is filled,
        we can use it directly to populate the css grid
        (we could use the by_gen with "grid-auto-flow: column" but I discovered this too late!)
        Currently, by_gen isn't used, but I'm loathe to get rid of it as I might revisit
        """
        self.id = cat_id
        self.db = database
        self.depth = settings["depth"]
        self.font_size = settings["font_size"]
        self.by_gen = recurse_and_pair(self.id, self.db.cats, self.depth)
        # self.flat = recurse_for_grid(self.id, self.db.cats, self.depth)


def main(argv):
    settings = dict(zip(("to_print", "font_size", "depth"), parse_cmd_line(argv)))
    db = Db()
    pedigrees = []
    for cat_id in settings["to_print"]:
        cat = db.cats[cat_id]
        print(f"Analysing database to create pedigree for: {cat['name']} (id: {cat_id})")
        # tmp_pedigree = Pedigree(cat_id, db, settings)
        # pedigrees.append(tmp_pedigree)
        pedigrees.append(Pedigree(cat_id, db, settings))
    build_grid(pedigrees)


if __name__ == "__main__":
    main(sys.argv[1:])
