"""Parse and represent sudoku boards from plain text."""

from .board import Board
from .errors import SudokuError, SudokuParseError
from .parser import parse

__all__ = ["Board", "SudokuError", "SudokuParseError", "parse"]

__version__ = "0.1.0"
