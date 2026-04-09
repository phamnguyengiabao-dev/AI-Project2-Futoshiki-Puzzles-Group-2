"""
A* Search solver for the Futoshiki Puzzle Solver.

Uses an admissible heuristic (number of unassigned cells) with AC3 constraint
propagation and MRV tie-breaking to efficiently find the solution.
"""

import heapq
import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from models import Puzzle, SolverResult


@dataclass
class SearchState:
    assignment: Dict[Tuple[int, int], int]    # (row,col) -> value (0 = unassigned)
    domains: Dict[Tuple[int, int], Set[int]]  # remaining domains per cell
    g: int                                     # cost so far (cells assigned)

    def h(self) -> int:
        """Heuristic: number of unassigned cells."""
        return sum(1 for v in self.assignment.values() if v == 0)

    def f(self) -> int:
        return self.g + self.h()

    def __lt__(self, other):
        return self.f() < other.f()


def _ac3(
    domains: Dict[Tuple[int, int], Set[int]], puzzle: Puzzle
) -> Tuple[Optional[Dict], bool]:
    """
    AC3 algorithm for arc consistency.
    Returns: (updated_domains, is_consistent)
    If any domain becomes empty, returns (None, False).
    """
    n = puzzle.n
    domains = {cell: set(vals) for cell, vals in domains.items()}

    # Build initial queue of all arcs
    queue: List[Tuple[Tuple[int, int], Tuple[int, int], str]] = []

    # Row arcs: all-different within each row
    for i in range(n):
        for j1 in range(n):
            for j2 in range(n):
                if j1 != j2:
                    queue.append(((i, j1), (i, j2), "neq"))

    # Column arcs: all-different within each column
    for j in range(n):
        for i1 in range(n):
            for i2 in range(n):
                if i1 != i2:
                    queue.append(((i1, j), (i2, j), "neq"))

    # Horizontal inequality arcs
    for i in range(n):
        for j in range(n - 1):
            c = puzzle.h_constraints[i][j]
            if c == 1:   # cell(i,j) < cell(i,j+1)
                queue.append(((i, j), (i, j + 1), "lt"))
                queue.append(((i, j + 1), (i, j), "gt"))
            elif c == -1:  # cell(i,j) > cell(i,j+1)
                queue.append(((i, j), (i, j + 1), "gt"))
                queue.append(((i, j + 1), (i, j), "lt"))

    # Vertical inequality arcs
    for i in range(n - 1):
        for j in range(n):
            c = puzzle.v_constraints[i][j]
            if c == 1:   # cell(i,j) < cell(i+1,j)
                queue.append(((i, j), (i + 1, j), "lt"))
                queue.append(((i + 1, j), (i, j), "gt"))
            elif c == -1:  # cell(i,j) > cell(i+1,j)
                queue.append(((i, j), (i + 1, j), "gt"))
                queue.append(((i + 1, j), (i, j), "lt"))

    # Process queue
    queue_set = list(queue)  # use list as deque
    idx = 0
    while idx < len(queue_set):
        xi, xj, rel = queue_set[idx]
        idx += 1

        revised = False
        to_remove = set()

        for v in domains[xi]:
            # Check if there exists any w in D[xj] satisfying the constraint
            has_support = False
            for w in domains[xj]:
                if rel == "neq" and v != w:
                    has_support = True
                    break
                elif rel == "lt" and v < w:
                    has_support = True
                    break
                elif rel == "gt" and v > w:
                    has_support = True
                    break
            if not has_support:
                to_remove.add(v)
                revised = True

        if revised:
            domains[xi] -= to_remove
            if not domains[xi]:
                return None, False

            # Add all arcs (xk, xi) back to queue for re-checking
            # Row neighbors
            ri, ci = xi
            for k in range(n):
                if k != ci:
                    queue_set.append(((ri, k), xi, "neq"))
            for k in range(n):
                if k != ri:
                    queue_set.append(((k, ci), xi, "neq"))

            # Inequality neighbors of xi
            ri, ci = xi
            # Horizontal
            if ci > 0:
                c = puzzle.h_constraints[ri][ci - 1]
                if c == 1:
                    queue_set.append(((ri, ci - 1), xi, "lt"))
                elif c == -1:
                    queue_set.append(((ri, ci - 1), xi, "gt"))
            if ci < n - 1:
                c = puzzle.h_constraints[ri][ci]
                if c == 1:
                    queue_set.append(((ri, ci + 1), xi, "gt"))
                elif c == -1:
                    queue_set.append(((ri, ci + 1), xi, "lt"))
            # Vertical
            if ri > 0:
                c = puzzle.v_constraints[ri - 1][ci]
                if c == 1:
                    queue_set.append(((ri - 1, ci), xi, "lt"))
                elif c == -1:
                    queue_set.append(((ri - 1, ci), xi, "gt"))
            if ri < n - 1:
                c = puzzle.v_constraints[ri][ci]
                if c == 1:
                    queue_set.append(((ri + 1, ci), xi, "gt"))
                elif c == -1:
                    queue_set.append(((ri + 1, ci), xi, "lt"))

    return domains, True


def _select_unassigned_cell(state: SearchState) -> Optional[Tuple[int, int]]:
    """MRV: select unassigned cell with smallest domain."""
    best_cell = None
    best_size = float("inf")
    for cell, val in state.assignment.items():
        if val == 0:
            size = len(state.domains[cell])
            if size < best_size:
                best_size = size
                best_cell = cell
    return best_cell


def _get_successors(state: SearchState, puzzle: Puzzle) -> List[SearchState]:
    """Generate successor states by assigning a value to the next cell."""
    cell = _select_unassigned_cell(state)
    if cell is None:
        return []

    successors = []
    for value in sorted(state.domains[cell]):
        new_assignment = dict(state.assignment)
        new_assignment[cell] = value

        # Fix domain of assigned cell to singleton
        new_domains = {c: set(d) for c, d in state.domains.items()}
        new_domains[cell] = {value}

        updated_domains, consistent = _ac3(new_domains, puzzle)
        if not consistent:
            continue

        # Sync assignment with any cells whose domain collapsed to a singleton
        for c, dom in updated_domains.items():
            if len(dom) == 1 and new_assignment[c] == 0:
                (v,) = dom
                new_assignment[c] = v

        new_state = SearchState(
            assignment=new_assignment,
            domains=updated_domains,
            g=state.g + 1,
        )
        successors.append(new_state)

    return successors


def solve(puzzle: Puzzle) -> SolverResult:
    """A* Search with AC3 constraint propagation."""
    start_time = time.time()
    n = puzzle.n

    # Initialize assignment and domains
    assignment: Dict[Tuple[int, int], int] = {}
    domains: Dict[Tuple[int, int], Set[int]] = {}

    for i in range(n):
        for j in range(n):
            v = puzzle.grid[i][j]
            assignment[(i, j)] = v
            if v != 0:
                domains[(i, j)] = {v}
            else:
                domains[(i, j)] = set(range(1, n + 1))

    # Initial AC3 pass
    updated_domains, consistent = _ac3(domains, puzzle)
    if not consistent:
        elapsed = (time.time() - start_time) * 1000
        return SolverResult(
            algorithm="A* Search",
            solution=None,
            solved=False,
            time_ms=elapsed,
            message="Initial AC3 detected inconsistency — puzzle has no solution.",
        )

    # Sync assignment with singleton domains after initial AC3
    for cell, dom in updated_domains.items():
        if len(dom) == 1 and assignment[cell] == 0:
            (v,) = dom
            assignment[cell] = v

    initial_state = SearchState(assignment=assignment, domains=updated_domains, g=0)

    # Check if already solved after initial propagation
    if initial_state.h() == 0:
        if puzzle.is_valid_solution(initial_state.assignment):
            elapsed = (time.time() - start_time) * 1000
            return SolverResult(
                algorithm="A* Search",
                solution=initial_state.assignment,
                solved=True,
                time_ms=elapsed,
            )

    # A* priority queue: (f, counter, state)
    counter = 0
    heap: List[Tuple[int, int, SearchState]] = []
    heapq.heappush(heap, (initial_state.f(), counter, initial_state))

    while heap:
        _, _, current = heapq.heappop(heap)

        # Goal check: all cells assigned
        if current.h() == 0:
            if puzzle.is_valid_solution(current.assignment):
                elapsed = (time.time() - start_time) * 1000
                return SolverResult(
                    algorithm="A* Search",
                    solution=current.assignment,
                    solved=True,
                    time_ms=elapsed,
                )
            continue

        for successor in _get_successors(current, puzzle):
            counter += 1
            heapq.heappush(heap, (successor.f(), counter, successor))

    elapsed = (time.time() - start_time) * 1000
    return SolverResult(
        algorithm="A* Search",
        solution=None,
        solved=False,
        time_ms=elapsed,
        message="No solution found.",
    )
