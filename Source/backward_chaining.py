"""
Backward Chaining solver (SLD resolution) for the Futoshiki Puzzle Solver.

Answers queries of the form Val(i,j,?) by reasoning backwards from the goal
using depth-first SLD resolution with occurs-check.
"""

import time
from typing import Dict, List, Optional, Set, Tuple

from models import KnowledgeBase, Puzzle, SolverResult


def _sld_resolve(goal: str, kb: KnowledgeBase, visited: Set[str]) -> bool:
    """
    SLD resolution with occurs-check.
    Returns True if goal can be proved from KB.

    - If goal in visited → False (occurs-check, prevents infinite loops)
    - If goal is a fact in kb.facts → True
    - If goal starts with '-': prove the positive literal is NOT provable
    - For positive goal: find clauses containing it, try to prove all other
      literals are false (their negations are true)
    """
    # Occurs-check: avoid infinite loops
    if goal in visited:
        return False
    visited = visited | {goal}  # immutable update so siblings don't share state

    # Negative literal: prove the positive form is NOT provable
    if goal.startswith("-"):
        positive = goal[1:]
        return not _sld_resolve(positive, kb, visited.copy())

    # Positive goal: check if it's a known fact
    if goal in kb.facts:
        return True

    # Try to prove via clauses that contain this literal as a positive member
    for clause in kb.clauses:
        if goal not in clause.literals:
            continue

        # For this clause to support the goal, every OTHER literal must be
        # provably false — i.e., its negation must be provable.
        other_literals = [lit for lit in clause.literals if lit != goal]

        # A unit clause [goal] with no other literals is already handled by
        # the facts check above (add_fact also adds to kb.facts).
        # But handle it here too for robustness.
        if not other_literals:
            return True

        # Try to prove all other literals are false
        all_false = True
        for lit in other_literals:
            # Prove that lit is false → prove -lit
            neg_lit = lit[1:] if lit.startswith("-") else f"-{lit}"
            if not _sld_resolve(neg_lit, kb, visited.copy()):
                all_false = False
                break

        if all_false:
            return True

    return False


def query_cell(kb: KnowledgeBase, i: int, j: int, n: int) -> Optional[int]:
    """
    Query Val(i,j,?) — return v if Val_i_j_v can be proved, else None.
    Tries each v in 1..N.
    """
    for v in range(1, n + 1):
        goal = f"Val_{i}_{j}_{v}"
        if _sld_resolve(goal, kb, set()):
            return v
    return None


def _backtrack_solve(
    cells: List[Tuple[int, int]],
    idx: int,
    assignment: Dict[Tuple[int, int], int],
    puzzle: Puzzle,
) -> Optional[Dict[Tuple[int, int], int]]:
    """
    Simple backtracking fallback for cells that backward chaining cannot resolve.
    """
    if idx == len(cells):
        return assignment if puzzle.is_valid_solution(assignment) else None

    cell = cells[idx]
    for v in range(1, puzzle.n + 1):
        assignment[cell] = v
        # Quick consistency check before going deeper
        if _is_consistent(assignment, cell, v, puzzle):
            result = _backtrack_solve(cells, idx + 1, assignment, puzzle)
            if result is not None:
                return result
    del assignment[cell]
    return None


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

    # Horizontal constraints
    for jj in range(n - 1):
        c = puzzle.h_constraints[i][jj]
        left = assignment.get((i, jj))
        right = assignment.get((i, jj + 1))
        if left is not None and right is not None:
            if c == 1 and not (left < right):
                return False
            if c == -1 and not (left > right):
                return False

    # Vertical constraints
    for ii in range(n - 1):
        c = puzzle.v_constraints[ii][j]
        top = assignment.get((ii, j))
        bottom = assignment.get((ii + 1, j))
        if top is not None and bottom is not None:
            if c == 1 and not (top < bottom):
                return False
            if c == -1 and not (top > bottom):
                return False

    return True


def solve(kb: KnowledgeBase, puzzle: Puzzle) -> SolverResult:
    """
    Solve by querying Val(i,j,?) for each cell via backward chaining (SLD resolution).
    Falls back to backtracking for cells that cannot be resolved by backward chaining alone.
    """
    start = time.time()
    n = puzzle.n
    assignment: Dict[Tuple[int, int], int] = {}
    unresolved: List[Tuple[int, int]] = []

    # Phase 1: backward chaining query for each cell
    for i in range(n):
        for j in range(n):
            val = query_cell(kb, i, j, n)
            if val is not None:
                assignment[(i, j)] = val
            else:
                unresolved.append((i, j))

    # Phase 2: backtracking fallback for unresolved cells
    if unresolved:
        # Seed the backtracking with already-resolved cells
        result = _backtrack_solve(unresolved, 0, assignment, puzzle)
        if result is None:
            elapsed = (time.time() - start) * 1000
            return SolverResult(
                algorithm="Backward Chaining",
                solution=None,
                solved=False,
                time_ms=elapsed,
                message="No solution found",
            )
        assignment = result

    elapsed = (time.time() - start) * 1000

    # Validate the complete assignment
    if len(assignment) == n * n and puzzle.is_valid_solution(assignment):
        return SolverResult(
            algorithm="Backward Chaining",
            solution=assignment,
            solved=True,
            time_ms=elapsed,
            message=f"Solved ({len(assignment) - len(unresolved)} cells via BC, "
                    f"{len(unresolved)} via backtracking)",
        )

    return SolverResult(
        algorithm="Backward Chaining",
        solution=None,
        solved=False,
        time_ms=elapsed,
        message="No valid solution found",
    )
