# Futoshiki Puzzle Solver

A Python application that solves Futoshiki logic puzzles on an N×N grid (4 ≤ N ≤ 9) using multiple AI algorithms.

## Overview

Futoshiki is a logic puzzle played on an N×N grid where each row and column must contain the numbers 1 to N exactly once, subject to inequality constraints between adjacent cells. This solver implements five algorithms:

- **Forward Chaining** — propagates known facts through a CNF Knowledge Base
- **Backward Chaining** — SLD resolution to answer queries of the form `Val(i,j,?)`
- **A\* Search** — informed search with AC3 constraint propagation and MRV tie-breaking
- **Backtracking** — systematic search with MRV heuristic and forward checking
- **Brute-Force** — exhaustive enumeration (baseline for comparison)

## Installation

Requires Python 3.7+. No external dependencies are needed for core solving. To install optional testing dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run a single algorithm

```bash
python main.py --input Inputs/input-01.txt --algorithm backtracking
python main.py --input Inputs/input-03.txt --algorithm astar
python main.py --input Inputs/input-05.txt --algorithm forward
python main.py --input Inputs/input-02.txt --algorithm backward
python main.py --input Inputs/input-01.txt --algorithm bruteforce
```

### Run all algorithms and compare

```bash
python main.py --input Inputs/input-01.txt --algorithm all
```

This prints a comparison table with algorithm name, solution status, and execution time in milliseconds.

### Specify a custom output file

```bash
python main.py --input Inputs/input-01.txt --algorithm backtracking --output Outputs/my-output.txt
```

### Available algorithm names

| Name            | Description                          |
|-----------------|--------------------------------------|
| `forward`       | Forward Chaining                     |
| `backward`      | Backward Chaining (SLD resolution)   |
| `astar`         | A\* Search with AC3                  |
| `backtracking`  | Backtracking with MRV                |
| `bruteforce`    | Brute-Force exhaustive search        |
| `all`           | Run all five and show comparison     |

## Input File Format

Input files are plain text named `input-XX.txt` and placed in `Inputs/`.

```
N
grid_row_0
...
grid_row_(N-1)
h_constraint_row_0
...
h_constraint_row_(N-1)
v_constraint_row_0
...
v_constraint_row_(N-2)
```

- **Line 1**: `N` — grid size (integer, 4 ≤ N ≤ 9)
- **Next N lines**: grid rows — N comma-separated integers per line
  - `0` = empty cell
  - `1..N` = pre-filled (given clue)
- **Next N lines**: horizontal constraint rows — (N-1) comma-separated integers per line
  - `0` = no constraint
  - `1` = left cell < right cell
  - `-1` = left cell > right cell
- **Next (N-1) lines**: vertical constraint rows — N comma-separated integers per line
  - `0` = no constraint
  - `1` = top cell < bottom cell
  - `-1` = top cell > bottom cell

### Example (4×4)

```
4
1,0,0,0
0,0,3,0
0,2,0,0
0,0,0,4
1,0,-1,0
0,1,0,0
0,0,1,0
0,-1,0,0
1,0,0,0
0,0,-1,0
```

## Output Format

Solutions are written to `Outputs/output-XX.txt` and printed to stdout. Cell values are displayed with inequality symbols between adjacent cells:

```
1 < 2   3   4
v       ^    
3   4   1 < 2
        v    
2   1   4   3
    ^        
4   3   2   1
```

- `<` / `>` — horizontal inequality between adjacent cells in the same row
- `^` — vertical constraint where top cell < bottom cell
- `v` — vertical constraint where top cell > bottom cell
- Single space — no constraint between adjacent cells
