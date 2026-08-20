from .board import BOX_SIZE, SIZE, Board
from .errors import SudokuError


class UnsolvableError(SudokuError):
    """Raised when a board has no solution."""


def solve(board):
    """Return a new, fully solved Board. Does not modify the input.

    Raises UnsolvableError if the board already breaks a row/column/box
    rule, or if no assignment of the blank cells satisfies the rules.
    """
    if not board.is_valid():
        raise UnsolvableError("board already has a duplicate value in some row, column, or box")

    cells = [row[:] for row in board.rows()]
    candidates = _initial_candidates(cells)

    if not _solve(cells, candidates):
        raise UnsolvableError("board has no solution")

    return Board(cells=cells)


def _initial_candidates(cells):
    return {
        (r, c): _possible_values(cells, r, c)
        for r in range(SIZE)
        for c in range(SIZE)
        if cells[r][c] == 0
    }


def _possible_values(cells, row, col):
    used = set(cells[row]) | {cells[r][col] for r in range(SIZE)}
    start_row = (row // BOX_SIZE) * BOX_SIZE
    start_col = (col // BOX_SIZE) * BOX_SIZE
    used |= {
        cells[r][c]
        for r in range(start_row, start_row + BOX_SIZE)
        for c in range(start_col, start_col + BOX_SIZE)
    }
    return {v for v in range(1, SIZE + 1) if v not in used}


def _solve(cells, candidates):
    if not candidates:
        return True

    # Filling the most-constrained cell first keeps the branching factor
    # low and fails fast on dead ends, instead of wandering through
    # mostly-open cells before hitting a contradiction.
    row, col = min(candidates, key=lambda pos: len(candidates[pos]))
    options = candidates.pop((row, col))

    if not options:
        candidates[(row, col)] = options
        return False

    peers = _peers(row, col)

    for value in options:
        cells[row][col] = value

        removed = []
        dead_end = False
        for pos in peers:
            peer_candidates = candidates.get(pos)
            if peer_candidates is not None and value in peer_candidates:
                peer_candidates.remove(value)
                removed.append(pos)
                if not peer_candidates:
                    dead_end = True

        if not dead_end and _solve(cells, candidates):
            return True

        for pos in removed:
            candidates[pos].add(value)

    cells[row][col] = 0
    candidates[(row, col)] = options
    return False


def _peers(row, col):
    start_row = (row // BOX_SIZE) * BOX_SIZE
    start_col = (col // BOX_SIZE) * BOX_SIZE
    peers = {(row, c) for c in range(SIZE)}
    peers |= {(r, col) for r in range(SIZE)}
    peers |= {
        (r, c)
        for r in range(start_row, start_row + BOX_SIZE)
        for c in range(start_col, start_col + BOX_SIZE)
    }
    peers.discard((row, col))
    return peers
