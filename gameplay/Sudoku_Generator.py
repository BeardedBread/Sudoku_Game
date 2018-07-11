"""
Module that generates a valid Sudoku Puzzle
Credits for Solver : http://norvig.com/sudoku.html
Credits for Generator: http://zhangroup.aporc.org/images/files/Paper_3485.pdf

"""
import random
import re

filledcell = re.compile('(?!0)')

def cross(array1, array2):
    """Cross product of elements in A and elements in B."""
    return [a+b for a in array1 for b in array2]


digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s], []))-set([s]))
             for s in squares)


def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    # To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s, d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False    # (Fail if we can't assign d to square s.)
    return values


def grid_values(grid):
    """Convert grid into a dict of {square: char} with '0' or '.' for empties."""
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))


def display(values):
    """Display these values as a 2-D grid."""
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    print('')


def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(str(d), '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False


def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values   # Already eliminated
    values[s] = values[s].replace(d, '')
    # (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False    # Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    # (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False    # Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values


#def solve(grid): return search(parse_grid(grid))
def solve(values): return search(values)


def search(values):
    """Using depth-first search and propagation, try all possible values."""
    if values is False:
        return False    # Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values   # Solved!
    # Chose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d))
                for d in values[s])


def some(seq):
    """Return some element of seq that is true."""
    for e in seq:
        if e:
            return e
    return False


def las_vegas(n):
    # Generate a board by randomly picking n cells and
    # fill them a random digit from 1-9
    values = parse_grid('0' * 81)
    valid_assignments = 0
    while valid_assignments < n:
        #display(values)
        cell_to_assign = squares[random.randint(0, 80)]
        valid_values = values[cell_to_assign]
        if len(valid_values):
            value_to_assign = valid_values[random.randint(0, len(valid_values)-1)]
            assign(values, cell_to_assign, value_to_assign)
            valid_assignments += 1
    return values


def generate_completed_grid():
    complete_values = solve(las_vegas(11))
    grid = ''
    for s in squares:
        grid += complete_values[s]

    return grid


def generate_dig_sequence(difficulty):
    # TODO: Determine the number of givens and lower bound of given
    if difficulty <= 1:
        random_number = list(range(81))
        while len(random_number) > 0:
            print(len(random_number))
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

def generate_sudoku_puzzle(difficulty):
    grid = generate_completed_grid()

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

    dig_sequence = generate_dig_sequence(difficulty)
    holes = 0

    while holes<81-n_givens:
        try:
            i = next(dig_sequence)
        except StopIteration:
            print("Reach end of Sequence")
            break
        # TODO: Check if givens at current row and column is at lower bound

        # TODO: Dig the current hole and check for uniqueness

    # TODO: Propagate and Output
    return grid


if __name__ == "__main__":
    #print(generate_completed_grid())
    func = generate_dig_sequence(3)
    #print(next(func))
    [print(a) for a in next(func)]