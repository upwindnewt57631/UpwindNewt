from time import sleep
from os import system, name
from random import randint

BOARD_LENGTH, BOARD_HEIGHT = 100, 60
SNOW_AMOUNT = 5

def list_to_binary(list):
    return "".join(["".join(map(str, row)) for row in list])

def binary_to_braille(binary):
    # Inspired by https://www.youtube.com/watch?v=RlpQkHBGAs0
    brailleBinary = [int(letter) for letter in binary]

    decimal_value = (
        brailleBinary[0] * 1
        + brailleBinary[1] * 8
        + brailleBinary[2] * 2
        + brailleBinary[3] * 16
        + brailleBinary[4] * 4
        + brailleBinary[5] * 32
        + brailleBinary[6] * 64
        + brailleBinary[7] * 128
    )

    braille_code_point = 0x2800 + decimal_value

    return chr(braille_code_point)


def divide_into_subgrids(grid, subgrid_height, subgrid_length):
    rows = len(grid)
    cols = len(grid[0])

    subgrids = []

    for i in range(0, rows, subgrid_height):
        subrow = []
        for j in range(0, cols, subgrid_length):
            subgrid = [
                row[j : j + subgrid_length] for row in grid[i : i + subgrid_height]
            ]

            # Fill remaining spaces with 0s if the subgrid is smaller than specified
            while len(subgrid) < subgrid_height:
                subgrid.append([0] * subgrid_length)

            for row in subgrid:
                while len(row) < subgrid_length:
                    row.append(0)

            subrow.append(subgrid)

        subgrids.append(subrow)

    return subgrids


def gravity():
    global grid
    falling = False
    for y in range(BOARD_HEIGHT - 2, -1, -1):
        if not all(item == 0 for item in grid[y]):
            for x in range(BOARD_LENGTH):
                try:
                    if grid[y][x] == 1:
                        if grid[y + 1][x] == 0:
                            grid[y][x] = 0
                            grid[y + 1][x] = 1
                            falling = True
                        elif grid[y + 1][x - 1] == 0 and grid[y][x - 1] == 0:
                            grid[y][x] = 0
                            grid[y + 1][x - 1] = 1
                            falling = True
                        elif grid[y + 1][x + 1] == 0 and grid[y][x + 1] == 0:
                            grid[y][x] = 0
                            grid[y + 1][x + 1] = 1
                            falling = True
                except IndexError:
                    pass
    return falling

def count_snow():
    global grid
    return sum([sum(row) for row in grid])

def print_grid():
    subgrids = divide_into_subgrids(grid, 4, 2)

    for subrow in subgrids:
        print(''.join([binary_to_braille(list_to_binary(subgrid)) for subgrid in subrow]))

    print("Snow Count: " + str(count_snow()))
    print("Merry Christmas!")

grid = [[0 for _ in range(BOARD_LENGTH)] for _ in range(BOARD_HEIGHT)]

while True:
    if all(cell == 0 for cell in grid[0]):
        for _ in range(min(SNOW_AMOUNT, BOARD_LENGTH)):
            number = randint(0, BOARD_LENGTH - 1)
            while grid[0][number] == 1:
                number = randint(0, BOARD_LENGTH - 1)
            for i in range(1):
                grid[i][number] = 1

        # for number in [0, BOARD_LENGTH // 2, BOARD_LENGTH - 1]:
        #     grid[0][number] = 1

    if gravity():
        print_grid()
        sleep(0.05)
        system("cls" if name == "nt" else "clear")
        if count_snow() > (BOARD_HEIGHT * BOARD_LENGTH) // 2:
            grid[-1] = [0 for _ in range(BOARD_LENGTH)]
    else:
        for i in range(1, 3):
            grid[-i] = [0 for _ in range(BOARD_LENGTH)]