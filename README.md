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

Two formats are accepted, chosen automatically based on the text.

A grid of nine rows of nine characters. A digit 1-9 is a filled cell,
`.` or `0` is blank. Spaces, `|`, and lines made of `-`, `+`, `=` are
allowed and ignored, so a board with visual dividers still parses:

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

Or a flat 81-character string, read left to right, top to bottom,
with the same rules for digits and blanks and no separators:

```
530070000600195000098000060800060003400803001700020006060000280000419005000080
```

`parse` picks the flat format whenever the text is a single line;
anything with more than one line is parsed as a grid.

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

A `Board` also tracks pencil marks per blank cell, for tools that want to
show or manipulate candidates the way a human solver would on paper:

```python
board.add_candidate(0, 2, 1)
board.add_candidate(0, 2, 4)
print(board.candidates(0, 2))  # {1, 4}

board.discard_candidate(0, 2, 1)
board.set(0, 2, 4)  # filling a cell clears its candidates
```

## Solving

```python
from sudoku_boards import solve, UnsolvableError

try:
    solved = solve(board)
except UnsolvableError as err:
    print(err)
    raise SystemExit(1)

print(solved)
```

`solve` returns a new `Board` and leaves the one you passed in untouched.
It raises `UnsolvableError` both for boards that already break a rule and
for well-formed boards that have no valid completion.

## Generating

```python
from sudoku_boards import generate

puzzle = generate("hard")
print(puzzle)
```

`generate` builds a random solved board and removes cells one at a time,
checking after each removal that the puzzle still has exactly one
solution, until it reaches the target number of givens for the chosen
difficulty (`"easy"`, `"medium"`, `"hard"`, or `"expert"`). Pass a
`random.Random` instance as `rng` to get a reproducible puzzle from a
saved seed.

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
- `sudoku_boards.Board` - rows, columns, 3x3 boxes, validity checks, and per-cell pencil marks
- `sudoku_boards.SudokuParseError` - carries `line`, `column`, and a caret-pointer `str()`
- `sudoku_boards.solve` - backtracking solver, returns a new solved `Board`
- `sudoku_boards.UnsolvableError` - raised when a board can't be solved
- `sudoku_boards.generate` - builds a random puzzle with a unique solution at a given difficulty
- `sudoku_boards.DIFFICULTIES` - the difficulty names `generate` accepts, mapped to their target clue count

## Status

Parsing, structural validation (row/column/box uniqueness), basic board
queries, solving, and puzzle generation work.

## License

MIT
