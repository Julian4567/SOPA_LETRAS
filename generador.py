# generador.py
import random
import threading
import string

directions = [
    (0,1),  # right
    (1,0),  # down
    (0,-1), # left
    (-1,0), # up
    (1,1),  # diag down-right
    (1,-1), # diag down-left
    (-1,1), # diag up-right
    (-1,-1) # diag up-left
]

def _place_word_attempt(grid, word, size, lock, positions):
    """
    Try to place 'word' into grid. If successful, write coordinates into positions[word].
    This is intended to be run in its own thread.
    """
    max_attempts = 300
    L = len(word)
    for _ in range(max_attempts):
        dir_r, dir_c = random.choice(directions)
        if dir_r == 0 and dir_c == 0:
            continue
        # choose a random start that fits
        start_r = random.randrange(size)
        start_c = random.randrange(size)
        end_r = start_r + dir_r*(L-1)
        end_c = start_c + dir_c*(L-1)
        if not (0 <= end_r < size and 0 <= end_c < size):
            continue

        # check if fits (allow overlap if same letter)
        can_place = True
        coords = []
        r,c = start_r, start_c
        for ch in word:
            if grid[r][c] != '' and grid[r][c] != ch:
                can_place = False
                break
            coords.append((r,c))
            r += dir_r
            c += dir_c

        if not can_place:
            continue

        # place (with lock)
        with lock:
            for (r,c), ch in zip(coords, word):
                grid[r][c] = ch
            positions[word] = coords
        return True
    # failed to place
    return False

def generate_board(words, size=12):
    """
    words: list of uppercase words
    size: grid size (size x size)
    Returns (grid_as_list_of_lists_of_chars, positions_dict)
    positions_dict: word -> list of (r,c)
    """
    # initialize empty grid
    grid = [['' for _ in range(size)] for _ in range(size)]
    positions = {}
    lock = threading.Lock()
    threads = []

    # shuffle words so longer words tend to be placed first in parallel
    words_sorted = sorted(words, key=lambda w: -len(w))

    for w in words_sorted:
        t = threading.Thread(target=_place_word_attempt, args=(grid, w, size, lock, positions))
        t.start()
        threads.append(t)

    # wait for all threads
    for t in threads:
        t.join()

    # For any word not placed (rare), attempt again single-threaded (deterministic attempts)
    for w in words_sorted:
        if w not in positions:
            _place_word_attempt(grid, w, size, lock, positions)

    # Fill empty cells with random letters
    alphabet = string.ascii_uppercase
    for r in range(size):
        for c in range(size):
            if grid[r][c] == '':
                grid[r][c] = random.choice(alphabet)

    # For sending over socket, turn coords into list of lists (JSON serializable)
    pos_serializable = {}
    for word, coords in positions.items():
        pos_serializable[word] = [list(pair) for pair in coords]

    return grid, pos_serializable
