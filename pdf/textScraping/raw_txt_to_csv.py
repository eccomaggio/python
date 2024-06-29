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
  result = []
  for i, item in enumerate(contents):
    item = [field for field in item if len(field)]
    tmp = {
       "ids": [],
       "notes": "",
       "author": "",
       }
    try:
      tmp["ref"] = item[0][0]
      tmp["artist"] = item[1][0]
      tmp["title"] = item[2][0]
      tmp["description"] = item[3]
      tmp["literature"], tmp["text"] = split_literature_and_text(item)
      tmp["text"], \
      tmp["notes"] = split_notes_from_text(tmp["text"])
      tmp["ids"] = get_ids(tmp["description"], i, tmp["ref"])[0]
      tmp["text"] = run_on_lines(tmp["text"])
      tmp["author"] = get_author_initials(tmp["text"])

      tmp["description"] = list_to_newlines(tmp["description"])
      tmp["literature"] = list_to_newlines(tmp["literature"])
      tmp["notes"] = rebuild_numbered_list(tmp["notes"])
      tmp["text"] = list_to_paragraphs(tmp["text"])
      tmp["notes"] = list_to_paragraphs(tmp["notes"])
    except IndexError:
       print(f"Record {i} has only {len(item)} field(s).")

    result.append(tmp)
  return result





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
  return (field, notes[0])


def get_ids(field, index="n/a", ref="n/a"):
  ids = []
  for line in field:
      ids.extend(re.findall(r'[A-Z]{2}\d{4}\.\d+', line))
  id_count = len(ids)
  if not id_count:
     print(f"No id found for record no.{index + 1}, ref {ref}")
  elif id_count > 1:
     print(f"More than one item for record no.{index + 1}, ref {ref}")
  return ids


def run_on_lines(para_arr):
  if not para_arr:
     return []
  tmp = []
  for para in para_arr:
    tmp.append(" ".join(para).replace("  ", " "))
  return tmp


def list_to_paragraphs(para_arr):
  if not para_arr:
     return ""
  return ("\n\n").join(para_arr)

def list_to_newlines(line_arr):
   if not line_arr:
      return ""
   return("\n".join(line_arr))


def rebuild_numbered_list(line_arr, pattern=None):
  if not line_arr:
     return []
  if not pattern:
     pattern = r"^\d+\."
  # tmp = [""]
  tmp = []
  for line in line_arr:
    match = re.match(pattern, line)
    if match:
       tmp.append(line)
    else:
       tmp_line = tmp[-1] + " " + line
       tmp[-1] = tmp_line.replace("  ", "")
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
    for i,item in enumerate(contents):
       print(i, item["ref"], len(item))

    output_filename = get_file_basename(input_filename, ".out.csv")
    print(f"Writing to: {output_filename}")
    save_dict_as_csv(output_filename, contents)
  else:
     print("Sorry, no files available matching those specs.")
