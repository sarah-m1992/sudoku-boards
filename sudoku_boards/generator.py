import random

from .board import BOX_SIZE, SIZE, Board
from .solver import _peers, _possible_values

# Clue counts, not solving-technique complexity. Fewer givens means more
# branching for the solver to resolve, which tracks difficulty well enough
# without building a full technique-based rating system.
DIFFICULTIES = {
    "easy": 36,
    "medium": 30,
    "hard": 26,
    "expert": 22,
}


def generate(difficulty="medium", rng=None):
    """Generate a random solvable puzzle with a unique solution.

    difficulty selects a target number of givens (see DIFFICULTIES); the
    higher difficulties may end up with a few more givens than their
    target if removing further cells would make the solution ambiguous.

    rng, if given, is a random.Random instance, useful for reproducing a
    specific puzzle from a saved seed.
    """
    if difficulty not in DIFFICULTIES:
        raise ValueError(f"unknown difficulty {difficulty!r}, expected one of {sorted(DIFFICULTIES)}")
    if rng is None:
        rng = random.Random()

    target_givens = DIFFICULTIES[difficulty]
    puzzle = _random_solved_grid(rng)

    positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    rng.shuffle(positions)

    givens = SIZE * SIZE
    for row, col in positions:
        if givens <= target_givens:
            break

        removed_value = puzzle[row][col]
        puzzle[row][col] = 0

        if _count_solutions(puzzle, limit=2) == 1:
            givens -= 1
        else:
            puzzle[row][col] = removed_value

    return Board(cells=puzzle)


def _random_solved_grid(rng):
    # A completed grid built from row/column offsets is trivially valid;
    # shuffling whole bands, stacks, and the digit labels turns that one
    # fixed grid into any of the far larger space of solved boards
    # without having to search for one.
    def shuffled_bands():
        return [
            band * BOX_SIZE + offset
            for band in _shuffled(range(BOX_SIZE), rng)
            for offset in _shuffled(range(BOX_SIZE), rng)
        ]

    rows = shuffled_bands()
    cols = shuffled_bands()
    digits = _shuffled(range(1, SIZE + 1), rng)

    return [[digits[(BOX_SIZE * (r % BOX_SIZE) + r // BOX_SIZE + c) % SIZE] for c in cols] for r in rows]


def _shuffled(iterable, rng):
    items = list(iterable)
    rng.shuffle(items)
    return items


def _count_solutions(cells, limit):
    candidates = {
        (r, c): _possible_values(cells, r, c)
        for r in range(SIZE)
        for c in range(SIZE)
        if cells[r][c] == 0
    }
    return _count(cells, candidates, limit)


def _count(cells, candidates, limit):
    if not candidates:
        return 1

    row, col = min(candidates, key=lambda pos: len(candidates[pos]))
    options = candidates.pop((row, col))

    if not options:
        candidates[(row, col)] = options
        return 0

    peers = _peers(row, col)
    total = 0

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

        if not dead_end:
            total += _count(cells, candidates, limit - total)

        for pos in removed:
            candidates[pos].add(value)

        if total >= limit:
            break

    cells[row][col] = 0
    candidates[(row, col)] = options
    return total
