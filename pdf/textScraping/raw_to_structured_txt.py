"""
Takes raw OCR txt file and tries to impose order on it by passing it through
a series of regex substitions.
These should be tailored for each text.

It tries to create a file where:
1) each record is delimited
2) each field / paragraph is separated by a blank line

This structure makes it suitable for passing on to raw_txt_to_csv.py
"""

import os
import sys
import argparse
from pathlib import Path
import csv
from enum import Enum
import pprint
import re
from collections import namedtuple

Sub = namedtuple("Sub", "pattern replace")


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


def read_file(filename):
    try:
        with open(filename, "r") as f:
        #     text = f.readlines()
        # text = [line.rstrip() for line in text]
          text = f.read()
        return text
    except IOError:
        print("Error: could not read file " + filename)


def get_input(file_suffix=None):
  if not file_suffix:
     file_suffix = "txt"
  files = get_filename(file_suffix)
  if files:
    input_filename = files[0]
    print(f"Reading: {input_filename}")
    text = read_file(input_filename)
    return (input_filename, text)
  else:
    print("Sorry, no files available matching those specs.")
    quit()


def get_file_basename(filename, suffix):
  file = Path(filename)
  if suffix and suffix[0] != ".":
    suffix = "." + suffix
  return Path(file.parent, (file.stem + suffix))


def save_txt(input_filename, text):
    output_filename = get_file_basename(input_filename, ".out.txt")
    try:
      with open(output_filename, "w") as f:
        f.write(text)
      print(f"Writing: {output_filename}")
    except IOError:
      print("Error: could not read file " + output_filename)


def apply_re_sequentially(text):


    subs = [
      # Sub(r"\r", r""),
      Sub(r"(\n\d{1,3},\s\d{1,3},\sand\s\d{1,3}\.[^n])",
          r"\n@@OBJECT@@\1"),
      Sub(r"(\n\d{1,3}\sand\s\d{1,3}\.[^\d])",
          r"\n@@OBJECT@@\1"),
      Sub(r"(\n\d{1,3}\.[^\d])",
          r"\n@@OBJECT@@\1"),
      Sub(r"\n\n\n", r"\n@@START@@\n"),
      Sub(r"\n\n", r""),
      Sub(r"@@START@@", r"\n\n@@START@@"),
      # Sub(r"(\n.*[^\n]\n@@OBJECT@@)", r"\n@@TOP@@$1")
      # Sub(r"\n.*[^\n]", r"\n...")
    ]
    for sub in subs:
      #  text = [line.replace(sub.search, sub.replace) for line in text]
      #  text = [re.sub(sub.pattern, sub.replace, line) for line in text]
      text = re.sub(sub.pattern, sub.replace, text)
    return text

if __name__ == '__main__':
  input_filename, text = get_input()
  # contents = categorize_as_dict(contents)
  text = apply_re_sequentially(text)
  save_txt(input_filename, text)
