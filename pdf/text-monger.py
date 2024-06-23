import os
import sys
import argparse
from pathlib import Path

def get_filename(suffix=None):
  """
  Look for filename in cmdline args list
  if found: return filename as list
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

def create_file(filename):
    try:
        with open(filename, "w") as f:
            f.write("Hello, world!\n")
        print("File " + filename + " created successfully.")
    except IOError:
        print("Error: could not create file " + filename)


def read_file(filename):
    try:
        with open(filename, "r") as f:
            contents = f.read()
            contents = transform_text(contents)
            print(contents)
    except IOError:
        print("Error: could not read file " + filename)

def transform_text(text):
   text = text.replace("e", "-")
   return text


if __name__ == '__main__':
  tmp = get_filename("txt")
  # print(tmp)
  if tmp:
    input_filename = tmp[0]
    output_filename = get_file_basename(input_filename, ".out.txt")
    print(input_filename, output_filename)
    contents = read_file(input_filename)
    print(contents)
  else:
     print("Sorry, no files available matching those specs.")