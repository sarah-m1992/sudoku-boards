from .board import BOX_SIZE, SIZE, Board
from .errors import SudokuParseError

_BLANK_CHARS = ".0"
_DIGIT_CHARS = "123456789"
_IGNORED_CHARS = " \t|"
_BORDER_CHARS = "+-="


class _Cell:
    __slots__ = ("value", "line", "column")

    def __init__(self, value, line, column):
        self.value = value
        self.line = line
        self.column = column


def parse(text):
    """Parse a text sudoku board into a Board.

    Expects nine rows of nine characters each, where a character is a
    digit 1-9 for a filled cell or '.'/'0' for a blank one. Spaces and
    '|' inside a row are ignored, so cells can be visually grouped.
    Blank lines, lines starting with '#', and lines made only of
    '+', '-' or '=' (ascii table borders) are skipped entirely and
    don't count as board rows.

    Raises SudokuParseError, with a line and column number pointing at
    the exact problem, if the text doesn't describe a well-formed
    9x9 board.
    """
    lines = text.splitlines()
    grid_rows = []  # list of (line_no, list[_Cell])

    for line_no, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if all(ch in _BORDER_CHARS for ch in stripped):
            continue

        cells = _parse_row(raw_line, line_no)
        grid_rows.append((line_no, cells))

        if len(grid_rows) > SIZE:
            extra_line_no, _ = grid_rows[SIZE]
            raise SudokuParseError(
                f"too many board rows (expected {SIZE})",
                line=extra_line_no,
                column=1,
                source_line=lines[extra_line_no - 1],
            )

    if len(grid_rows) < SIZE:
        raise SudokuParseError(
            f"expected {SIZE} board rows, found {len(grid_rows)}",
            line=len(lines) + 1,
            column=1,
        )

    values = [[cell.value for cell in cells] for _, cells in grid_rows]
    positions = [[(cell.line, cell.column) for cell in cells] for _, cells in grid_rows]

    _check_duplicates(values, positions, lines)

    return Board(cells=values)


def _parse_row(raw_line, line_no):
    cells = []
    for column, ch in enumerate(raw_line, start=1):
        if ch in _IGNORED_CHARS:
            continue
        if len(cells) >= SIZE:
            raise SudokuParseError(
                f"too many cells in row (expected {SIZE})",
                line=line_no,
                column=column,
                source_line=raw_line,
            )
        if ch in _BLANK_CHARS:
            cells.append(_Cell(0, line_no, column))
        elif ch in _DIGIT_CHARS:
            cells.append(_Cell(int(ch), line_no, column))
        else:
            raise SudokuParseError(
                f"unexpected character {ch!r} in board row (expected a digit 1-9 or '.')",
                line=line_no,
                column=column,
                source_line=raw_line,
            )

    if len(cells) < SIZE:
        raise SudokuParseError(
            f"row has {len(cells)} cell(s), expected {SIZE}",
            line=line_no,
            column=len(raw_line) + 1,
            source_line=raw_line,
        )

    return cells


def _check_duplicates(values, positions, lines):
    for r in range(SIZE):
        group = [(values[r][c], positions[r][c]) for c in range(SIZE)]
        _check_group(group, f"row {r + 1}", lines)

    for c in range(SIZE):
        group = [(values[r][c], positions[r][c]) for r in range(SIZE)]
        _check_group(group, f"column {c + 1}", lines)

    for b in range(SIZE):
        start_row = (b // BOX_SIZE) * BOX_SIZE
        start_col = (b % BOX_SIZE) * BOX_SIZE
        group = [
            (values[r][c], positions[r][c])
            for r in range(start_row, start_row + BOX_SIZE)
            for c in range(start_col, start_col + BOX_SIZE)
        ]
        _check_group(group, f"box {b + 1}", lines)


def _check_group(group, label, lines):
    seen = {}
    for value, (line, column) in group:
        if value == 0:
            continue
        if value in seen:
            first_line, first_column = seen[value]
            raise SudokuParseError(
                f"duplicate value '{value}' in {label} "
                f"(first seen at line {first_line}, column {first_column})",
                line=line,
                column=column,
                source_line=lines[line - 1],
            )
        seen[value] = (line, column)
