"""
Input file parser for the Futoshiki Puzzle Solver.

Reads and validates Input_Files, producing Puzzle data structures.
Supports round-trip serialization for testing.

Input File Format:
    N
    grid_row_0: v0,v1,...,v(N-1)
    ...
    grid_row_(N-1): v0,v1,...,v(N-1)
    h_constraint_row_0: c0,c1,...,c(N-2)
    ...
    h_constraint_row_(N-1): c0,c1,...,c(N-2)
    v_constraint_row_0: c0,c1,...,c(N-1)
    ...
    v_constraint_row_(N-2): c0,c1,...,c(N-1)

Lines starting with '#' are comments and are ignored.
"""

from models import Puzzle


def _parse_lines(lines: list[str], source_name: str) -> Puzzle:
    """
    Core parsing logic shared by parse_puzzle and parse_from_string.

    Args:
        lines: raw lines (may include comments)
        source_name: used in error messages (file path or "<string>")

    Returns:
        Parsed Puzzle

    Raises:
        ValueError: on invalid data, with source_name and line number
    """
    # Strip comments and blank lines, keeping original line numbers (1-indexed)
    data_lines: list[tuple[int, str]] = []
    for lineno, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped and not stripped.startswith("#"):
            data_lines.append((lineno, stripped))

    if not data_lines:
        raise ValueError(f"{source_name}: file is empty or contains only comments")

    idx = 0  # index into data_lines

    def next_line() -> tuple[int, str]:
        nonlocal idx
        if idx >= len(data_lines):
            raise ValueError(
                f"{source_name}: unexpected end of file (expected more data)"
            )
        lineno, text = data_lines[idx]
        idx += 1
        return lineno, text

    def parse_int_list(text: str, lineno: int, expected_len: int,
                       valid_values: set[int] | None = None,
                       label: str = "") -> list[int]:
        """Parse a comma-separated list of ints from 'label: v0,v1,...'."""
        # Strip optional 'label:' prefix
        if ":" in text:
            text = text.split(":", 1)[1]
        parts = [p.strip() for p in text.split(",")]
        if len(parts) != expected_len:
            raise ValueError(
                f"{source_name} line {lineno}: expected {expected_len} values, "
                f"got {len(parts)}"
            )
        result = []
        for part in parts:
            try:
                v = int(part)
            except ValueError:
                raise ValueError(
                    f"{source_name} line {lineno}: '{part}' is not a valid integer"
                )
            if valid_values is not None and v not in valid_values:
                raise ValueError(
                    f"{source_name} line {lineno}: value {v} not in {sorted(valid_values)}"
                )
            result.append(v)
        return result

    # --- Parse N ---
    lineno, text = next_line()
    # N line may have a label prefix like "N:" or just be a bare integer
    n_text = text.split(":", 1)[-1].strip() if ":" in text else text
    try:
        n = int(n_text)
    except ValueError:
        raise ValueError(f"{source_name} line {lineno}: expected integer N, got '{text}'")
    if not (4 <= n <= 9):
        raise ValueError(
            f"{source_name} line {lineno}: N={n} is out of range [4, 9]"
        )

    # --- Parse N grid rows ---
    grid: list[list[int]] = []
    valid_grid = set(range(0, n + 1))  # 0..N
    for row in range(n):
        lineno, text = next_line()
        values = parse_int_list(text, lineno, n, valid_values=valid_grid,
                                label=f"grid_row_{row}")
        grid.append(values)

    # --- Parse N h_constraint rows (each has N-1 values) ---
    h_constraints: list[list[int]] = []
    valid_constraint = {-1, 0, 1}
    for row in range(n):
        lineno, text = next_line()
        values = parse_int_list(text, lineno, n - 1, valid_values=valid_constraint,
                                label=f"h_constraint_row_{row}")
        h_constraints.append(values)

    # --- Parse N-1 v_constraint rows (each has N values) ---
    v_constraints: list[list[int]] = []
    for row in range(n - 1):
        lineno, text = next_line()
        values = parse_int_list(text, lineno, n, valid_values=valid_constraint,
                                label=f"v_constraint_row_{row}")
        v_constraints.append(values)

    return Puzzle(n=n, grid=grid, h_constraints=h_constraints, v_constraints=v_constraints)


def parse_puzzle(file_path: str) -> Puzzle:
    """
    Read an Input_File and return a Puzzle.

    Args:
        file_path: path to the input file

    Returns:
        Parsed Puzzle

    Raises:
        FileNotFoundError: if the file does not exist
        ValueError: if data is invalid, message includes file name and line number
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")

    return _parse_lines(lines, source_name=file_path)


def parse_from_string(content: str) -> Puzzle:
    """
    Parse a Puzzle from a string (same format as Input_File).
    Useful for testing without touching the filesystem.

    Args:
        content: puzzle data as a multi-line string

    Returns:
        Parsed Puzzle

    Raises:
        ValueError: if data is invalid
    """
    lines = content.splitlines()
    return _parse_lines(lines, source_name="<string>")


def serialize_puzzle(puzzle: Puzzle) -> str:
    """
    Convert a Puzzle back to the Input_File format string.
    Includes comment lines explaining each section.

    Args:
        puzzle: the Puzzle to serialize

    Returns:
        Multi-line string in Input_File format
    """
    n = puzzle.n
    lines: list[str] = []

    # N
    lines.append(f"# Grid size")
    lines.append(str(n))

    # Grid rows
    lines.append(f"# Grid rows (0=empty, 1..{n}=given clue)")
    for i, row in enumerate(puzzle.grid):
        lines.append(f"grid_row_{i}: {','.join(str(v) for v in row)}")

    # Horizontal constraint rows
    lines.append(f"# Horizontal constraints (0=none, 1='<', -1='>')")
    for i, row in enumerate(puzzle.h_constraints):
        lines.append(f"h_constraint_row_{i}: {','.join(str(v) for v in row)}")

    # Vertical constraint rows
    lines.append(f"# Vertical constraints (0=none, 1='<', -1='>')")
    for i, row in enumerate(puzzle.v_constraints):
        lines.append(f"v_constraint_row_{i}: {','.join(str(v) for v in row)}")

    return "\n".join(lines)
