import os
import tempfile
import unittest

from sudoku_boards import Board, SudokuParseError, parse

# A known valid solved grid (every row, column, and 3x3 box has 1-9
# exactly once), used as a base for both flat and grid format tests.
SOLVED_ROWS = [
    "534678912",
    "672195348",
    "198342567",
    "859761423",
    "426853791",
    "713924856",
    "961537284",
    "287419635",
    "345286179",
]
SOLVED_FLAT = "".join(SOLVED_ROWS)
SOLVED_CELLS = [[int(ch) for ch in row] for row in SOLVED_ROWS]


def blank_grid_text():
    """Nine rows of nine blank cells, as a starting point for edits."""
    return "\n".join("." * 9 for _ in range(9))


class FlatFormatTests(unittest.TestCase):
    def test_valid_flat_string(self):
        board = parse(SOLVED_FLAT)
        self.assertEqual(board, Board(cells=SOLVED_CELLS))

    def test_blank_cells_accept_dot_or_zero(self):
        text = ("." * 81)[:40] + ("0" * 41)
        board = parse(text)
        self.assertTrue(all(v == 0 for row in board.rows() for v in row))

    def test_surrounding_whitespace_is_stripped(self):
        board = parse(f"  {SOLVED_FLAT}  \n")
        self.assertEqual(board, Board(cells=SOLVED_CELLS))

    def test_too_short_reports_column_after_last_character(self):
        text = SOLVED_FLAT[:-1]
        with self.assertRaises(SudokuParseError) as ctx:
            parse(text)
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.column, len(text) + 1)

    def test_too_long_reports_first_extra_column(self):
        text = SOLVED_FLAT + "5"
        with self.assertRaises(SudokuParseError) as ctx:
            parse(text)
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.column, 82)

    def test_invalid_character_reports_its_column(self):
        text = SOLVED_FLAT[:10] + "x" + SOLVED_FLAT[11:]
        with self.assertRaises(SudokuParseError) as ctx:
            parse(text)
        self.assertEqual(ctx.exception.column, 11)
        self.assertIn("'x'", str(ctx.exception))


class GridFormatTests(unittest.TestCase):
    def test_valid_grid(self):
        board = parse("\n".join(SOLVED_ROWS))
        self.assertEqual(board, Board(cells=SOLVED_CELLS))

    def test_dividers_comments_and_blank_lines_are_ignored(self):
        text = "\n".join([
            "# a comment above the board",
            "",
            "5 3 4 | 6 7 8 | 9 1 2",
            "6 7 2 | 1 9 5 | 3 4 8",
            "1 9 8 | 3 4 2 | 5 6 7",
            "------+-------+------",
            "8 5 9 | 7 6 1 | 4 2 3",
            "4 2 6 | 8 5 3 | 7 9 1",
            "7 1 3 | 9 2 4 | 8 5 6",
            "======+=======+======",
            "9 6 1 | 5 3 7 | 2 8 4",
            "2 8 7 | 4 1 9 | 6 3 5",
            "3 4 5 | 2 8 6 | 1 7 9",
            "",
        ])
        board = parse(text)
        self.assertEqual(board, Board(cells=SOLVED_CELLS))

    def test_row_too_short_reports_column_after_last_cell(self):
        rows = list(SOLVED_ROWS)
        rows[3] = rows[3][:7]
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        self.assertEqual(ctx.exception.line, 4)
        self.assertEqual(ctx.exception.column, 8)

    def test_row_too_long_reports_tenth_cell_column(self):
        rows = list(SOLVED_ROWS)
        rows[0] = rows[0] + "5"
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.column, 10)

    def test_invalid_character_reports_line_and_column(self):
        rows = list(SOLVED_ROWS)
        rows[5] = "12345678?"
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        self.assertEqual(ctx.exception.line, 6)
        self.assertEqual(ctx.exception.column, 9)
        self.assertIn("'?'", str(ctx.exception))

    def test_too_few_rows(self):
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(SOLVED_ROWS[:8]))
        self.assertIn("found 8", str(ctx.exception))

    def test_too_many_rows(self):
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(SOLVED_ROWS + [SOLVED_ROWS[0]]))
        self.assertEqual(ctx.exception.line, 10)

    def test_empty_text_reports_missing_rows(self):
        with self.assertRaises(SudokuParseError) as ctx:
            parse("")
        self.assertEqual(ctx.exception.line, 1)
        self.assertIn("found 0", str(ctx.exception))


class DuplicateValidationTests(unittest.TestCase):
    def test_duplicate_in_row(self):
        text = blank_grid_text()
        rows = text.splitlines()
        rows[0] = "11......."
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        self.assertIn("row 1", str(ctx.exception))
        self.assertEqual(ctx.exception.line, 1)
        self.assertEqual(ctx.exception.column, 2)

    def test_duplicate_in_column(self):
        rows = blank_grid_text().splitlines()
        rows[0] = "1........"
        rows[1] = "1........"
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        self.assertIn("column 1", str(ctx.exception))
        self.assertEqual(ctx.exception.line, 2)

    def test_duplicate_in_box_but_not_row_or_column(self):
        rows = blank_grid_text().splitlines()
        rows[0] = "1........"
        rows[1] = ".1......."
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        self.assertIn("box 1", str(ctx.exception))
        self.assertEqual(ctx.exception.line, 2)
        self.assertEqual(ctx.exception.column, 2)

    def test_error_message_names_first_occurrence(self):
        rows = blank_grid_text().splitlines()
        rows[0] = "5.......5"
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        self.assertIn("first seen at line 1, column 1", str(ctx.exception))


class FromFileTests(unittest.TestCase):
    def _write(self, text):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write(text)
        self.addCleanup(os.remove, path)
        return path

    def test_reads_and_parses_a_grid_file(self):
        path = self._write("\n".join(SOLVED_ROWS))
        board = Board.from_file(path)
        self.assertEqual(board, Board(cells=SOLVED_CELLS))

    def test_reads_and_parses_a_flat_file(self):
        path = self._write(SOLVED_FLAT)
        board = Board.from_file(path)
        self.assertEqual(board, Board(cells=SOLVED_CELLS))

    def test_malformed_file_raises_parse_error_with_location(self):
        rows = list(SOLVED_ROWS)
        rows[2] = "1234567?9"
        path = self._write("\n".join(rows))
        with self.assertRaises(SudokuParseError) as ctx:
            Board.from_file(path)
        self.assertEqual(ctx.exception.line, 3)
        self.assertEqual(ctx.exception.column, 8)

    def test_missing_file_raises_os_error(self):
        with self.assertRaises(OSError):
            Board.from_file("/no/such/path/puzzle.txt")


class ErrorFormattingTests(unittest.TestCase):
    def test_str_includes_source_line_and_caret(self):
        rows = list(SOLVED_ROWS)
        rows[2] = "1234567?9"
        with self.assertRaises(SudokuParseError) as ctx:
            parse("\n".join(rows))
        message = str(ctx.exception)
        lines = message.splitlines()
        self.assertEqual(lines[1].strip(), "1234567?9")
        self.assertEqual(lines[2].index("^"), lines[1].index("?"))

    def test_str_without_source_line_omits_pointer(self):
        err = SudokuParseError("boom", line=3, column=5)
        self.assertEqual(str(err), "line 3, column 5: boom")


if __name__ == "__main__":
    unittest.main()
