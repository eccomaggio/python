import ocrmypdf
import sharedArgs
from pdfminer.high_level import extract_text


pdf_path = sharedArgs.get_file_from_suffix("pdf")
out_path = sharedArgs.get_file_basename(pdf_path, "_ocr.pdf")
# out_path = pdf_path + "_ocr.pdf"
ocrmypdf.ocr(pdf_path,out_path, deskew=True)
text = extract_text(out_path)
print(text)