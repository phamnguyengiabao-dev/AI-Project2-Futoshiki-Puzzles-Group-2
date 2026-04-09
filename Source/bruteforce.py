"""
Brute-Force solver for the Futoshiki Puzzle Solver.

Enumerates all possible value assignments without pruning.
Serves as a correctness baseline for comparing other solvers.
"""

import time
from typing import Dict, List, Optional, Tuple

from models import Puzzle, SolverResult


def _verify_solution(assignment: Dict[Tuple[int, int], int], puzzle: Puzzle) -> bool:
    """Verify complete assignment satisfies all constraints."""
    n = puzzle.n

    # Check row uniqueness
    for i in range(n):
        row_vals = [assignment[(i, j)] for j in range(n)]
        if sorted(row_vals) != list(range(1, n + 1)):
            return False

    # Check column uniqueness
    for j in range(n):
        col_vals = [assignment[(i, j)] for i in range(n)]
        if sorted(col_vals) != list(range(1, n + 1)):
            return False

    # Check horizontal inequality constraints
    for i in range(n):
        for j in range(n - 1):
            c = puzzle.h_constraints[i][j]
            if c == 1 and not (assignment[(i, j)] < assignment[(i, j + 1)]):
                return False
            if c == -1 and not (assignment[(i, j)] > assignment[(i, j + 1)]):
                return False

    # Check vertical inequality constraints
    for i in range(n - 1):
        for j in range(n):
            c = puzzle.v_constraints[i][j]
            if c == 1 and not (assignment[(i, j)] < assignment[(i + 1, j)]):
                return False
            if c == -1 and not (assignment[(i, j)] > assignment[(i + 1, j)]):
                return False

    # Check given clues are respected
    for cell, value in puzzle.get_given_clues():
        if assignment.get((cell.row, cell.col)) != value:
            return False

    return True


def _enumerate(
    cells: List[Tuple[int, int]],
    assignment: Dict[Tuple[int, int], int],
    puzzle: Puzzle,
) -> Optional[Dict[Tuple[int, int], int]]:
    """Recursively try all values 1..N for each empty cell."""
    # Base case: all cells filled — verify the complete assignment
    if not cells:
        if _verify_solution(assignment, puzzle):
            return dict(assignment)
        return None

    cell = cells[0]
    rest = cells[1:]

    for v in range(1, puzzle.n + 1):
        assignment[cell] = v
        result = _enumerate(rest, assignment, puzzle)
        if result is not None:
            return result

    # Clean up and signal failure
    del assignment[cell]
    return None


def solve(puzzle: Puzzle) -> SolverResult:
    """Solve using brute-force enumeration."""
    start = time.time()

    # Build initial assignment from given clues
    assignment: Dict[Tuple[int, int], int] = {}
    for i in range(puzzle.n):
        for j in range(puzzle.n):
            if puzzle.grid[i][j] != 0:
                assignment[(i, j)] = puzzle.grid[i][j]

    # Collect empty cells
    empty_cells: List[Tuple[int, int]] = [
        (i, j)
        for i in range(puzzle.n)
        for j in range(puzzle.n)
        if puzzle.grid[i][j] == 0
    ]

    solution = _enumerate(empty_cells, assignment, puzzle)

    time_ms = (time.time() - start) * 1000

    if solution is not None:
        return SolverResult(
            algorithm="Brute-Force",
            solution=solution,
            solved=True,
            time_ms=time_ms,
        )
    else:
        return SolverResult(
            algorithm="Brute-Force",
            solution=None,
            solved=False,
            time_ms=time_ms,
            message="No solution found.",
        )
