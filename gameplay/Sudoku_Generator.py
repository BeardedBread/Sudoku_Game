# TODO: Generator currently does not produce unique puzzle, requires rewrite possibly

"""
Module that generates a valid Sudoku Puzzle
Credits for Generator: http://zhangroup.aporc.org/images/files/Paper_3485.pdf
"""
import random
import re
import numpy as np

if __name__ == "__main__":
    import Sudoku_Solver as solver
else:
    from . import Sudoku_Solver as solver

given_regex = re.compile('(?!0)')


def check_for_givens(seq):
    return len([m.start() for m in given_regex.finditer(seq)])-1


def generate_completed_grid(n):
    # Generate a board by randomly picking n cells and
    # fill them a random digit from 1-9
    values = solver.parse_grid('0' * 81)
    valid_assignments = 0
    while valid_assignments < n:
        cell_to_assign = solver.squares[random.randint(0, 80)]
        valid_values = values[cell_to_assign]
        if len(valid_values):
            value_to_assign = valid_values[random.randint(0, len(valid_values) - 1)]
            solver.assign(values, cell_to_assign, value_to_assign)
            valid_assignments += 1

    complete_values = solver.solve(values)
    grid = ''
    for s in solver.squares:
        grid += complete_values[s]

    return grid


def generate_dig_sequence(difficulty):
    if difficulty <= 1:
        random_number = list(range(81))
        while len(random_number) > 0:
            yield random_number.pop(random.randint(0, len(random_number)-1))
    elif difficulty == 2:
        current = 0
        while current < 162:
            actual = current % 81
            row = int(actual / 9)
            if not row % 2:
                yield actual
            else:
                yield (row+1) * 9 - 1 - (actual % 9) % 81
            current += 2
    elif difficulty == 3:
        current = 0
        while current < 81:
            row = int(current / 9)
            if not row % 2:
                yield current
            else:
                yield (row+1) * 9 - 1 - (current % 9)
            current += 1
    elif difficulty == 4:
        current = 0
        while current < 81:
            yield current
            current += 1


def specify_grid_properties(difficulty):
    if difficulty == 0:
        n_givens = random.randint(50, 60)
        lower_bound = 5
    elif difficulty == 1:
        n_givens = random.randint(36, 49)
        lower_bound = 4
    elif difficulty == 2:
        n_givens = random.randint(32, 35)
        lower_bound = 3
    elif difficulty == 3:
        n_givens = random.randint(28, 31)
        lower_bound = 2
    elif difficulty == 4:
        n_givens = random.randint(22, 27)
        lower_bound = 0

    return n_givens, lower_bound


def grid_to_array(grid):
    assert len(grid) == 81
    sudoku_array = np.zeros((9,9), dtype=np.uint8)
    for i in range(81):
        r = int(i / 9)
        c = i % 9
        sudoku_array[r, c] = int(grid[i])

    return sudoku_array


def array_to_grid(sudoku_array):
    assert sudoku_array.shape == (9,9)

    b = [str(num) for num in sudoku_array.reshape((81,))]
    return ''.join(b)


def propagate_array(sudoku_array, N):
    prop_seq = [random.randint(0, 2) for _ in range(N)]

    #prop_seq = [0]
    prev_num = -1
    prev_bigcol = -1
    prev_rot = -1
    swap_choice = ((0, 1), (0, 2), (1, 2))
    #print(prop_seq)
    for num in prop_seq:
        if num == 0:
            rot = random.randint(0, 2)
            if num == prev_num and rot == 2-prev_rot:
                rot += random.randint(1, 2)
                rot %= 3
            sudoku_array[:] = np.rot90(sudoku_array, k=rot+1)
            prev_rot = rot
        elif num == 1:
            choice = random.randint(0, 2)
            if num == prev_num:
                choice += random.randint(1, 2)
                choice %= 3
            swap_bigcol = swap_choice[choice]

            for i in range(3):
                sudoku_array[:, [swap_bigcol[0]*3+i, swap_bigcol[1]*3+i]] \
                    = sudoku_array[:, [swap_bigcol[1] * 3 + i, swap_bigcol[0] * 3 + i]]
        else:
            choice = random.randint(0, 2)
            bigcol_select = random.randint(0, 2)
            if num == prev_num and bigcol_select == prev_bigcol:
                choice += random.randint(1, 2)
                choice %= 3
            swap_col = swap_choice[choice]

            sudoku_array[:, [bigcol_select * 3 + swap_col[0], bigcol_select * 3 + swap_col[1]]] \
                = sudoku_array[:, [bigcol_select * 3 + swap_col[1], bigcol_select * 3 + swap_col[0]]]

            prev_bigcol = bigcol_select

        prev_num = num

    #print('Propagate Complete')


def generate_sudoku_grid(difficulty):
    grid = generate_completed_grid(11)
    n_givens, lower_bound = specify_grid_properties(difficulty)
    dig_sequence = generate_dig_sequence(difficulty)
    holes = 0

    while holes < 81-n_givens:
        try:
            i = next(dig_sequence)
        except StopIteration:
            print("Reach end of Sequence")
            break
        row = int(i / 9) * 9
        col = i % 9
        if check_for_givens(grid[row:row+9]) > lower_bound and\
                check_for_givens(grid[col::9]) > lower_bound:
            current_number = grid[i]
            other_numbers = solver.digits.replace(current_number, '')
            unique = True
            for digit in other_numbers:
                grid_check = grid[:i] + digit + grid[i+1:]
                if solver.solve(solver.parse_grid(grid_check)):
                    unique = False
                    break
            if unique:
                grid = grid[:i] + '0' + grid[i+1:]
                holes += 1

    return grid


def generate_sudoku_puzzle(difficulty):
    grid = generate_sudoku_grid(difficulty)
    print('Difficulty level: ', difficulty, 'Givens: ', check_for_givens(grid))
    sudoku_array = grid_to_array(grid)
    propagate_array(sudoku_array, 18)
    print("Warning: the solution to the puzzle may be non-unique.")
    print('Puzzle: ', array_to_grid(sudoku_array))
    return sudoku_array


if __name__ == "__main__":
    a = generate_sudoku_puzzle(3)
    print(a)
