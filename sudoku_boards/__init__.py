"""Parse and represent sudoku boards from plain text."""

from .board import Board
from .errors import SudokuError, SudokuParseError
from .generator import DIFFICULTIES, generate
from .parser import parse
from .solver import UnsolvableError, solve

__all__ = [
    "Board",
    "DIFFICULTIES",
    "SudokuError",
    "SudokuParseError",
    "UnsolvableError",
    "generate",
    "parse",
    "solve",
]

__version__ = "0.1.0"
