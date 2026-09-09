SIZE = 9
BOX_SIZE = 3


class Board:
    """A 9x9 sudoku board. Cells hold 0 for blank or 1-9."""

    def __init__(self, cells=None):
        if cells is None:
            self._cells = [[0] * SIZE for _ in range(SIZE)]
        else:
            if len(cells) != SIZE or any(len(row) != SIZE for row in cells):
                raise ValueError(f"cells must be a {SIZE}x{SIZE} grid")
            self._cells = [list(row) for row in cells]
        self._candidates = [[set() for _ in range(SIZE)] for _ in range(SIZE)]

    @classmethod
    def from_file(cls, path, encoding="utf-8"):
        """Read a board from a text file and parse it.

        `path` accepts anything `open()` does. Raises `SudokuParseError`
        under the same conditions as `sudoku_boards.parse`.
        """
        from .parser import parse  # avoid a circular import at module load time

        with open(path, encoding=encoding) as f:
            text = f.read()
        return parse(text)

    def get(self, row, col):
        self._check_bounds(row, col)
        return self._cells[row][col]

    def set(self, row, col, value):
        self._check_bounds(row, col)
        if value < 0 or value > 9:
            raise ValueError(f"value must be 0-9, got {value}")
        self._cells[row][col] = value
        # A filled cell has no pencil marks left to track.
        if value != 0:
            self._candidates[row][col].clear()

    @staticmethod
    def _check_bounds(row, col):
        if not (0 <= row < SIZE and 0 <= col < SIZE):
            raise IndexError(f"cell ({row}, {col}) is out of bounds for a {SIZE}x{SIZE} board")

    def candidates(self, row, col):
        """The set of pencil-marked candidate values for a cell."""
        self._check_bounds(row, col)
        return set(self._candidates[row][col])

    def add_candidate(self, row, col, value):
        self._check_bounds(row, col)
        self._check_candidate_value(value)
        if self._cells[row][col] != 0:
            raise ValueError(f"cell ({row}, {col}) is filled, it can't hold candidates")
        self._candidates[row][col].add(value)

    def discard_candidate(self, row, col, value):
        self._check_bounds(row, col)
        self._check_candidate_value(value)
        self._candidates[row][col].discard(value)

    def clear_candidates(self, row, col):
        self._check_bounds(row, col)
        self._candidates[row][col].clear()

    @staticmethod
    def _check_candidate_value(value):
        if value < 1 or value > 9:
            raise ValueError(f"candidate value must be 1-9, got {value}")

    def row(self, index):
        return list(self._cells[index])

    def column(self, index):
        return [self._cells[r][index] for r in range(SIZE)]

    def box(self, index):
        # boxes are numbered left-to-right, top-to-bottom: 0,1,2 / 3,4,5 / 6,7,8
        start_row = (index // BOX_SIZE) * BOX_SIZE
        start_col = (index % BOX_SIZE) * BOX_SIZE
        return [
            self._cells[r][c]
            for r in range(start_row, start_row + BOX_SIZE)
            for c in range(start_col, start_col + BOX_SIZE)
        ]

    def rows(self):
        return [self.row(i) for i in range(SIZE)]

    def columns(self):
        return [self.column(i) for i in range(SIZE)]

    def boxes(self):
        return [self.box(i) for i in range(SIZE)]

    def is_complete(self):
        return all(value != 0 for row in self._cells for value in row)

    def is_valid(self):
        for group in self.rows() + self.columns() + self.boxes():
            seen = set()
            for value in group:
                if value == 0:
                    continue
                if value in seen:
                    return False
                seen.add(value)
        return True

    def to_text(self):
        return "\n".join(
            "".join(str(v) if v else "." for v in row) for row in self._cells
        )

    def __eq__(self, other):
        if not isinstance(other, Board):
            return NotImplemented
        return self._cells == other._cells

    def __str__(self):
        return self.to_text()

    def __repr__(self):
        return f"<Board {self.to_text()!r}>"
