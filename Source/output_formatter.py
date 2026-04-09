"""
Output formatter for the Futoshiki Puzzle Solver.

Formats solved grids with inequality symbols between adjacent cells.

Output format (example 4×4):
    2 < 3   4   1
    v
    1   2 > 3   4
                ^
    4   1   2   3
    ^
    3   4   1 < 2

Rules:
- Each cell value occupies 1 character.
- Between horizontally adjacent cells: " < " or " > " (3 chars) if constraint, else "   " (3 spaces).
- Vertical separator rows: only the symbol (^ or v) at the column position of the constraint,
  rest is spaces. The symbol is aligned under the digit of the cell above.
- Empty separator rows (no vertical constraints on that row boundary) are omitted.
"""

import os
from typing import Dict, Tuple

from models import Puzzle


def _col_positions(puzzle: Puzzle) -> list:
    """
    Compute the character position of each column's digit in a formatted row.
    
    Row format: "d1 X d2 X d3 X d4" where X is '<', '>' or ' '
    Each cell digit is at position: j * 4  (0, 4, 8, 12, ...)
    Between cells: positions j*4+1, j*4+2, j*4+3 hold " X " or "   "
    """
    return [j * 4 for j in range(puzzle.n)]


def _format_row(puzzle: Puzzle, assignment: Dict[Tuple[int, int], int], row: int) -> str:
    """
    Format a single data row.
    
    Example: "2 < 3   4   1"
    - Between col j and col j+1: " < " if LessH, " > " if GreaterH, "   " otherwise
    """
    n = puzzle.n
    result = []
    for j in range(n):
        result.append(str(assignment[(row, j)]))
        if j < n - 1:
            c = puzzle.h_constraints[row][j]
            if c == 1:
                result.append(" < ")
            elif c == -1:
                result.append(" > ")
            else:
                result.append("   ")
    return "".join(result)


def _format_v_separator(puzzle: Puzzle, row: int) -> str:
    """
    Format the vertical separator line between row `row` and row `row+1`.
    
    Only prints '^' or 'v' at the exact character position of the column digit.
    All other positions are spaces.
    Returns empty string if no vertical constraints on this boundary.
    
    Column digit positions: j * 4  (since each cell+separator = 4 chars: "d   " or "d < ")
    """
    n = puzzle.n
    col_pos = _col_positions(puzzle)
    
    # Total row width = last col position + 1
    total_width = col_pos[-1] + 1
    chars = [' '] * total_width
    
    has_any = False
    for j in range(n):
        c = puzzle.v_constraints[row][j]
        if c == 1:
            chars[col_pos[j]] = '^'
            has_any = True
        elif c == -1:
            chars[col_pos[j]] = 'v'
            has_any = True
    
    if not has_any:
        return ""
    
    # Strip trailing spaces
    return "".join(chars).rstrip()


def format_solution(puzzle: Puzzle, assignment: Dict[Tuple[int, int], int]) -> str:
    """
    Format the complete solution grid with inequality symbols.
    
    Example output (4×4):
        2 < 3   4   1
        v
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
            sep = _format_v_separator(puzzle, i)
            # Always add separator line (even if empty, to match PDF format)
            lines.append(sep)
    return "\n".join(lines)


def write_output(content: str, output_path: str) -> None:
    """Write formatted solution to file, creating directories as needed."""
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        f.write("\n")
