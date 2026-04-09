"""
Forward Chaining solver for the Futoshiki Puzzle Solver.

Propagates known facts through the CNF Knowledge Base until a fixed point is reached.
Falls back to backtracking when forward chaining alone cannot fully determine the solution.
"""

import time
from typing import Dict, Optional, Set, Tuple

from models import KnowledgeBase, Puzzle, SolverResult


def _is_false(literal: str, facts: Set[str]) -> bool:
    """Return True if literal is known to be FALSE given the current fact set."""
    if literal.startswith("-"):
        # Negative literal "-X" is false when X is a fact
        return literal[1:] in facts
    else:
        # Positive literal "X" is false when "-X" is a fact
        return f"-{literal}" in facts


def _propagate(kb: KnowledgeBase) -> Tuple[Set[str], bool]:
    """
    Run forward chaining to fixed point.

    Algorithm:
      1. Seed facts from KB.facts (unit clauses already known).
      2. Iterate over all clauses:
         - Count unresolved literals (neither TRUE nor FALSE).
         - If exactly 1 unresolved literal and all others are FALSE → derive it.
      3. Repeat until no new facts are derived (fixed point).
      4. Check for contradictions: both L and -L in facts.

    Returns:
        (all_facts, has_contradiction)
    """
    facts: Set[str] = set(kb.facts)

    changed = True
    while changed:
        changed = False
        for clause in kb.clauses:
            # Collect unresolved literals (not yet TRUE and not FALSE)
            unresolved = []
            clause_satisfied = False

            for lit in clause.literals:
                if lit in facts:
                    # Literal is TRUE → clause already satisfied
                    clause_satisfied = True
                    break
                if not _is_false(lit, facts):
                    unresolved.append(lit)

            if clause_satisfied:
                continue

            # Unit propagation: if exactly one literal is unresolved and all
            # others are false, derive that literal as a new fact.
            if len(unresolved) == 1:
                new_fact = unresolved[0]
                if new_fact not in facts:
                    facts.add(new_fact)
                    changed = True

    # Contradiction check: both Val_i_j_v and -Val_i_j_v derived
    has_contradiction = any(
        f"-{fact}" in facts
        for fact in facts
        if not fact.startswith("-")
    )

    return facts, has_contradiction


def _is_complete(facts: Set[str], n: int) -> bool:
    """Check if all N×N cells have exactly one value assigned in the fact set."""
    for i in range(n):
        for j in range(n):
            assigned = [
                v for v in range(1, n + 1)
                if f"Val_{i}_{j}_{v}" in facts
            ]
            if len(assigned) != 1:
                return False
    return True


def _facts_to_assignment(facts: Set[str], n: int) -> Dict[Tuple[int, int], int]:
    """Convert fact set to assignment dict {(i, j): v}."""
    assignment: Dict[Tuple[int, int], int] = {}
    for i in range(n):
        for j in range(n):
            for v in range(1, n + 1):
                if f"Val_{i}_{j}_{v}" in facts:
                    assignment[(i, j)] = v
                    break
    return assignment


def solve(kb: KnowledgeBase, puzzle: Puzzle) -> SolverResult:
    """
    Solve using Forward Chaining.

    Steps:
      1. Run _propagate to fixed point.
      2. If contradiction → unsolvable.
      3. If complete → return solution.
      4. Otherwise → combine partial assignment with backtracking.
    """
    from backtracking import _backtrack, _is_consistent  # noqa: PLC0415

    start = time.time()
    n = puzzle.n

    facts, has_contradiction = _propagate(kb)

    if has_contradiction:
        elapsed = (time.time() - start) * 1000
        return SolverResult(
            algorithm="Forward Chaining",
            solution=None,
            solved=False,
            time_ms=elapsed,
            message="Contradiction detected during forward chaining",
        )

    if _is_complete(facts, n):
        elapsed = (time.time() - start) * 1000
        return SolverResult(
            algorithm="Forward Chaining",
            solution=_facts_to_assignment(facts, n),
            solved=True,
            time_ms=elapsed,
            message="Solved by forward chaining alone",
        )

    # Underdetermined — use backtracking to fill remaining cells
    partial = _facts_to_assignment(facts, n)

    # Build domains: cells already determined get singleton domains;
    # remaining cells get domains pruned by derived negative facts.
    domains: Dict[Tuple[int, int], Set[int]] = {}
    for i in range(n):
        for j in range(n):
            if (i, j) in partial:
                domains[(i, j)] = {partial[(i, j)]}
            else:
                domain = set()
                for v in range(1, n + 1):
                    neg = f"-Val_{i}_{j}_{v}"
                    if neg not in facts:
                        domain.add(v)
                domains[(i, j)] = domain if domain else set(range(1, n + 1))

    result = _backtrack(dict(partial), domains, puzzle)
    elapsed = (time.time() - start) * 1000

    if result is not None:
        return SolverResult(
            algorithm="Forward Chaining",
            solution=result,
            solved=True,
            time_ms=elapsed,
            message="Solved by forward chaining + backtracking",
        )

    return SolverResult(
        algorithm="Forward Chaining",
        solution=None,
        solved=False,
        time_ms=elapsed,
        message="No solution found",
    )
