"""
Module that generates a valid Sudoku Puzzle
Credits for Solver : http://norvig.com/sudoku.html
Credits for Generator: http://zhangroup.aporc.org/images/files/Paper_3485.pdf

"""
import random

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


def dig_holes(board, difficulty):
    # Empty out some cells in a completed board
    pass
    # TODO: Determine the number of givens and lower bound of given

    # TODO: Determine the sequence of digging

    # TODO: Set all cells as "Can be Dug"

    # TODO: Is there a cell that can be dug?

    # TODO: Select the next cell that "can be dug"and Yield unique solution?

    # TODO: Propagate and Output


def generate_sudoku_puzzle(difficulty):
    grid = generate_completed_grid()

    puzzle = dig_holes(board, difficulty)

    return puzzle


if __name__ == "__main__":
    #print(generate_completed_grid())
    success = True
    for i in range(500):
        if not parse_grid(generate_completed_grid()):
            print("failed at test" + str(i))
            success = False
    print(success)