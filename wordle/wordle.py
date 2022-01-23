import pprint as pretty

cols,rows = 5,6
key = list("robot")
guess = [["" for c in range(cols)] for r in range(rows)]
guess[0] = ["p","o","r","k","o"]
report = [[0 for c in range(cols)] for r in range(rows)]


def check_guess(guess_no,guess_line,key):
    curr_line = []
    ## make copy of answer
    ## remove a correct guess to hide repeated letters
    tmp_key = [i for i in key]
    for i,letter in enumerate(guess_line):
        status = 0
        if letter == tmp_key[i]: 
            status = 2
            tmp_key[i] = " "
        elif letter in tmp_key:
            status = 1
            tmp_key[tmp_key.index(letter)] = " "
        curr_line.append(status)
    return curr_line

pretty.pprint(key)
pretty.pprint(guess)
line = 0
report[line] = check_guess(0,guess[line],key)
pretty.pprint(report)
