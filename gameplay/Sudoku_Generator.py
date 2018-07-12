"""
Module that generates a valid Sudoku Puzzle
Credits for Solver : http://norvig.com/sudoku.html
Credits for Generator: http://zhangroup.aporc.org/images/files/Paper_3485.pdf

"""
import random
import re

#from . import Sudoku_Solver as solver
import Sudoku_Solver as solver

filledcell = re.compile('(?!0)')

def check_for_nonzeros(seq):
    return len([m.start() for m in filledcell.finditer(seq)])


def generate_completed_grid(n):
    # Generate a board by randomly picking n cells and
    # fill them a random digit from 1-9
    values = solver.parse_grid('0' * 81)
    valid_assignments = 0
    while valid_assignments < n:
        # display(values)
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
    # TODO: Determine the number of givens and lower bound of given
    if difficulty <= 1:
        random_number = list(range(81))
        while len(random_number) > 0:
            #print(len(random_number))
            yield random_number.pop(random.randint(0, len(random_number)-1))
    elif difficulty == 2:
        current = 0
        while current < 81:
            row = int(current / 9)
            if not row % 2:
                yield current
            else:
                yield (row+1) * 9 - 1 - (current % 9)
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


def generate_sudoku_puzzle(difficulty):
    grid = generate_completed_grid(11)
    n_givens, lower_bound = specify_grid_properties()
    dig_sequence = generate_dig_sequence(difficulty)
    holes = 0

    while holes < 81-n_givens:
        try:
            i = next(dig_sequence)
        except StopIteration:
            print("Reach end of Sequence")
            break
        row = i % 9
        if check_for_nonzeros(grid[row:row+9]) > lower_bound:
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
    # TODO: Propagate and Output
    return grid


if __name__ == "__main__":
    puzzle = generate_sudoku_puzzle(4)
    print(check_for_nonzeros(puzzle))

    solver.display_grid(puzzle)
    solver.display(solver.solve(solver.parse_grid(puzzle)))
