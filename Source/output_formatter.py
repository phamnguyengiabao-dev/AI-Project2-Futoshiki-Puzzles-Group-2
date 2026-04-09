"""
Output formatter for the Futoshiki Puzzle Solver.

Formats solved grids with inequality symbols between adjacent cells.
"""

import os
from typing import Dict, Tuple

from models import Puzzle


def _format_row(puzzle: Puzzle, assignment: Dict[Tuple[int, int], int], row: int) -> str:
    """Format a single row with horizontal constraint symbols."""
    n = puzzle.n
    parts = []
    for j in range(n):
        parts.append(str(assignment[(row, j)]))
        if j < n - 1:
            c = puzzle.h_constraints[row][j]
            if c == 1:
                parts.append("<")
            elif c == -1:
                parts.append(">")
            else:
                parts.append(" ")
    return " ".join(parts)


def _format_v_separator(puzzle: Puzzle, row: int) -> str:
    """
    Format the vertical separator row between grid row `row` and row `row+1`.
    Uses '^' when top < bottom (v_constraint == 1),
         'v' when top > bottom (v_constraint == -1),
         ' ' when no constraint.
    Aligned under each cell column.
    """
    n = puzzle.n
    # Each cell value takes 1 char; separators between cells take 1 char each.
    # Total width per cell position = 1 (value) + 1 (space) + 1 (h-sep) + 1 (space) = 4
    # But we just need to align under the value character.
    # Row format: "v1 < v2   v3 > v4" — each value at positions 0, 4, 8, 12 (step 4 for N=4)
    # Actually the row is built as " ".join(parts) where parts alternate value/h-sep.
    # For N cells: positions of values in the joined string:
    #   j=0 → index 0, j=1 → index 2 (after "v1 X "), etc.
    # Let's just build the separator aligned to match _format_row output.

    parts = []
    for j in range(n):
        c = puzzle.v_constraints[row][j]
        if c == 1:
            parts.append("^")
        elif c == -1:
            parts.append("v")
        else:
            parts.append(" ")
        if j < n - 1:
            parts.append(" ")  # spacer under h-sep position
    return " ".join(parts)


def format_solution(puzzle: Puzzle, assignment: Dict[Tuple[int, int], int]) -> str:
    """
    Format the complete solution grid with inequality symbols.

    Example output (4×4):
        2 < 3   4   1
        v           ^
        1   2 > 3   4
                ^
        4   1   2   3
            ^
        3   4   1 < 2
    """
    n = puzzle.n
    lines = []
    for i in range(n):
        lines.append(_format_row(puzzle, assignment, i))
        if i < n - 1:
            lines.append(_format_v_separator(puzzle, i))
    return "\n".join(lines)


def write_output(content: str, output_path: str) -> None:
    """Write formatted solution to file, creating directories as needed."""
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        f.write("\n")
