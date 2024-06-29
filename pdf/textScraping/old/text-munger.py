import os
import sys
import argparse
from pathlib import Path
import csv
from enum import Enum
import pprint
import re

class Field(Enum):
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
   was_blank = 1
   completed = 10



class Item:
   def __init__(self) -> None:
      self.mode = Field.unset
      self.status = Status.in_progress
      self.id = ""
      self.ref = None
      self.artist = ""
      self.title = ""
      self.description = []
      self.literature = []
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
      print("Error: could not read file " + write_file)


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

def clean_items(contents):
  for item in contents:
    text = " ".join(item.text)
    text = text.replace("  ", " ")
    item.text = text

    ids = []
    for line in item.description:
      ids.extend(re.findall(r'[A-Z]{2}\d{4}\.\d+', line))
    item.id = ids
    del item.mode
    del item.status
  return contents






def process_line(line, contents, item_delimiter=None):
  # if contents[-1].status == Status.completed:
  #    return contents
  if not item_delimiter:
     item_delimiter = chr(12)

  if line[0] == item_delimiter:
    contents = start_new_item(contents)
  line = line.strip()
  curr_item = contents[-1]

  match (curr_item.mode, curr_item.status, line):

    case (Field.text, Status.in_progress, line) if not line:
      contents = append_field("text", contents, "\n\n")

    case (_, _, line) if not line:
      contents = register_blank_line(contents)

    case (_, _, line) if line.isnumeric() and not curr_item.ref:
      contents = add_field("ref", contents, line)

    case (Field.ref, Status.was_blank, _) if not curr_item.artist:
      contents = add_field("artist", contents, line)

    case (Field.artist, Status.was_blank, _) if not curr_item.title:
      contents = add_field("title", contents, line)

    case (Field.title, Status.was_blank, _) | (Field.description, Status.in_progress,_):
      contents = append_field("description", contents, line)

    # case (Mode.description, Status.was_blank_line, line) if line.startswith("Literature:"):
    case (_, _, line) if line.startswith("Literature:"):
      contents = append_field("literature", contents, line)

    case (Field.literature, Status.in_progress, _):
      contents = append_field("literature", contents, line)

    case (Field.description | Field.literature, Status.was_blank, _) | (Field.text, _, _):
      contents = append_field("text", contents, line)

    case _:
      contents = append_field("misc", contents, line)

  return contents



def register_blank_line(contents):
    contents[-1].status = Status.was_blank
    print("Blank line")
    return contents

def start_new_item(contents):
  contents[-1].status = Status.completed
  contents.append(Item())
  # print("Starting a new item")
  return contents

def add_field(field, contents, line):
   curr_item = contents[-1]
   setattr(curr_item, field, line)
   curr_item.mode = Field[field]
   curr_item.status = Status.in_progress
  #  print(f"[{field}]: {line}")
   return contents

def append_field(field, contents, line):
   curr_item = contents[-1]
   value = getattr(curr_item, field)
   value.append(line)
   setattr(curr_item, field, value)
   if field != "misc":
      curr_item.mode = Field[field]
   curr_item.status = Status.in_progress
  #  print(f"[{field}]: {line}")
   return contents






if __name__ == '__main__':
  filenames = get_filename("txt")
  if filenames:
    input_filename = filenames[0]
    print(f"Reading: {input_filename}")
    # output_filename = get_file_basename(input_filename, ".out.txt")
    # print(f"Writing to: {output_filename}")
    contents = read_file(input_filename)
    print(f"{len(contents)} items/records found.")
    contents = clean_items(contents)
    for item in contents:
      #  pprint.pp(vars(item))
      print(item.id)
      print(item.text)
      print("")
  else:
     print("Sorry, no files available matching those specs.")