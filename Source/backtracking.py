"""
Backtracking solver for the Futoshiki Puzzle Solver.

Implements systematic search with MRV (Minimum Remaining Values) heuristic
and forward checking to prune invalid branches early.
"""

import time
from typing import Dict, Optional, Set, Tuple

from models import Puzzle, SolverResult


def _is_consistent(
    assignment: Dict[Tuple[int, int], int],
    cell: Tuple[int, int],
    value: int,
    puzzle: Puzzle,
) -> bool:
    """Check that assigning value to cell doesn't violate any constraint."""
    i, j = cell
    n = puzzle.n

    # Row uniqueness
    for jj in range(n):
        if jj != j and assignment.get((i, jj)) == value:
            return False

    # Column uniqueness
    for ii in range(n):
        if ii != i and assignment.get((ii, j)) == value:
            return False

    # Horizontal inequality constraints
    # cell(i,j) vs cell(i,j+1)
    if j < n - 1:
        c = puzzle.h_constraints[i][j]
        right = assignment.get((i, j + 1))
        if right is not None:
            if c == 1 and not (value < right):
                return False
            if c == -1 and not (value > right):
                return False

    # cell(i,j-1) vs cell(i,j)
    if j > 0:
        c = puzzle.h_constraints[i][j - 1]
        left = assignment.get((i, j - 1))
        if left is not None:
            if c == 1 and not (left < value):
                return False
            if c == -1 and not (left > value):
                return False

    # Vertical inequality constraints
    # cell(i,j) vs cell(i+1,j)
    if i < n - 1:
        c = puzzle.v_constraints[i][j]
        below = assignment.get((i + 1, j))
        if below is not None:
            if c == 1 and not (value < below):
                return False
            if c == -1 and not (value > below):
                return False

    # cell(i-1,j) vs cell(i,j)
    if i > 0:
        c = puzzle.v_constraints[i - 1][j]
        above = assignment.get((i - 1, j))
        if above is not None:
            if c == 1 and not (above < value):
                return False
            if c == -1 and not (above > value):
                return False

    return True


def _select_unassigned_cell(
    assignment: Dict[Tuple[int, int], int],
    domains: Dict[Tuple[int, int], Set[int]],
) -> Tuple[int, int]:
    """MRV: pick unassigned cell with smallest domain."""
    best = None
    best_size = float("inf")
    for cell, domain in domains.items():
        if cell not in assignment:
            if len(domain) < best_size:
                best_size = len(domain)
                best = cell
    return best


def _forward_check(
    assignment: Dict[Tuple[int, int], int],
    domains: Dict[Tuple[int, int], Set[int]],
    cell: Tuple[int, int],
    value: int,
    puzzle: Puzzle,
) -> Optional[Dict[Tuple[int, int], Set[int]]]:
    """
    After assigning value to cell, prune domains of peers.
    Returns updated domains copy, or None if any domain becomes empty.
    """
    new_domains = {c: set(d) for c, d in domains.items()}
    i, j = cell
    n = puzzle.n

    peers_to_remove_value: Set[Tuple[int, int]] = set()

    # Same row / column peers (all-different)
    for jj in range(n):
        if jj != j:
            peers_to_remove_value.add((i, jj))
    for ii in range(n):
        if ii != i:
            peers_to_remove_value.add((ii, j))

    for peer in peers_to_remove_value:
        if peer not in assignment:
            new_domains[peer].discard(value)
            if not new_domains[peer]:
                return None

    # Inequality constraint pruning
    def _prune_inequality(peer: Tuple[int, int], keep_fn) -> bool:
        """Remove values from peer's domain that violate keep_fn(peer_val)."""
        if peer in assignment:
            return True
        to_remove = {v for v in new_domains[peer] if not keep_fn(v)}
        new_domains[peer] -= to_remove
        return bool(new_domains[peer])

    # Horizontal: cell(i,j) vs cell(i,j+1)
    if j < n - 1:
        c = puzzle.h_constraints[i][j]
        peer = (i, j + 1)
        if c == 1:  # value < peer_val
            if not _prune_inequality(peer, lambda v: v > value):
                return None
        elif c == -1:  # value > peer_val
            if not _prune_inequality(peer, lambda v: v < value):
                return None

    # Horizontal: cell(i,j-1) vs cell(i,j)
    if j > 0:
        c = puzzle.h_constraints[i][j - 1]
        peer = (i, j - 1)
        if c == 1:  # peer_val < value
            if not _prune_inequality(peer, lambda v: v < value):
                return None
        elif c == -1:  # peer_val > value
            if not _prune_inequality(peer, lambda v: v > value):
                return None

    # Vertical: cell(i,j) vs cell(i+1,j)
    if i < n - 1:
        c = puzzle.v_constraints[i][j]
        peer = (i + 1, j)
        if c == 1:  # value < peer_val
            if not _prune_inequality(peer, lambda v: v > value):
                return None
        elif c == -1:  # value > peer_val
            if not _prune_inequality(peer, lambda v: v < value):
                return None

    # Vertical: cell(i-1,j) vs cell(i,j)
    if i > 0:
        c = puzzle.v_constraints[i - 1][j]
        peer = (i - 1, j)
        if c == 1:  # peer_val < value
            if not _prune_inequality(peer, lambda v: v < value):
                return None
        elif c == -1:  # peer_val > value
            if not _prune_inequality(peer, lambda v: v > value):
                return None

    return new_domains


def _backtrack(
    assignment: Dict[Tuple[int, int], int],
    domains: Dict[Tuple[int, int], Set[int]],
    puzzle: Puzzle,
) -> Optional[Dict[Tuple[int, int], int]]:
    """Recursive backtracking with MRV + forward checking."""
    n = puzzle.n
    if len(assignment) == n * n:
        return assignment

    cell = _select_unassigned_cell(assignment, domains)
    if cell is None:
        return None

    for value in sorted(domains[cell]):
        if _is_consistent(assignment, cell, value, puzzle):
            assignment[cell] = value
            new_domains = _forward_check(assignment, domains, cell, value, puzzle)
            if new_domains is not None:
                result = _backtrack(assignment, new_domains, puzzle)
                if result is not None:
                    return result
            del assignment[cell]

    return None


def solve(puzzle: Puzzle) -> SolverResult:
    """Backtracking with MRV + forward checking."""
    start = time.time()
    n = puzzle.n

    # Initialise domains
    domains: Dict[Tuple[int, int], Set[int]] = {}
    assignment: Dict[Tuple[int, int], int] = {}

    for i in range(n):
        for j in range(n):
            v = puzzle.grid[i][j]
            if v != 0:
                domains[(i, j)] = {v}
                assignment[(i, j)] = v
            else:
                domains[(i, j)] = set(range(1, n + 1))

    result = _backtrack(assignment, domains, puzzle)
    elapsed = (time.time() - start) * 1000

    if result is not None:
        return SolverResult(
            algorithm="Backtracking",
            solution=result,
            solved=True,
            time_ms=elapsed,
        )
    return SolverResult(
        algorithm="Backtracking",
        solution=None,
        solved=False,
        time_ms=elapsed,
        message="No solution found",
    )
