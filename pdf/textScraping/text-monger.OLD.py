import os
import sys
import argparse
from pathlib import Path
import csv
from enum import Enum
import pprint

class Mode(Enum):
  # Mode keeps a record of the most recently found/added field
  unset = 0
  ref = 1
  artist = 2
  title = 3
  description = 4
  literature = 5
  text = 6
  p = 7
  note = 8
  id = 9
  # misc = 10

class Status(Enum):
   in_progress = 0
   was_blank_line = 1
   completed = 10



class Item:
   def __init__(self) -> None:
      self.mode = Mode.unset
      self.status = Status.in_progress
      self.id = ""
      self.ref = None
      self.artist = ""
      self.title = ""
      self.description = []
      self.literature = ""
      self.text = []
      self.misc = []

def get_filename(suffix=None):
  """
  Look for filename in cmdline args list
  if found: return filename as list with one element
  else check for suffix
  if found: return list of all files in current dir with that suffix
  if no arg or suffix, return empty list
  """
  filenames = []
  if len(sys.argv) > 1:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument('-q', '--qqq', action='store_true')
    args = parser.parse_args()
    # print(">>>>>>>", args)
    # maybe add explicit check for suffixes instead of full filename here & act accordingly
    # currently does this by accident!!
    tmp = Path(args.filename)
    if Path.is_file(tmp):
        filenames = [tmp]

  if suffix and not filenames:
    if suffix[0] != ".":
        suffix = f".{suffix}"
    filenames = [file.name for file in Path.cwd().iterdir() if file.suffix.lower() == suffix]
  return filenames


def get_file_basename(filename, suffix):
   file = Path(filename)
   if suffix and suffix[0] != ".":
      suffix = "." + suffix
  #  print(file.parent, file.stem, file.suffix)
   return Path(file.parent, (file.stem + suffix))


def save_as_delimited_file(write_file, delimiter=None):
  if not delimiter:
    delimiter = ","
    try:
      with open(write_file , newline='', encoding='utf-8', delimiter=delimiter) as f:
          reader = csv.reader(f)
          for row in reader:
              print(row)
    except IOError:
      print("Error: could not read file " + filename)


# def create_file(filename):
#     try:
#         with open(filename, "w") as f:
#             f.write("Hello, world!\n")
#         print("File " + filename + " created successfully.")
#     except IOError:
#         print("Error: could not create file " + filename)


def read_file(filename):
  contents = []
  try:
      with open(filename, "r") as f:
        contents.append(Item())
        for line in f:
            # contents = process_line(line, contents)
            process_line(line, contents)
  except IOError:
      print("Error: could not read file " + filename)
  return contents







def process_line(line, contents, item_delimiter=None):
  if contents[-1].status == Status.completed:
     return contents

  if not item_delimiter:
     item_delimiter = chr(12)

  if line[0] == item_delimiter:
    contents = start_new_item(contents)

  line = line.strip()
  curr_item = contents[-1]

  match (curr_item.mode, curr_item.status, line):

    case (Mode.text, Status.in_progress, line) if not line:
      contents = append_field("text", contents, "\n")

    case (_, _, line) if not line:
      contents = register_blank_line(contents)

    case (_, _, line) if line.isnumeric():
      contents = add_field("ref", contents, line)

    case (Mode.ref, Status.was_blank_line, _):
      contents = add_field("artist", contents, line)

    case (Mode.artist, Status.was_blank_line, _):
      contents = add_field("title", contents, line)

    case (Mode.title, Status.was_blank_line, _) | (Mode.description, Status.in_progress,_):
      contents = append_field("description", contents, line)

    # case (Mode.description, Status.was_blank_line, line) if line.startswith("Literature:"):
    case (_, _, line) if line.startswith("Literature:"):
      contents = add_field("literature", contents, line)

    case (Mode.description | Mode.literature, Status.was_blank_line, _) | (Mode.text, _, _):
      contents = append_field("text", contents, line)

    case _:
      contents = append_field("misc", contents, line)
      # curr_item.status = Status.in_progress

  return contents




def register_blank_line(contents):
    contents[-1].status = Status.was_blank_line
    print("Blank line")
    return contents

def start_new_item(contents):
  contents[-1].status = Status.completed
  contents.append(Item())
  print("Starting a new item")
  return contents

def add_field(field, contents, line):
   curr_item = contents[-1]
   setattr(curr_item, field, line)
   curr_item.mode = Mode[field]
   curr_item.status = Status.in_progress
   print(f"[{field}]: {line}")
   return contents

def append_field(field, contents, line):
   curr_item = contents[-1]
   value = getattr(curr_item, field)
   value.append(line)
   setattr(curr_item, field, value)
   if field != "misc":
      curr_item.mode = Mode[field]
   curr_item.status = Status.in_progress
   print(f"[{field}]: {line}")
   return contents




# def process_lineOLD(line, contents, item_delimiter=None):
#   if not item_delimiter:
#      item_delimiter = chr(12)

#   curr_item = contents[-1]
#   # print(f"{len(line)} <{ord(line[0])}> {line}")
#   # if curr_item.status == Status.completed:
#   #   print("!! already finished!")
#   #   return contents

#   if line[0] == item_delimiter:
#     contents = start_new_item(contents)

#   line = line.strip()
#   if not line:
#     return register_blank_line(contents)

#   elif line.isnumeric():
#     contents = add_field("ref", contents, line)

#   elif curr_item.mode == Mode.ref:
#     contents = add_field("artist", contents, line)

#   elif curr_item.mode == Mode.artist:
#     contents = add_field("title", contents, line)

#   elif curr_item.mode == Mode.title and curr_item.status == Status.was_blank_line:
#     contents = add_field("description", contents, line)

#   elif curr_item.mode == Mode.description and curr_item.status == Status.was_blank_line and line.startswith("Literature:"):
#     contents = add_field("literature", contents, line)

#   elif (curr_item.mode == Mode.description or curr_item.mode == Mode.literature) and curr_item.status == Status.was_blank_line:
#     contents = add_field("text", contents, line)

#   else:
#     print("Chugging on...")
#     curr_item.status = Status.in_progress

#   return contents
# def add_field(field, contents, line):
#    curr_item = contents[-1]
#    curr_item[field] = line
#    curr_item.mode = Mode[field]
#    curr_item.status = Status.in_progress
#    print(f"Adding {field}")
#    return contents


# def add_ref(contents, number):
#   curr_item = contents[-1]
#   curr_item.ref = number
#   curr_item.mode = Mode.ref
#   print("Adding ref")
#   return contents

# def add_artist(contents, number):
#   curr_item = contents[-1]
#   curr_item.ref = number
#   curr_item.mode = Mode.artist
#   print("Adding artist")
#   return contents

# def add_title(contents, number):
#   curr_item = contents[-1]
#   curr_item.ref = number
#   curr_item.mode = Mode.title
#   print("Adding id")
#   return contents


if __name__ == '__main__':
  filenames = get_filename("txt")
  if filenames:
    input_filename = filenames[0]
    print(f"Reading: {input_filename}")
    # output_filename = get_file_basename(input_filename, ".out.txt")
    # print(f"Writing to: {output_filename}")
    contents = read_file(input_filename)
    print(f"{len(contents)} items/records found.")
    # for item in contents:
    #    pprint.pp(vars(item))
    #    print("")
    # print("hello")
  else:
     print("Sorry, no files available matching those specs.")