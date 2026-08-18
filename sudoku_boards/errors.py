class SudokuError(Exception):
    """Base class for all errors raised by this library."""


class SudokuParseError(SudokuError):
    """A board could not be parsed from text.

    Carries the 1-based line and column of the offending character so
    a caller can point straight at the problem, the way a compiler
    would, instead of just saying "invalid board".
    """

    def __init__(self, message, line, column, source_line=""):
        self.line = line
        self.column = column
        self.source_line = source_line
        super().__init__(message)

    def __str__(self):
        header = f"line {self.line}, column {self.column}: {self.args[0]}"
        if not self.source_line:
            return header
        pointer = " " * (self.column - 1) + "^"
        return f"{header}\n    {self.source_line}\n    {pointer}"
