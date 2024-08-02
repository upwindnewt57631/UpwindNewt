import os
import msvcrt
from random import choice
from time import sleep
import threading
from math import sqrt

GRID_HEIGHT, GRID_WIDTH = 20, 10
printing = False
MAX_LEVEL = 20


def get_key():
    key = msvcrt.getch()
    if key == b"\xe0":
        arrow_key = msvcrt.getch()
        if arrow_key == b"H":
            return "Up Arrow"
        elif arrow_key == b"P":
            return "Down Arrow"
        elif arrow_key == b"K":
            return "Left Arrow"
        elif arrow_key == b"M":
            return "Right Arrow"
    else:
        key = key.decode()
        if key == " ":
            return "Space"
        else:
            return key


def starting_level_input():
    while True:
        level = input(f"What level would you like to start at? <1 - {MAX_LEVEL}>: ")
        if level.isdigit():
            if 1 <= int(level) <= MAX_LEVEL:
                return int(level)
        print("Please try a diffrent input")


def make_info_string():
    global score, GRID_WIDTH, lines, next_pieces, tetrominos, held_piece
    grid_of_grids = []
    for key in next_pieces:
        temp = tetrominos[key][0]
        icon = tetrominos[key]["display_icon"]
        for row in temp:
            while len(row) != 4:
                row.append(0)
        while len(temp) != 4:
            temp.append([0, 0, 0, 0])
        grid_of_grids.append((temp, icon))

    string = ""

    for i in range(4):
        string += "|"
        for part in grid_of_grids:
            string += (
                "".join(
                    [
                        part[1].replace("█", "#") if item == 1 else " "
                        for item in part[0][i]
                    ]
                )
                + " "
            )
        string += "|\n"

    string += "+" + 2 * GRID_WIDTH * "-" + "+" + "\n"

    score_print = "0" * (GRID_WIDTH * 2 - len(str(score)) - 5) + str(score)

    level_print = f"Level: {calculate_level()}" + " " * (
        GRID_WIDTH * 2 - len(f"Level: {calculate_level()}") - 5
    )

    lines_print = f"Lines: {lines}" + " " * (
        GRID_WIDTH * 2 - len(f"Lines: {lines}") - 5
    )

    print_data = (score_print, level_print, lines_print, " " * (GRID_WIDTH * 2 - 5))

    if held_piece == None:
        temp = ([[0, 0, 0, 0] for _ in range(4)], " ")
    else:
        temp = (
            held_piece[0] + [[0, 0, 0, 0] for _ in range(4 - len(held_piece[0]))],
            held_piece[1],
        )

    for i, row in enumerate(temp[0]):
        string += (
            "|"
            + "".join(
                [temp[1].replace("█", "#") if item == 1 else " " for item in row]
                + [" "] * (4 - len(row))
            )
            + "|"
            + print_data[i]
            + "|"
            + "\n"
        )
    for _ in range(4 - len(temp[0])):
        string += ("|    |") + "\n"
    string += "+" + 2 * GRID_WIDTH * "-" + "+"
    return string


def gravity(sleep_time):
    global grid, stop_gravity, can_hold, lines, score, combo, current_level
    while not stop_gravity:
        if not stop_gravity:
            move((0, 1))

        for _ in range(int(sleep_time * 100)):
            if stop_gravity:
                break
            sleep(.01)

        if not is_moving():
            can_hold = True
            add_tetromino(get_data(get_next_key()))
        else:
            for y, row in enumerate(grid):
                if all([item["state"] == "S" for item in row]):
                    grid.pop(y)
                    grid.insert(
                        0, [{"state": "E", "icon": " "} for _ in range(GRID_WIDTH)]
                    )
                    combo += 1
                    lines += 1

            score += [0, 100, 300, 500, 800][combo] * (calculate_level())
            combo = 0

        display_game()


def get_tetromino():
    global tetrominos, next_pieces
    return choice(
        list(item for item in tetrominos.keys() if next_pieces.count(item) <= 1)
    )


def get_icon():
    global grid
    for y in range(len(grid)):
        for x, item in enumerate(grid[y]):
            if item["state"] == "M":
                return item["icon"]


def average(lst):
    return round(sum(lst) / len(lst))


def simulate_free_fall(grid):
    global GRID_HEIGHT, GRID_WIDTH
    y_d = 1

    temp_grid = [[item for item in row] for row in grid]

    while True:
        empty_grid = [
            [{"state": "E", "icon": " "} for _ in range(GRID_WIDTH)]
            for _ in range(GRID_HEIGHT)
        ]

        coords = []
        for y in range(len(temp_grid)):
            for x, item in enumerate(temp_grid[y]):
                if item["state"] == "M":
                    coords.append((x, y))

        if any(coord[1] + y_d > GRID_HEIGHT - 1 for coord in coords):
            return coords

        elif any(
            temp_grid[coord[1] + y_d][coord[0]]["state"] == "S" for coord in coords
        ):
            return coords

        for y in range(len(temp_grid)):
            for x, item in enumerate(temp_grid[y]):
                if item["state"] == "M":
                    empty_grid[y + y_d][x]["state"] = "M"
                else:
                    if empty_grid[y][x]["state"] != "M":
                        empty_grid[y][x] = {
                            "state": temp_grid[y][x]["state"],
                            "icon": "",
                        }

        temp_grid = empty_grid


def move(direction):
    global grid, GRID_HEIGHT, GRID_WIDTH, pause_gravity, gravity_thread
    x_d, y_d = direction

    icon = get_icon()
    coords = get_coords()

    if x_d < 0 and any(row[0]["state"] == "M" for row in grid):
        return
    elif x_d > 0 and any(row[-1]["state"] == "M" for row in grid):
        return
    elif any(coord[0] + x_d < 0 or coord[0] + x_d > GRID_WIDTH - 1 for coord in coords):
        return
    elif any(grid[coord[1]][coord[0] + x_d]["state"] == "S" for coord in coords):
        return

    solid_grid = [
        [
            (
                {"state": "S", "icon": pixel["icon"]}
                if pixel["state"] != "E"
                else {"state": "E", "icon": " "}
            )
            for pixel in row
        ]
        for row in grid
    ]

    if any(coord[1] + y_d > GRID_HEIGHT - 1 for coord in coords):
        grid = solid_grid
        return
    elif any(grid[coord[1] + y_d][coord[0]]["state"] == "S" for coord in coords):
        grid = solid_grid
        return

    empty_grid = [
        [{"state": "E", "icon": " "} for _ in range(GRID_WIDTH)]
        for _ in range(GRID_HEIGHT)
    ]

    for y in range(len(grid)):
        for x, item in enumerate(grid[y]):
            if item["state"] == "M":
                empty_grid[y + y_d][x + x_d]["state"] = "M"
                empty_grid[y + y_d][x + x_d]["icon"] = icon
            else:
                if empty_grid[y][x]["state"] != "M":
                    empty_grid[y][x] = {
                        "state": grid[y][x]["state"],
                        "icon": grid[y][x]["icon"],
                    }

    grid = empty_grid

    return None


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def is_moving():
    global grid

    for y in range(len(grid)):
        for x, item in enumerate(grid[y]):
            if item["state"] == "M":
                return True

    return False


def rotate_tetromino(clockwise):
    global grid

    coords = get_coords()

    # find the middle using average
    try:
        avg_x = average([coord[0] for coord in coords])
        avg_y = average([coord[1] for coord in coords])
        "Used a Zero error incase the rotate key is press when a moving tetris pice isnt present"
    except ZeroDivisionError:
        return

    # Calculates new cords for the piece and stores them in a list
    rotated_coords = []
    for x, y in coords:
        if clockwise:
            new_x = round(avg_x - (y - avg_y))
            new_y = round(avg_y + (x - avg_x))
        else:
            new_x = round(avg_x + (y - avg_y))
            new_y = round(avg_y - (x - avg_x))
        rotated_coords.append((new_x, new_y))

    x_offset, y_offset = 0, 0

    for x, y in rotated_coords:
        if y >= GRID_HEIGHT:
            y_offset = -1
        elif y < 0:
            y_offset = 1

        if x >= GRID_WIDTH:
            x_offset = -1
        elif x < 0:
            x_offset = 1

    rotated_coords = [(x + x_offset, y + y_offset) for x, y in rotated_coords]

    # Check if the new coordinates are valid before applying the rotation
    for x, y in rotated_coords:
        if (
            x < 0
            or x >= GRID_WIDTH
            or y < 0
            or y >= GRID_HEIGHT
            or grid[y][x]["state"] == "S"
        ):
            return

    icon = get_icon()

    # Clear the current tetromino from the grid
    grid = [
        [item if item["state"] != "M" else {"state": "E", "icon": " "} for item in row]
        for row in grid
    ]

    # Place the rotated tetromino on the grid
    for x, y in rotated_coords:
        grid[y][x]["state"] = "M"
        grid[y][x]["icon"] = icon


def display_game():
    global grid, GRID_WIDTH, printing

    if not printing:
        printing = True
        static_grid = [[item for item in row] for row in grid]

        if is_moving():
            ghost_coords = simulate_free_fall(static_grid)
        else:
            ghost_coords = []

        for coord in ghost_coords:
            if static_grid[coord[1]][coord[0]]["state"] == "E":
                static_grid[coord[1]][coord[0]] = {"state": "E", "icon": "█"}

        string = ""
        string += ("+" + 2 * GRID_WIDTH * "-" + "+") + "\n"
        for y, row in enumerate(static_grid):
            string += (
                "|"
                + "".join([(item["icon"] * 2) for x, item in enumerate(row)])
                + "|"
                + "\n"
            )

        string += ("+" + 2 * GRID_WIDTH * "-" + "+") + "\n"
        string += make_info_string()
        clear_console()
        print(string)
    printing = False


def get_next_key():
    global tetrominos, next_pieces,pity
    next = next_pieces[-1]
    next_pieces.pop(-1)
    key = get_tetromino()

    if next != "l":
        pity += 1
    else:
        pity = 0
    
    if pity >= 25:
        key = "l"
        pity = 0

    next_pieces.insert(0, key)

    return next


def get_data(key):
    global tetrominos
    return tetrominos[key][0], tetrominos[key]["display_icon"]


def get_coords() -> list[tuple[int, int]]:
    global grid
    coords = []
    for y in range(len(grid)):
        for x, item in enumerate(grid[y]):
            if item["state"] == "M":
                coords.append((x, y))
    return coords


def make_schematic():
    coords = get_coords()
    # gets the smallest number to adjust later
    min_x = min(coords, key=lambda x: x[0])[0]
    min_y = min(coords, key=lambda x: x[1])[1]

    # makes a 2d list of 0s
    schematic = [
        [0 for _ in range(max([x - min_x for x, _ in coords]) + 1)]
        for _ in range(max([y - min_y for _, y in coords]) + 1)
    ]

    # creates coords
    for x, y in coords:
        schematic[y - min_y][x - min_x] = 1

    return schematic, get_icon()


def hold():
    global grid, held_piece, current_piece, can_hold

    if held_piece is None:
        held_piece = make_schematic()
        grid = [
            [
                item if item["state"] != "M" else {"state": "E", "icon": " "}
                for item in row
            ]
            for row in grid
        ]
        current_piece = get_next_key()
        add_tetromino(get_data(current_piece))
    else:
        can_hold = False
        current_piece = make_schematic()
        grid = [
            [
                item if item["state"] != "M" else {"state": "E", "icon": " "}
                for item in row
            ]
            for row in grid
        ]
        add_tetromino(held_piece)
        held_piece = current_piece


def add_tetromino(data):
    global grid, can_hold, ceiling_hit

    temp, icon = data

    current = [
        [
            {"state": "M", "icon": icon} if pixel == 1 else {"state": "E", "icon": " "}
            for pixel in row
        ]
        for row in temp
    ]

    # Calculate the starting position for the new tetromino
    # grid[y][start_position : start_position + len(row)] = row
    start_position = GRID_WIDTH // 2 - 1
    start_position = max(0, min(start_position, GRID_WIDTH - len(current[0])))
    
    for y in range(len(current)):
        for x in range(len(current[y])):
            if current[y][x]["state"] == "M":
                if grid[y][start_position + x]["state"] == "S":
                    grid[y][start_position + x] = current[y][x]
                    ceiling_hit = True
                else:
                    grid[y][start_position + x] = current[y][x]


def paint(text, color):
    colors = {
        "cyan": "\033[0;36m",
        "blue": "\033[0;34m",
        "orange": "\033[0;33m",
        "yellow": "\033[1;33m",
        "green": "\033[0;32m",
        "purple": "\033[0;35m",
        "red": "\033[0;31m",
        "light gray": "\033[0;37m",
    }

    return colors[color] + text + "\033[0m"


tetrominos = {
    "B": {
        "display_icon": paint("█", "yellow"),
        0: [[1, 1], [1, 1]],
    },
    "l": {
        "display_icon": paint("█", "cyan"),
        0: [[1], [1], [1], [1]],
    },
    "T": {
        "display_icon": paint("█", "purple"),
        0: [[0, 1, 0], [1, 1, 1]],
    },
    "L": {
        "display_icon": paint("█", "orange"),
        0: [[1, 1], [0, 1], [0, 1]],
    },
    "J": {
        "display_icon": paint("█", "blue"),
        0: [[1, 1], [1, 0], [1, 0]],
    },
    "Z": {
        "display_icon": paint("█", "green"),
        0: [[1, 1, 0], [0, 1, 1]],
    },
    "S": {
        "display_icon": paint("█", "red"),
        0: [[0, 1, 1], [1, 1, 0]],
    },
}


can_hold = True


def display_score(file_path):
    os.system("cls" if os.name == "nt" else "clear")
    print("+" + 2 * GRID_WIDTH * "-" + "+")
    scores = []

    with open(file_path, "r") as file:
        for _, line in enumerate(file):
            values = line.split(":")
            values = [value.strip(":") for value in values]
            scores.append({"Name": values[1], "Score": int(values[2])})
            print(
                "|"
                + f'{_+1}:{scores[-1]["Name"]}: '
                + "0"
                * (
                    2 * GRID_WIDTH
                    - len(f'{_+1}:{scores[-1]["Name"]}: ')
                    - len(str(scores[-1]["Score"]))
                )
                + str(scores[-1]["Score"])
                + "|"
            )

        for _ in range(_ + 2, 11):
            print(
                "|"
                + f"{_}:------: "
                + "0" * (2 * GRID_WIDTH - len(f"{_}:------: "))
                + "|"
            )

        print("+" + 2 * GRID_WIDTH * "-" + "+")

    return scores


def time_of_gravity():
    return max(0.1, 3 - (sqrt(calculate_level()) / (sqrt(20) / 3)))


def calculate_level():
    global lines, st_level
    min_level = st_level
    return max(lines // 10, min_level)


script_directory = os.path.dirname(__file__)
file_name = "config.txt"
file_path = os.path.join(script_directory, file_name)

try:
    with open(file_path, "r"):
        pass
except FileNotFoundError:
    with open(file_path, "w") as file:
        pass
        file.write(
            """Left:a
Down:s
Right:d
Hold:r
RotateC:e
RotateCC:q
Reset:x
Pause:p
Hard Drop:Space
END OF CONTROLS

Use Up Arrow , Down Arrow , Left Arrow , Right Arrow for arrow keys 
"""
        )
controls = {}

print("Welcome to TETRIS\n")

with open(file_path, "r") as file:
    for line in file:
        line = line.strip("\n")
        if line == "END OF CONTROLS":
            break
        data = line.split(":")
        name, key = data
        print(name+": "+" "*(11-len(name+": "))+key)
        controls[name] = key

print("""
Controls can be changed in your file directory
To Apply Changed Controls, Relaunch this program
""")

st_level = starting_level_input()
grid = [
    [{"state": "E", "icon": " "} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)
]
direction = (0, 0)
score, combo = 0, 0
lines = 0
next_pieces = []
tetromino_key = get_tetromino()
temp = tetrominos[tetromino_key][0]
pity = 0
delay = time_of_gravity()
running = True
pity = 0
next_pieces = [get_tetromino() for _ in range(4)]
play_agian = None
current_level = calculate_level()
key = None
current_piece = None
held_piece = None
ceiling_hit = False
display_game()
add_tetromino(get_data(get_next_key()))
try:
    stop_gravity = False  # Reset the flag
    gravity_thread = threading.Thread(target=gravity, args=(delay,))
    gravity_thread.start()  # Start a new gravity thread

    while running:

        # Inside the game loop, where a new tetromino is selected
        if not is_moving():
            can_hold = True

            add_tetromino(get_data(get_next_key()))

            if ceiling_hit:
                stop_gravity = True
                gravity_thread.join()

                display_game()
                sleep(2)
                clear_console()

                script_directory = os.path.dirname(__file__)
                file_name = "High_Score.txt"
                file_path = os.path.join(script_directory, file_name)

                try:
                    with open(file_path, "r"):
                        pass
                except FileNotFoundError:
                    with open(file_path, "w") as file:
                        pass
                        file.write("1:------: 0")

                scores = display_score(file_path)

                name = input(f"Enter your name for your score of {score} > ")
                name = "".join(letter for letter in name if letter != ":")
                name += "-" * max(6 - len(name), 0)
                name = name[:6]
                scores.append({"Name": name, "Score": score})

                with open(file_path, "w") as file:
                    # Sort the scores in descending order
                    scores = sorted(scores, key=lambda x: x["Score"], reverse=True)

                    scores = scores[: min(len(scores), 10)]

                    for position, data in enumerate(scores):
                        try:
                            file.write(
                                f'{position + 1}:{data["Name"]}:{data["Score"]}\n'
                            )
                        except UnicodeEncodeError:
                            file.write(f'{position + 1}:Error-:{data["Score"]}\n')

                display_score(file_path)
                sleep(1)

                while play_agian not in ["y", "n"]:
                    play_agian = input("Play Agian? [Y/N] > ").lower()
                if play_agian == "y":
                    key = controls["Reset"]
                    scores = []
                    grid = [
                        [{"state": "E", "icon": " "} for _ in range(GRID_WIDTH)]
                        for _ in range(GRID_HEIGHT)
                    ]
                    play_agian = None
                    stop_gravity = False
                else:
                    running = False
        if running and key != controls["Reset"]:
            key = get_key()

        if key == controls["Left"]:
            direction = (-1, 0)
        elif key == controls["Down"]:
            if is_moving():
                score += 1 * (calculate_level())
            direction = (0, 1)
        elif key == controls["Right"]:
            direction = (1, 0)
        elif key == controls["RotateC"]:
            if is_moving():
                rotate_tetromino(True)
            direction = (0, 0)
        elif key == controls["RotateCC"]:
            if is_moving():
                rotate_tetromino(False)
            direction = (0, 0)
        elif key == controls["Reset"]:
            key = None

            grid = [
                [{"state": "E", "icon": " "} for _ in range(GRID_WIDTH)]
                for _ in range(GRID_HEIGHT)
            ]
            score, lines = 0, 0
            direction = (0, 0)
            stop_gravity = True  # Set the flag to stop gravity
            gravity_thread.join()  # Wait for the gravity thread to finish
            st_level = starting_level_input()
            delay = time_of_gravity()
            stop_gravity = False  # Reset the flag
            gravity_thread = threading.Thread(target=gravity, args=(delay,))
            gravity_thread.start()  # Start a new gravity thread
            current_level = calculate_level()
            current_piece = None
            held_piece = None

            next_pieces = [get_tetromino() for _ in range(4)]
            ceiling_hit = False
        elif key == controls["Hold"] and can_hold:
            if is_moving():
                hold()
            direction = (0, 0)
        elif key == controls["Pause"]:
            direction = (0, 0)
            stop_gravity = True  # Set the flag to stop gravity
            gravity_thread.join()  # Wait for the gravity thread to finish
            stop_gravity = False  # Reset the flag
            clear_console()
            print("+" + 2 * GRID_WIDTH * "-" + "+")
            for _ in range(GRID_HEIGHT // 2 - 1):
                print("|" + 2 * GRID_WIDTH * " " + "|")

            print("|" + "ENTER to Unpause".center(GRID_WIDTH * 2) + "|")

            for _ in range(GRID_HEIGHT // 2):
                print("|" + 2 * GRID_WIDTH * " " + "|")

            print("+" + 2 * GRID_WIDTH * "-" + "+")
            print(make_info_string())
            input()
            gravity_thread = threading.Thread(target=gravity, args=(delay,))
            gravity_thread.start()  # Start a new gravity thread

        elif key == controls["Hard Drop"]:
            while is_moving():
                move((0, 1))
                score += 2 * (calculate_level())
        else:
            direction = (0, 0)

        move(direction)
        current_level = calculate_level()
        for y, row in enumerate(grid):
            if all([item["state"] == "S" for item in row]):
                grid.pop(y)
                grid.insert(0, [{"state": "E", "icon": " "} for _ in range(GRID_WIDTH)])
                combo += 1
                lines += 1

        if calculate_level() != current_level:
            stop_gravity = True  # Set the flag to stop gravity
            gravity_thread.join()  # Wait for the gravity thread to finish
            stop_gravity = False  # Reset the flag
            delay = time_of_gravity()
            gravity_thread = threading.Thread(target=gravity, args=(delay,))
            gravity_thread.start()  # Start a new gravity thread

        score += [0, 100, 300, 500, 800][combo] * (calculate_level())
        combo = 0

        if running:
            display_game()
except ZeroDivisionError as error:
    print(error)
finally:
    stop_gravity = True
    gravity_thread.join()

input("Press ENTER to exit")