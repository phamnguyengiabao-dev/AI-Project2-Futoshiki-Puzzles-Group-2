"""
Data models for the Futoshiki Puzzle Solver.

Defines core data structures: Cell, Constraint, Puzzle, Clause, KnowledgeBase, SolverResult.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Cell:
    row: int    # 0-indexed
    col: int    # 0-indexed


@dataclass
class Constraint:
    cell1: Cell
    cell2: Cell
    relation: str   # "<" or ">"


@dataclass
class Puzzle:
    n: int
    grid: List[List[int]]           # N×N, 0=empty, 1..N=given clue
    h_constraints: List[List[int]]  # N×(N-1), 0=none, 1="<", -1=">"
    v_constraints: List[List[int]]  # (N-1)×N, 0=none, 1="<", -1=">"

    def get_given_clues(self) -> List[Tuple[Cell, int]]:
        """Return list of (Cell, value) for all pre-filled cells."""
        clues = []
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] != 0:
                    clues.append((Cell(i, j), self.grid[i][j]))
        return clues

    def get_h_constraint(self, i: int, j: int) -> Optional[str]:
        """Return "<", ">" or None for horizontal constraint between (i,j) and (i,j+1)."""
        val = self.h_constraints[i][j]
        if val == 1:
            return "<"
        elif val == -1:
            return ">"
        return None

    def get_v_constraint(self, i: int, j: int) -> Optional[str]:
        """Return "<", ">" or None for vertical constraint between (i,j) and (i+1,j)."""
        val = self.v_constraints[i][j]
        if val == 1:
            return "<"
        elif val == -1:
            return ">"
        return None

    def is_valid_solution(self, assignment: Dict[Tuple[int, int], int]) -> bool:
        """Check if assignment satisfies all Futoshiki constraints."""
        n = self.n

        # Check all cells are assigned with values in 1..N
        for i in range(n):
            for j in range(n):
                v = assignment.get((i, j))
                if v is None or v < 1 or v > n:
                    return False

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

        # Check horizontal constraints
        for i in range(n):
            for j in range(n - 1):
                c = self.h_constraints[i][j]
                if c == 1 and not (assignment[(i, j)] < assignment[(i, j + 1)]):
                    return False
                if c == -1 and not (assignment[(i, j)] > assignment[(i, j + 1)]):
                    return False

        # Check vertical constraints
        for i in range(n - 1):
            for j in range(n):
                c = self.v_constraints[i][j]
                if c == 1 and not (assignment[(i, j)] < assignment[(i + 1, j)]):
                    return False
                if c == -1 and not (assignment[(i, j)] > assignment[(i + 1, j)]):
                    return False

        # Check given clues are respected
        for cell, value in self.get_given_clues():
            if assignment.get((cell.row, cell.col)) != value:
                return False

        return True


@dataclass
class Clause:
    literals: List[str]   # Positive: "Val_i_j_v", Negative: "-Val_i_j_v"


@dataclass
class KnowledgeBase:
    clauses: List[Clause] = field(default_factory=list)
    facts: Set[str] = field(default_factory=set)
    n: int = 0

    def add_clause(self, clause: Clause) -> None:
        """Add a clause to the knowledge base."""
        self.clauses.append(clause)

    def add_fact(self, literal: str) -> None:
        """Add a unit fact to the knowledge base."""
        self.facts.add(literal)
        self.clauses.append(Clause(literals=[literal]))

    def get_unit_clauses(self) -> List[Clause]:
        """Return all unit clauses (clauses with exactly one literal)."""
        return [c for c in self.clauses if len(c.literals) == 1]


@dataclass
class SolverResult:
    algorithm: str
    solution: Optional[Dict[Tuple[int, int], int]]
    solved: bool
    time_ms: float
    message: str = ""
