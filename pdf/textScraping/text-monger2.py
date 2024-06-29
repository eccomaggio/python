import os
import sys
import argparse
from pathlib import Path
import csv
from enum import Enum
import pprint
import re


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


# def save_as_delimited_file(write_file, delimiter=None):
#   if not delimiter:
#     delimiter = ","
#     try:
#       with open(write_file , newline='', encoding='utf-8', delimiter=delimiter) as f:
#           reader = csv.reader(f)
#           for row in reader:
#               print(row)
#     except IOError:
#       print("Error: could not read file " + write_file)

def save_dict_as_csv(filename, dictionary, delimiter=None):
  if not delimiter:
    delimiter = ","
  try:
    with open(filename, "w") as f:
      writer = csv.DictWriter(f, fieldnames=dictionary[0].keys())
      writer.writeheader()
      writer.writerows(dictionary)
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
            contents = []
            for line in f:
                contents = chunk_line(line, contents)
    except IOError:
        print("Error: could not read file " + filename)
    return contents


def chunk_line(line, contents, item_delimiter=None):
    if not item_delimiter:
        item_delimiter = chr(12)

    match (line):
      case line if line.startswith(item_delimiter):
        contents.append([[]])
        line = line.strip()
      case line if len(line) == 1:
        contents[-1].append([])
      case _:
          contents[-1][-1].append(line.strip())
    return contents

def categorize_as_dict(contents):
  tmp = []
  for i, item in enumerate(contents):
    print(i)
    item = [field for field in item if len(field)]
    tmp_dict = {
       "ids": [],
       "notes": "",
       "author": "",
       }
    try:
      tmp_dict["ref"] = item[0][0]
      tmp_dict["artist"] = item[1][0]
      tmp_dict["title"] = item[2][0]
      tmp_dict["description"] = item[3]
      tmp_dict["literature"], tmp_dict["text"] = split_literature_and_text(item)
      tmp_dict["text"], tmp_dict["notes"] = split_notes_from_text(tmp_dict["text"])
      tmp_dict["ids"] = get_ids(tmp_dict["description"])
      tmp_dict["text"] = run_on_lines(tmp_dict["text"])
      tmp_dict["author"] = get_author_initials(tmp_dict["text"])
    except IndexError:
       print(f"Record {i} has only {len(item)} field(s).")

    tmp.append(tmp_dict)
  return tmp


def split_literature_and_text(item):
  literature = []
  text = []
  if item[4][0].startswith("Literature:"):
    literature = item[4]
    text = item[5:]
  else:
    text = item[4:]
  return (literature, text)

def split_notes_from_text(field, notes_identifier=None):
  if not notes_identifier:
    notes_identifier = "1."
  notes = []

  note_start = -1
  for j, line in enumerate(field):
    if len(line) and line[0].startswith(notes_identifier):
      note_start = j
  if note_start >= 0:
      notes = field[note_start:]
      field = field[:note_start]
  return (field, notes)

def get_ids(field):
  ids = []
  for line in field:
      ids.extend(re.findall(r'[A-Z]{2}\d{4}\.\d+', line))
  return ids

def run_on_lines(para_arr):
  tmp = []
  for para in para_arr:
    tmp.append(" ".join(para).replace("  ", " "))
  return tmp

def get_author_initials(field):
   initials = ""
   tmp = re.search(r" [A-Z]+$", field[-1])
   if tmp:
      initials = tmp.group(0).strip()
   return initials


if __name__ == '__main__':
  filenames = get_filename("txt")
  if filenames:
    input_filename = filenames[0]
    print(f"Reading: {input_filename}")

    contents = read_file(input_filename)
    contents = categorize_as_dict(contents)
    # pprint.pp(contents)
    print(f"{len(contents)} items/records found.")

    output_filename = get_file_basename(input_filename, ".out.txt")
    print(f"Writing to: {output_filename}")
    save_dict_as_csv(output_filename, contents)
  else:
     print("Sorry, no files available matching those specs.")
