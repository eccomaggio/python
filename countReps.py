# Count the reps of words in a given file
import string

word_freq = {}
# typography = ["\u2018","\u2019", "\u201C", "\u201D"]
typography = "\u2018\u2019\u201C\u201D"
# print(typography)

table = str.maketrans(dict.fromkeys(string.punctuation + typography))
results_table = []

def main():
    with open("./text.txt","r") as f:
        Lines = f.readlines()
        for line in Lines:
            clean_line = line.translate(table)
            # print(f"orig: {line}\nnew:  {clean_line}\n")
            Words = clean_line.split()
            for word in Words:
                if word in word_freq:
                    word_freq[word] += 1
                else:
                    word_freq[word] = 1

    col_max = 3
    col = 0
    row = 0
    for word in sorted(word_freq, key=word_freq.get, reverse=True):
        if word_freq[word] > 1:
            # print(f"row={row}, col={col} > {word}: {word_freq[word]}")
            if col == 0: 
                results_table.append(["","",""])
            results_table[row][col] = f"{word} : {word_freq[word]}"
            col += 1
            if col >= col_max:
                col = 0
                row += 1
            # results_table.append([])
            

    for row in results_table:
        print("{: >20} {: >20} {: >20}".format(*row))

            


if __name__ == "__main__":
    main()
