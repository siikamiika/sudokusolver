from itertools import permutations, product, islice
import multiprocessing as mp


def _int(num):
    try:
        return int(num)
    except ValueError:
        return None

def file_to_grid(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        return tuple(tuple(map(_int, r)) for r in f.read().splitlines() if r)

def check_win(product):
    grid = Grid(product)
    if winning_grid(grid):
        for row in product:
            print(' '.join(str(n) for n in row))

def winning_grid(grid):
    _1_to_9 = list(range(1,10))
    # check rows
    for row_idx in range(9):
        if sorted(grid.get_row(row_idx)) != _1_to_9:
            return False
    # check columns
    for col_idx in range(9):
        if sorted(grid.get_column(col_idx)) != _1_to_9:
            return False
    # helpers
    offset = [0, 0]
    def next_square(_offset, step, borders):
        if _offset[0] + step < borders[0]:
            _offset[0] += step
        elif _offset[1] + step < borders[1]:
            _offset[0] = 0
            _offset[1] += step
        else:
            print(_offset)
            raise Exception('out of bounds')
        return _offset
    # check subsquares
    for _ in range(9):
        position = [0, 0]
        subsq_content = []
        for __ in range(9):
            x = position[0] + offset[0]
            y = position[1] + offset[1]
            subsq_content.append(grid.grid[y][x])
            if __ < 9 - 1:
                position = next_square(position, 1, (3, 3))
        if sorted(subsq_content) != _1_to_9:
            return False
        if _ < 9 - 1:
            offset = next_square(offset, 3, (9, 9))

    return True


class Grid(object):

    def __init__(self, inp):
        self.grid = inp

    def get_column(self, index):
        return tuple(r[index] for r in self.grid)

    def get_row(self, index):
        return self.grid[index]


class SudokuSolver(object):

    def __init__(self, grid, size=3):
        self.unsolved_grid = grid
        self.size = size

    def row_combinations(self, row):
        unsolved_row = self.unsolved_grid.get_row(row)
        unused = tuple(n for n in range(1, 10) if n not in unsolved_row)
        combinations = []
        for p in permutations(unused):
            p = list(p)
            combination = list(unsolved_row)
            for i, v in enumerate(combination):
                if v == None:
                    combination[i] = p.pop(0)
            combinations.append(tuple(combination))
        return combinations

    def grid_combinations(self):
        row_comb = []
        for i in range(9):
            row_comb.append(self.row_combinations(i))
        pos = 0
        pool = mp.Pool(processes=16)
        grid_combinations = product(*row_comb)
        while True:
            chunk = pool.map(check_win, islice(grid_combinations, 1000000))
            if chunk:
                continue
            else:
                break

def main():
    unsolved_grid = Grid(file_to_grid('viineri.txt'))
    solver = SudokuSolver(unsolved_grid)
    solver.grid_combinations()

if __name__ == '__main__':
    main()
