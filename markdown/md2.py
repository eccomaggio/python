"""
    go through .txt
    identify unit numbers (#)
    add as prefix to all relevant lines
    group & associate correctly
    deal with macrons (i.e. create lookup without them; use ":" internally? strip out if ignoring macros; replace with macros for display?)

"""
from pprint import pprint
from dataclasses import dataclass
from pathlib import Path
import sys
import getopt
import json
import csv
import re


def get_current_directory():
    return Path( __file__ ).parent.absolute()

def read_json(filename):
    file_address = Path(get_current_directory() / filename)
    with open(file_address, "r")as f:
        data = json.load(f)
    return data

def write_json_file(lines, filename="latin.json"):
    file_address = Path(get_current_directory() / filename)
    with open(file_address, "w") as f:
        json.dump(lines,f)



def read_csv_file(filename, separator=","):
    tmp = []
    file_address = Path(get_current_directory() / filename)
    print(f"\n\nOpening <{file_address.name}> to create pedigree...\n")
    with open(file_address, "r") as f:
        csv_reader = csv.reader(f, delimiter=separator)
        for row in csv_reader:
            # print("csv:",row)
            tmp.append(row)
    return tmp

def write_csv_file(data, filename, separator=","):
    file_address = Path(get_current_directory() / filename)
    with open(file_address, "w") as f:
        # csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer = csv.writer(f, delimiter=separator)
        csv_writer.writerows(data)



def retrieve_file_by_suffix(suffix="csv"):
    if suffix[0] == ".":
        suffix = suffix[1:]
    current_dir = get_current_directory()
    for full_path in sorted(current_dir.glob(f"*.{suffix}")):
        file_address = Path(current_dir / full_path.name)
        print(f"\n\nOpening <{file_address.name}> to create pedigree...\n")
        return file_address


# def parse_cmd_line(argv):
#     ids = ""
#     ## Change these three variables according to needs
#     id_list = [1,2,3,4]
#     depth = 5
#     basefont = 12

#     opts, _ = getopt.getopt(argv,"hi:d:s:",["help","ids=", "depth=", "size="])
#     for opt, arg in opts:
#         if opt in ("-h", "--help"):
#             print ("""
# You can specify the following variables after pedigrees.py
#     -h / --help=    <prints this help message>
#     -i / --ids=     <comma-separated list of cat ids (NO SPACES)>
#                         e.g. -i 2,27 OR --ids=2,27
#     -d / --depth=   <depth of generations (4 or 5 is best)>
#                         e.g -d 5 OR --depth=5
#     -s / --size=    <font size of grid in points (12 is default)>
#                         e.g. -s 11 OR --size=11

# To print out, use your browser to save or export this file as a pdf.
# N.B. There must be ONE .csv file (cat database) in the same folder as this script.
# """)
#             sys.exit()
#         elif opt in ("-i", "--ids"):
#             ids = arg
#             id_list = [int(id) for id in ids.split(",")]
#         elif opt in ("-d", "--depth"):
#             depth = int(arg)
#         elif opt in ("-s", "--size"):
#             basefont = int(arg)
#     return(id_list, basefont, depth)


# class Db:
#     def __init__(self):
#         self.lemmas = create_list_from_file(retrieve_file_by_suffix())

# def read_in_data(source_file):
#     with open(source_file, mode="r") as f:
#         lines = []
#         prev = ""
#         # curr = ""
#         curr = f.readline()
#         tsugi = ""

#         count = 0
#         while f:
#             # if count == 0:
#             #     curr = f.readline()
#             # else:
#             #     prev = "3" + curr
#             #     curr = "2" + tsugi
#             # tsugi = "1" + f.readline()
#             prev, curr, tsugi = curr, tsugi, f.readline().rstrip()
#             lines.append(prev)
#             if tsugi == "1":
#                 break
#             count +=1
#     return lines

class Line:
    def __init__(self, prev, curr, read_from_file) -> None:
        self.prev = prev
        self.curr = curr
        self.tsugi = read_from_file
        self.result = []
        self.count = 0

    def update(self, raw_line):
        self.prev, self.curr, self.tsugi = self.curr, self.tsugi, raw_line
        self.count += 1
        return self

    def get_next_line(self, file):
        try:
            line = next(file).rstrip()
        except Exception:
            # line = -1
            line = None
        print("line:", line)
        self.update(line)
        return self



def read_in_data(source_file, lines=[]):
    with open(source_file, mode="r") as f:
        context = Line("", "", "")
        while f:
            context.get_next_line(f)
            process_line(context)
            # lines.append(f"{context.count} >> {context.curr}")
            lines.append(f"{context.count} >> {context.result}")
            if context.tsugi == None:
                break
    return lines



def process_line(context):
    if context.curr.startswith("#"):
        heading(context)
    else:
        text(context)
    # return context




def text(context):
    context.result = ["text", context.curr]
    # return context

def heading(context):
    depth = re.match("#+", context.curr).span()[1]
    context.result = [f"h{depth}", context.curr[depth:]]
    # return context

def bold(context):
    pass

def code_block(context):
    context.result = ["cblock", context.curr[3:]]
    is_in_cblock = True
    def cb(line, context)

# def main(argv):
def main():
    """

    """
    in_file = "sample.md"
    lines = read_in_data(Path(get_current_directory() / in_file))
    for line in lines:
        print(line[:50])





if __name__ == "__main__":
    # main(sys.argv[1:])
    main()

