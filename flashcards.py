import html

"""
Takes a text file containing vocab: lemma_pinyin_gloss

with thanks to https://stackabuse.com/read-a-file-line-by-line-in-python/ 
"""


def list_entries_in_file(source_file):
    with open(source_file, "r", encoding="utf-8") as f:
        for line, curr_line in enumerate(f):
            if curr_line[0] != "#" or curr_line.strip().len() > 0:
                entry = curr_line.split("_")
                if len(entry) == 3:
                    flashcards[entry[0]] = (entry[1],entry[2].strip())
                else:
                    print("problem at line:",line)

source_file="vocab.txt"
flashcards = {}
list_entries_in_file(source_file)
print(flashcards)
