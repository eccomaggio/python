# from https://realpython.com/command-line-interfaces-python-argparse/
import argparse
import sys
from pathlib import Path

def get_file_from_suffix(suffix=None):
  if not suffix:
     return
  else:
    if suffix[0] != ".":
       suffix = f".{suffix}"
  args_passed = len(sys.argv) > 1

  if args_passed:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument('-f', '--foo', action='store_true')
    args = parser.parse_args()
    tmp = Path(args.filename)

  pdf_file_name = None
  # print(args.filename, Path.exists(tmp), Path.is_file(tmp))
  if args_passed and Path.is_file(tmp):
      pdf_file_name = tmp
  else:
    pdfs_in_home = [file for file in Path.cwd().iterdir() if file.suffix.lower() == ".pdf"]
    if len(pdfs_in_home):
      pdf_file_name = pdfs_in_home[0]
    # for pdf in pdfs_in_home:
    #     print(pdf.name)
  return pdf_file_name


def get_file_basename(filename, suffix):
   file = Path(filename)
   if suffix and suffix[0] != ".":
      suffix = "." + suffix
  #  print(file.parent, file.stem, file.suffix)
   return Path(file.parent, (file.stem + suffix))



# pdf = get_file_from_suffix("pdf")
# print(pdf) if pdf else print("nowt")

