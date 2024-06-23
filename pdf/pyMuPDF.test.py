# from https://pymupdf.readthedocs.io/en/latest/recipes-ocr.html
import pymupdf
# import pytesseract
import sharedArgs
from pathlib import Path
import sys
import os

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

def read_text(pdf):
    out_file = "pyMuPDF.out.txt"
    # tessdata = os.getenv("TESSDATA_PREFIX")
    # if not tessdata:
    #     tessdata = "/usr/local/Cellar/tesseract/5.4.1/share/tessdata"
    # print(f"Is the TESSDATA_PREFIX environmental variable set? {pymupdf.get_tessdata()}")
    MODE = "tess"

    # if MODE == "write1":
    #     print(f"mode = {MODE}")
    #     doc = pymupdf.open(pdf)
    #     out = open(out_file, "wb")
    #     for page in doc:
    #         text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
    #         out.write(text)
    #         out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
    #     out.close()

    # elif MODE == "write2":

    if MODE == "write":
        print(f"mode = {MODE}")
        with pymupdf.open(pdf) as doc:
            text = chr(12).join([page.get_text() for page in doc])
        Path(out_file).write_bytes(text.encode()) # write as a binary file to support non-ASCII characters

    elif MODE == "ocr":
        print(f"mode = {MODE}")
        tessdata = os.getenv("TESSDATA_PREFIX")
        if not tessdata:
            tessdata = "/usr/local/Cellar/tesseract/5.4.1/share/tessdata"
        with pymupdf.open(pdf) as doc:
            for page in doc:
                text = page.get_textpage_ocr(flags=3, language='eng', dpi=72, full=False, tessdata=tessdata).extractText()
                print(text)

    elif MODE == "tess":
        # pytesseract.pytesseract.tesseract_cmd = (tessdata)
        with pymupdf.open(pdf) as doc:
            for page in doc:
                text = pytesseract.image_to_string(page)
                text += "\n"
                print(text)

    else:
        print("Ooops. Mode not recognized.")


if pdf_file_name:= sharedArgs.get_file_from_suffix("pdf"):
    print(f"Reading file: {pdf_file_name}")
    read_text(pdf_file_name)
else:
    print("no pdf file available")

quit()
