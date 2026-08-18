# sudoku-boards

A small library for reading sudoku boards out of plain text and telling
you exactly what's wrong with them when they aren't valid.

Most sudoku tools either accept a flat 81-character string or throw a
bare "invalid board" exception when something's off. Neither is
pleasant if the text came from a file, an OCR pass over a newspaper
scan, or someone typing a puzzle in by hand. This library parses a
readable grid format and, when parsing fails, points at the exact
line and column of the problem, the way a compiler would.

## Board format

Nine rows of nine characters. A digit 1-9 is a filled cell, `.` or `0`
is blank. Spaces, `|`, and lines made of `-`, `+`, `=` are allowed and
ignored, so a board with visual dividers still parses:

```
5 3 . | . 7 . | . . .
6 . . | 1 9 5 | . . .
. 9 8 | . . . | . 6 .
------+-------+------
8 . . | . 6 . | . . 3
4 . . | 8 . 3 | . . 1
7 . . | . 2 . | . 6 .
------+-------+------
. 6 . | . . . | 2 8 .
. . . | 4 1 9 | . . 5
. . . | . 8 . | . 7 9
```

## Usage

```python
from sudoku_boards import parse, SudokuParseError

text = open("puzzle.txt").read()

try:
    board = parse(text)
except SudokuParseError as err:
    print(err)
    raise SystemExit(1)

print("solved" if board.is_complete() and board.is_valid() else "not solved")
print(board.row(0))
print(board.column(0))
print(board.box(0))
```

If a row is short, the error says exactly where it stopped counting:

```
>>> parse("53..7....\n" + ".......\n" + ("........." * 7))
sudoku_boards.errors.SudokuParseError: line 2, column 8: row has 7 cell(s), expected 9
    .......
           ^
```

And if two cells in the same row, column, or 3x3 box repeat a digit,
the error names both locations:

```
>>> parse("55.......\n" + "........." * 8)
sudoku_boards.errors.SudokuParseError: line 1, column 2: duplicate value '5' in row 1 (first seen at line 1, column 1)
    55.......
     ^
```

## What's here

- `sudoku_boards.parse` - text in, a `Board` out, or a `SudokuParseError`
- `sudoku_boards.Board` - rows, columns, 3x3 boxes, and validity checks
- `sudoku_boards.SudokuParseError` - carries `line`, `column`, and a caret-pointer `str()`

## Status

Parsing, structural validation (row/column/box uniqueness), and basic
board queries work. There's no solver yet.

## License

MIT
