"""
CNF Knowledge Base generator for the Futoshiki Puzzle Solver.

Automatically generates a propositional CNF Knowledge Base from FOL axioms (A1–A9)
grounded for a specific puzzle instance.
"""

from itertools import combinations
from typing import List

from models import Clause, KnowledgeBase, Puzzle


def _var(i: int, j: int, v: int) -> str:
    """Create propositional variable name: Val_i_j_v"""
    return f"Val_{i}_{j}_{v}"


def _neg(literal: str) -> str:
    """Negate a literal."""
    return literal[1:] if literal.startswith("-") else f"-{literal}"


def _gen_a1_completeness(n: int) -> List[Clause]:
    """A1: For each cell (i,j), at least one value must be true.
    Clause: [Val_i_j_1, Val_i_j_2, ..., Val_i_j_N]
    """
    clauses = []
    for i in range(n):
        for j in range(n):
            clauses.append(Clause(literals=[_var(i, j, v) for v in range(1, n + 1)]))
    return clauses


def _gen_a2_cell_uniqueness(n: int) -> List[Clause]:
    """A2: For each cell (i,j), at most one value can be true.
    Clause: [-Val_i_j_v1, -Val_i_j_v2] for each pair v1 < v2
    """
    clauses = []
    for i in range(n):
        for j in range(n):
            for v1, v2 in combinations(range(1, n + 1), 2):
                clauses.append(Clause(literals=[_neg(_var(i, j, v1)), _neg(_var(i, j, v2))]))
    return clauses


def _gen_a3_row_uniqueness(n: int) -> List[Clause]:
    """A3: For each row i, each value v appears at most once.
    Clause: [-Val_i_j1_v, -Val_i_j2_v] for each pair j1 < j2 and each value v
    """
    clauses = []
    for i in range(n):
        for j1, j2 in combinations(range(n), 2):
            for v in range(1, n + 1):
                clauses.append(Clause(literals=[_neg(_var(i, j1, v)), _neg(_var(i, j2, v))]))
    return clauses


def _gen_a4_col_uniqueness(n: int) -> List[Clause]:
    """A4: For each column j, each value v appears at most once.
    Clause: [-Val_i1_j_v, -Val_i2_j_v] for each pair i1 < i2 and each value v
    """
    clauses = []
    for j in range(n):
        for i1, i2 in combinations(range(n), 2):
            for v in range(1, n + 1):
                clauses.append(Clause(literals=[_neg(_var(i1, j, v)), _neg(_var(i2, j, v))]))
    return clauses


def _gen_a5_given_clues(puzzle: Puzzle) -> List[Clause]:
    """A5: For each given clue (i,j,v), add unit clause [Val_i_j_v]."""
    clauses = []
    for cell, value in puzzle.get_given_clues():
        clauses.append(Clause(literals=[_var(cell.row, cell.col, value)]))
    return clauses


def _gen_a6_h_less(puzzle: Puzzle) -> List[Clause]:
    """A6: For each LessH(i,j) constraint (cell(i,j) < cell(i,j+1)):
    For each pair (v1, v2) where v1 >= v2:
      Clause: [-Val_i_j_v1, -Val_i_(j+1)_v2]
    Also add fact: LessH_i_j
    """
    n = puzzle.n
    clauses = []
    for i in range(n):
        for j in range(n - 1):
            if puzzle.get_h_constraint(i, j) == "<":
                clauses.append(Clause(literals=[f"LessH_{i}_{j}"]))
                for v1 in range(1, n + 1):
                    for v2 in range(1, n + 1):
                        if v1 >= v2:
                            clauses.append(Clause(literals=[_neg(_var(i, j, v1)), _neg(_var(i, j + 1, v2))]))
    return clauses


def _gen_a7_h_greater(puzzle: Puzzle) -> List[Clause]:
    """A7: For each GreaterH(i,j) constraint (cell(i,j) > cell(i,j+1)):
    For each pair (v1, v2) where v1 <= v2:
      Clause: [-Val_i_j_v1, -Val_i_(j+1)_v2]
    Also add fact: GreaterH_i_j
    """
    n = puzzle.n
    clauses = []
    for i in range(n):
        for j in range(n - 1):
            if puzzle.get_h_constraint(i, j) == ">":
                clauses.append(Clause(literals=[f"GreaterH_{i}_{j}"]))
                for v1 in range(1, n + 1):
                    for v2 in range(1, n + 1):
                        if v1 <= v2:
                            clauses.append(Clause(literals=[_neg(_var(i, j, v1)), _neg(_var(i, j + 1, v2))]))
    return clauses


def _gen_a8_v_less(puzzle: Puzzle) -> List[Clause]:
    """A8: For each LessV(i,j) constraint (cell(i,j) < cell(i+1,j)):
    For each pair (v1, v2) where v1 >= v2:
      Clause: [-Val_i_j_v1, -Val_(i+1)_j_v2]
    Also add fact: LessV_i_j
    """
    n = puzzle.n
    clauses = []
    for i in range(n - 1):
        for j in range(n):
            if puzzle.get_v_constraint(i, j) == "<":
                clauses.append(Clause(literals=[f"LessV_{i}_{j}"]))
                for v1 in range(1, n + 1):
                    for v2 in range(1, n + 1):
                        if v1 >= v2:
                            clauses.append(Clause(literals=[_neg(_var(i, j, v1)), _neg(_var(i + 1, j, v2))]))
    return clauses


def _gen_a9_v_greater(puzzle: Puzzle) -> List[Clause]:
    """A9: For each GreaterV(i,j) constraint (cell(i,j) > cell(i+1,j)):
    For each pair (v1, v2) where v1 <= v2:
      Clause: [-Val_i_j_v1, -Val_(i+1)_j_v2]
    Also add fact: GreaterV_i_j
    """
    n = puzzle.n
    clauses = []
    for i in range(n - 1):
        for j in range(n):
            if puzzle.get_v_constraint(i, j) == ">":
                clauses.append(Clause(literals=[f"GreaterV_{i}_{j}"]))
                for v1 in range(1, n + 1):
                    for v2 in range(1, n + 1):
                        if v1 <= v2:
                            clauses.append(Clause(literals=[_neg(_var(i, j, v1)), _neg(_var(i + 1, j, v2))]))
    return clauses


def generate_kb(puzzle: Puzzle) -> KnowledgeBase:
    """Generate full CNF KB from all 9 FOL axioms for the given puzzle."""
    kb = KnowledgeBase(n=puzzle.n)

    # A1–A4: structural axioms (independent of puzzle instance)
    for clause in _gen_a1_completeness(puzzle.n):
        kb.add_clause(clause)

    for clause in _gen_a2_cell_uniqueness(puzzle.n):
        kb.add_clause(clause)

    for clause in _gen_a3_row_uniqueness(puzzle.n):
        kb.add_clause(clause)

    for clause in _gen_a4_col_uniqueness(puzzle.n):
        kb.add_clause(clause)

    # A5: given clues as facts
    for clause in _gen_a5_given_clues(puzzle):
        literal = clause.literals[0]
        kb.add_fact(literal)

    # A6–A9: inequality constraints as facts + exclusion clauses
    for clause in _gen_a6_h_less(puzzle):
        if len(clause.literals) == 1 and not clause.literals[0].startswith("-"):
            kb.add_fact(clause.literals[0])
        else:
            kb.add_clause(clause)

    for clause in _gen_a7_h_greater(puzzle):
        if len(clause.literals) == 1 and not clause.literals[0].startswith("-"):
            kb.add_fact(clause.literals[0])
        else:
            kb.add_clause(clause)

    for clause in _gen_a8_v_less(puzzle):
        if len(clause.literals) == 1 and not clause.literals[0].startswith("-"):
            kb.add_fact(clause.literals[0])
        else:
            kb.add_clause(clause)

    for clause in _gen_a9_v_greater(puzzle):
        if len(clause.literals) == 1 and not clause.literals[0].startswith("-"):
            kb.add_fact(clause.literals[0])
        else:
            kb.add_clause(clause)

    return kb
