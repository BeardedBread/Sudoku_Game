import numpy as np
from . import Sudoku_Generator as SdkGen

EMPTY = 0
VALID = 1
INVALID = 2
FIXED = 3

TESTING = False
if __name__ == "__main__":
    test_dir = './test_board.txt'
else:
    test_dir = './gameplay/test_board.txt'


class SudokuSystem:

    def __init__(self):
        self.number_grid = np.zeros((9, 9), dtype=np.uint8)
        self.cell_status = np.zeros((9, 9), dtype=np.uint8)
        self.scribbles = np.zeros((9, 9), dtype='<U9')
        self.offending_cells = []
        for i in range(9):
            row = []
            for j in range(9):
                row.append([])
            self.offending_cells.append(row)

    def clear_grid(self):
        self.number_grid[:] = 0
        self.cell_status[:] = FIXED
        self.scribbles[:] = ''
        for i in range(9):
            for j in range(9):
                while self.offending_cells[i][j]:
                    self.offending_cells[i][j].pop()

    def replace_cell_number(self, row, col, val):
        prev_val = self.number_grid[row, col]
        self.number_grid[row, col] = int(val)
        self.invalid_cell_check(row, col, prev_val)
        if val == 0:
            self.change_cell_status(row, col, EMPTY)

    def clear_scribble(self, row, col):
        self.scribbles[row, col] = ''

    def toggle_scribble(self, row, col, val):
        if val in self.scribbles[row, col]:
            self.scribbles[row, col] = self.scribbles[row, col].replace(val, '')
        else:
            self.scribbles[row, col] += val

    def get_cell_number(self, row, col):
        return self.number_grid[row, col]

    def change_cell_status(self, row, col, new_status):
        if not self.cell_status[row, col] == FIXED:
            self.cell_status[row, col] = new_status

    def get_cell_status(self, row, col):
        return self.cell_status[row, col]

    def completion_check(self):
        if np.all(np.logical_or(self.cell_status == VALID, self.cell_status == FIXED)):
            self.cell_status[:] = FIXED
            return True
        else:
            return False

    def invalid_cell_check(self, row, col, prev_num):
        val_check = self.number_grid[row, col]

        if not prev_num == val_check or val_check == 0:
            while self.offending_cells[row][col]:
                r, c = self.offending_cells[row][col].pop()
                try:
                    self.offending_cells[r][c].remove((row, col))
                except ValueError:
                    print('No such cell found')
                if not self.offending_cells[r][c]:
                    self.change_cell_status(r, c, VALID)

        if not val_check == 0:

            row_check = np.where(self.number_grid[row, :] == val_check)[0]
            col_check = np.where(self.number_grid[:, col] == val_check)[0]
            local_grid_row = int(row / 3) * 3
            local_grid_col = int(col / 3) * 3
            local_grid_check_row, local_grid_check_col = np.where(
                self.number_grid[local_grid_row:local_grid_row + 3, local_grid_col:local_grid_col + 3] == val_check)

            if len(row_check) == 1 and len(col_check) == 1 and len(local_grid_check_row) == 1:
                self.cell_status[row, col] = VALID
            else:
                self.cell_status[row, col] = INVALID
                bad_cells = []
                if not len(row_check) == 1:
                    for c in row_check:
                        if not c == col:
                            bad_cells.append((row, c))
                            self.offending_cells[row][c].append((row, col))
                            self.change_cell_status(row, c, INVALID)
                if not len(col_check) == 1:
                    for r in col_check:
                        if not r == row:
                            bad_cells.append((r, col))
                            self.offending_cells[r][col].append((row, col))
                            self.change_cell_status(r, col, INVALID)
                if not len(local_grid_check_row) == 1:
                    for r, c in zip(local_grid_check_row + local_grid_row, local_grid_check_col + local_grid_col):
                        if not (c == col or r == row):
                            bad_cells.append((r, c))
                            self.offending_cells[r][c].append((row, col))
                            self.change_cell_status(r, c, INVALID)

                self.offending_cells[row][col] = bad_cells

    def generate_test_board(self, difficulty):
        self.clear_grid()
        try:
            with open(test_dir, 'r') as f:
                lines = f.readlines()

            values = []
            for line in lines:
                values.append([int(val) for val in line.strip('\n').split(',')])

            self.number_grid[:] = values
            self.cell_status[:] = FIXED
            row, col = np.where(self.number_grid == 0)

            for r, c in zip(row, col):
                self.cell_status[r, c] = EMPTY
        except Exception as e:
            print(e)
            print('Something went wrong loading the test file. Generating a random board instead')
            self.generate_random_board(difficulty)

    def generate_random_board(self, difficulty):
        self.clear_grid()
        self.number_grid[:] = SdkGen.generate_sudoku_puzzle(difficulty)
        row, col = np.where(self.number_grid == 0)

        for r, c in zip(row, col):
            self.cell_status[r, c] = EMPTY
