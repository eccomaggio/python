"""
Rough implementation of John Horton Conway's "Game of Life" (https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life), implementing the four rules:
1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
2. Any live cell with two or three live neighbours lives on to the next generation.
3. Any live cell with more than three live neighbours dies, as if by overpopulation.
4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.

Implemented using arr[x][y], assuming 0,0 = top left of screen.
"""

import sys
import os
import time

countdown = 500
delta = 0.05

cols, rows = (70, 20)
arr = [[0 for _ in range(cols)] for _ in range(rows)]
tmpArr = [[0 for _ in range(cols)] for _ in range(rows)]

Xseed = """
01111111101111100011100000011111110111110
"""
XXseed = """
111111
01111011111111111110011
111111
"""

seed = """
00000000000000000000000001
00000000000000000000000101
0000000000000110000001100000000000011
0000000000001000100001100000000000011
01100000000100000100011
0110000000010001010001110000101
0000000000010000010001110000001
00000000000010001
000000000000011
"""

# seedling = [[int(i) for i in line] for line in seed.strip().split("\n")]
# if len(set([len(i) for i in seedling])) > 1:
#    raise Exception("All lines in the seed must be the same")
try:
    seedling = [[int(i) for i in line.strip()] for line in seed.strip().split("\n")]
except Exception:
    print("ERROR: Your string seed pattern should only contain 1s and 0s.")
    sys.exit(1)

sRows, sCols = len(seedling), len(seedling[0])
insertCol, insertRow = round((cols - sCols) / 2), round((rows - sRows) / 2)
for i in range(sRows):
    # arr[insertRow + i][insertCol : insertCol + sCols] = seedling[i]
    arr[insertRow + i][insertCol : insertCol + len(seedling[i])] = seedling[i]

endRow = "|\n"
spacer = " " * 8
xAxis = "".join(map(str, [i % 10 for i in range(cols)]))


def main_loop():

    for turns in range(countdown):

        print("Press CTRL-c to quit.\n")

        grid = (
            "T: " + f"{countdown - turns}".ljust(4) + xAxis.replace("0", " ") + endRow
        )
        for r in range(rows):
            grid += f"row {str(r).ljust(2)} |"
            for c in range(cols):
                grid += "." if arr[r][c] == 0 else "@"
            grid += endRow
        print(grid)
        print("Press CTRL-c to quit.\n")

        if countdown > 1:
            time.sleep(delta)
            os.system("clear")

        for col in range(cols):
            min_col = (col - 1) if col > 0 else (cols - 1)
            max_col = (col + 1) if col < (cols - 1) else 0
            for row in range(rows):
                min_row = (row - 1) if row > 0 else (rows - 1)
                max_row = (row + 1) if row < (rows - 1) else 0

                neighbours = 0
                neighbours = sum(
                    [
                        arr[min_row][min_col],
                        arr[min_row][col],
                        arr[min_row][max_col],
                        arr[row][min_col],
                        arr[row][max_col],
                        arr[max_row][min_col],
                        arr[max_row][col],
                        arr[max_row][max_col],
                    ]
                )

                if arr[row][col] == 1:
                    if neighbours < 2 or neighbours > 3:
                        tmpArr[row][col] = 0
                    else:
                        tmpArr[row][col] = 1
                elif neighbours == 3:
                    tmpArr[row][col] = 1
                else:
                    tmpArr[row][col] = 0

        for col in range(cols):
            for row in range(rows):
                arr[row][col] = tmpArr[row][col]


try:
    main_loop()
except KeyboardInterrupt:
    print(f"\nYou interrupted the program {countdown * delta} seconds into the run.")
    sys.exit(1)
