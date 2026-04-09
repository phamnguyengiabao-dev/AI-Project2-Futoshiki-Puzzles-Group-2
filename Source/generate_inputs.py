"""
Script to generate valid Futoshiki input files from known solutions.
Each puzzle is defined by a complete solution grid + chosen constraints,
then some cells are hidden to create the puzzle.
"""

import os
import random

def make_puzzle(solution, h_constraints, v_constraints, hide_cells):
    """
    Create a puzzle from a solution by hiding specified cells.
    solution: list of lists (N x N)
    h_constraints: list of lists (N x N-1), 0/1/-1
    v_constraints: list of lists (N-1 x N), 0/1/-1
    hide_cells: set of (i,j) to hide (set to 0)
    """
    n = len(solution)
    grid = [row[:] for row in solution]
    for (i, j) in hide_cells:
        grid[i][j] = 0
    return n, grid, h_constraints, v_constraints

def write_input(filename, n, grid, h_constraints, v_constraints):
    lines = [str(n)]
    lines.append("# Grid: 0=empty, 1..N=given")
    for row in grid:
        lines.append(",".join(str(v) for v in row))
    lines.append("# Horizontal constraints: 0=none, 1=<, -1=>")
    for row in h_constraints:
        lines.append(",".join(str(v) for v in row))
    lines.append("# Vertical constraints: 0=none, 1=<, -1=>")
    for row in v_constraints:
        lines.append(",".join(str(v) for v in row))
    with open(filename, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Written: {filename}")

def verify_solution(solution, h_constraints, v_constraints):
    """Verify a solution is valid."""
    n = len(solution)
    for i in range(n):
        if sorted(solution[i]) != list(range(1, n+1)):
            return False, f"Row {i} not a permutation: {solution[i]}"
    for j in range(n):
        col = [solution[i][j] for i in range(n)]
        if sorted(col) != list(range(1, n+1)):
            return False, f"Col {j} not a permutation: {col}"
    for i in range(n):
        for j in range(n-1):
            c = h_constraints[i][j]
            if c == 1 and not (solution[i][j] < solution[i][j+1]):
                return False, f"H constraint fail at ({i},{j}): {solution[i][j]} < {solution[i][j+1]}"
            if c == -1 and not (solution[i][j] > solution[i][j+1]):
                return False, f"H constraint fail at ({i},{j}): {solution[i][j]} > {solution[i][j+1]}"
    for i in range(n-1):
        for j in range(n):
            c = v_constraints[i][j]
            if c == 1 and not (solution[i][j] < solution[i+1][j]):
                return False, f"V constraint fail at ({i},{j}): {solution[i][j]} < {solution[i+1][j]}"
            if c == -1 and not (solution[i][j] > solution[i+1][j]):
                return False, f"V constraint fail at ({i},{j}): {solution[i][j]} > {solution[i+1][j]}"
    return True, "OK"

def derive_constraints(solution, h_mask, v_mask):
    """
    Derive constraints from solution where mask is 1.
    h_mask[i][j]=1 means add h constraint between (i,j) and (i,j+1)
    v_mask[i][j]=1 means add v constraint between (i,j) and (i+1,j)
    """
    n = len(solution)
    h_constraints = [[0]*(n-1) for _ in range(n)]
    v_constraints = [[0]*n for _ in range(n-1)]
    for i in range(n):
        for j in range(n-1):
            if h_mask[i][j]:
                h_constraints[i][j] = 1 if solution[i][j] < solution[i][j+1] else -1
    for i in range(n-1):
        for j in range(n):
            if v_mask[i][j]:
                v_constraints[i][j] = 1 if solution[i][j] < solution[i+1][j] else -1
    return h_constraints, v_constraints

# ============================================================
# PUZZLE DEFINITIONS (all solutions verified manually)
# ============================================================

os.makedirs("Inputs", exist_ok=True)

# --- input-01: 4x4, >60% filled (12/16 cells given) ---
sol1 = [
    [2, 3, 4, 1],
    [1, 4, 2, 3],
    [4, 1, 3, 2],
    [3, 2, 1, 4],
]
h1 = [[1,0,0],[0,0,1],[0,1,0],[0,0,0]]  # 2<3, 2<3, 1<3
v1 = [[0,0,0,0],[1,0,0,0],[0,0,1,0]]    # 1<4, 3<? wait let me derive
h_mask1 = [[1,0,1],[0,1,0],[1,0,1],[0,1,0]]
v_mask1 = [[1,0,1,0],[0,1,0,1],[1,0,1,0]]
h1, v1 = derive_constraints(sol1, h_mask1, v_mask1)
ok, msg = verify_solution(sol1, h1, v1)
print(f"input-01 solution valid: {ok} {msg}")
hide1 = {(0,3),(1,0),(2,1),(3,2)}  # hide 4 cells -> 12/16 given
n1, g1, hc1, vc1 = make_puzzle(sol1, h1, v1, hide1)
write_input("Inputs/input-01.txt", n1, g1, hc1, vc1)

# --- input-02: 4x4, <30% filled (3/16 cells given) ---
sol2 = [
    [1, 2, 3, 4],
    [3, 4, 1, 2],
    [2, 3, 4, 1],
    [4, 1, 2, 3],
]
h_mask2 = [[1,0,1],[0,1,0],[1,0,1],[0,1,0]]
v_mask2 = [[0,1,0,1],[1,0,1,0],[0,1,0,1]]
h2, v2 = derive_constraints(sol2, h_mask2, v_mask2)
ok, msg = verify_solution(sol2, h2, v2)
print(f"input-02 solution valid: {ok} {msg}")
# Keep only 3 cells: (0,0)=1, (1,2)=1, (3,3)=3
all_cells2 = [(i,j) for i in range(4) for j in range(4)]
keep2 = {(0,0),(1,2),(3,3)}
hide2 = set(all_cells2) - keep2
n2, g2, hc2, vc2 = make_puzzle(sol2, h2, v2, hide2)
write_input("Inputs/input-02.txt", n2, g2, hc2, vc2)

# --- input-03: 5x5, >60% filled (17/25 cells given) ---
sol3 = [
    [1, 2, 3, 4, 5],
    [3, 4, 5, 1, 2],
    [5, 1, 2, 3, 4],
    [2, 3, 4, 5, 1],
    [4, 5, 1, 2, 3],
]
h_mask3 = [[1,0,1,0],[0,1,0,1],[1,0,1,0],[0,1,0,1],[1,0,1,0]]
v_mask3 = [[1,0,0,1,0],[0,1,0,0,1],[1,0,1,0,0],[0,1,0,1,0]]
h3, v3 = derive_constraints(sol3, h_mask3, v_mask3)
ok, msg = verify_solution(sol3, h3, v3)
print(f"input-03 solution valid: {ok} {msg}")
hide3 = {(0,1),(0,3),(1,0),(2,2),(3,4),(4,1),(4,3),(8,8)}  # 8 cells
hide3 = {(0,1),(0,3),(1,0),(2,2),(3,4),(4,1),(4,3),(1,4)}  # 8 cells -> 17/25
n3, g3, hc3, vc3 = make_puzzle(sol3, h3, v3, hide3)
write_input("Inputs/input-03.txt", n3, g3, hc3, vc3)

# --- input-04: 5x5, <30% filled (6/25 cells given) ---
sol4 = [
    [2, 4, 1, 5, 3],
    [5, 1, 3, 2, 4],
    [3, 2, 4, 1, 5],
    [1, 5, 2, 4, 3],  # wait: col check
    [4, 3, 5, 3, 1],  # col3: 5,2,1,4,3 OK; col4: 3,4,5,3,1 NOT OK
]
# Use a proper Latin square for 5x5
sol4 = [
    [1, 2, 3, 4, 5],
    [2, 3, 4, 5, 1],
    [3, 4, 5, 1, 2],
    [4, 5, 1, 2, 3],
    [5, 1, 2, 3, 4],
]
h_mask4 = [[1,0,0,1],[0,1,0,0],[0,0,1,0],[1,0,0,1],[0,1,0,0]]
v_mask4 = [[1,0,0,0,1],[0,1,0,0,0],[0,0,1,0,0],[0,0,0,1,0]]
h4, v4 = derive_constraints(sol4, h_mask4, v_mask4)
ok, msg = verify_solution(sol4, h4, v4)
print(f"input-04 solution valid: {ok} {msg}")
keep4 = {(0,0),(1,2),(2,4),(3,1),(4,3),(0,4)}  # 6 cells
all_cells4 = [(i,j) for i in range(5) for j in range(5)]
hide4 = set(all_cells4) - keep4
n4, g4, hc4, vc4 = make_puzzle(sol4, h4, v4, hide4)
write_input("Inputs/input-04.txt", n4, g4, hc4, vc4)

# --- input-05: 6x6, >60% filled (23/36 cells given) ---
sol5 = [
    [1, 2, 3, 4, 5, 6],
    [2, 3, 4, 5, 6, 1],
    [3, 4, 5, 6, 1, 2],
    [4, 5, 6, 1, 2, 3],
    [5, 6, 1, 2, 3, 4],
    [6, 1, 2, 3, 4, 5],
]
h_mask5 = [[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0]]
v_mask5 = [[1,0,0,1,0,0],[0,1,0,0,1,0],[0,0,1,0,0,1],[1,0,0,1,0,0],[0,1,0,0,1,0]]
h5, v5 = derive_constraints(sol5, h_mask5, v_mask5)
ok, msg = verify_solution(sol5, h5, v5)
print(f"input-05 solution valid: {ok} {msg}")
hide5 = {(0,1),(0,3),(1,0),(1,4),(2,2),(3,1),(3,5),(4,0),(4,3),(5,2),(5,4),(2,5),(3,3)}  # 13 cells -> 23/36
n5, g5, hc5, vc5 = make_puzzle(sol5, h5, v5, hide5)
write_input("Inputs/input-05.txt", n5, g5, hc5, vc5)

# --- input-06: 6x6, <30% filled (8/36 cells given) ---
sol6 = [
    [6, 1, 2, 3, 4, 5],
    [5, 6, 1, 2, 3, 4],
    [4, 5, 6, 1, 2, 3],
    [3, 4, 5, 6, 1, 2],
    [2, 3, 4, 5, 6, 1],
    [1, 2, 3, 4, 5, 6],
]
h_mask6 = [[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1],[0,1,0,1,0],[1,0,1,0,1]]
v_mask6 = [[1,0,1,0,0,1],[0,1,0,1,0,0],[1,0,1,0,1,0],[0,1,0,1,0,1],[1,0,1,0,1,0]]
h6, v6 = derive_constraints(sol6, h_mask6, v_mask6)
ok, msg = verify_solution(sol6, h6, v6)
print(f"input-06 solution valid: {ok} {msg}")
keep6 = {(0,0),(1,2),(2,4),(3,1),(4,3),(5,5),(0,5),(3,3)}  # 8 cells
all_cells6 = [(i,j) for i in range(6) for j in range(6)]
hide6 = set(all_cells6) - keep6
n6, g6, hc6, vc6 = make_puzzle(sol6, h6, v6, hide6)
write_input("Inputs/input-06.txt", n6, g6, hc6, vc6)

# --- input-07: 6x6, medium (~45% filled, 16/36 cells given) ---
sol7 = [
    [3, 6, 2, 5, 1, 4],
    [5, 1, 4, 2, 6, 3],
    [6, 2, 5, 1, 4, 3],  # col check: col5 = 4,3,3... NOT OK
]
# Use cyclic shift
sol7 = [
    [1, 3, 5, 2, 4, 6],
    [4, 6, 2, 5, 1, 3],
    [2, 5, 1, 4, 6, 3],  # col3: 2,5,4,1,3,6 OK; col5: 6,3,3... NOT OK
]
# Use a proper 6x6 Latin square
sol7 = [
    [1, 2, 3, 4, 5, 6],
    [3, 4, 5, 6, 1, 2],
    [5, 6, 1, 2, 3, 4],
    [2, 1, 4, 3, 6, 5],
    [4, 3, 6, 5, 2, 1],
    [6, 5, 2, 1, 4, 3],
]
h_mask7 = [[1,0,1,0,0],[0,1,0,0,1],[1,0,0,1,0],[0,0,1,0,1],[1,0,0,1,0],[0,1,0,0,1]]
v_mask7 = [[1,0,0,1,0,0],[0,1,0,0,1,0],[1,0,1,0,0,1],[0,1,0,1,0,0],[1,0,1,0,1,0]]
h7, v7 = derive_constraints(sol7, h_mask7, v_mask7)
ok, msg = verify_solution(sol7, h7, v7)
print(f"input-07 solution valid: {ok} {msg}")
hide7 = {(0,1),(0,3),(0,5),(1,0),(1,2),(2,1),(2,3),(3,0),(3,4),(4,1),(4,3),(4,5),(5,0),(5,2),(5,4),(1,5),(2,5),(3,2),(3,5),(4,2)}  # 20 cells -> 16/36
n7, g7, hc7, vc7 = make_puzzle(sol7, h7, v7, hide7)
write_input("Inputs/input-07.txt", n7, g7, hc7, vc7)

# --- input-08: 7x7 (~40% filled, 20/49 cells given) ---
# Build a 7x7 Latin square using cyclic shifts
sol8 = []
base = [1,2,3,4,5,6,7]
for i in range(7):
    sol8.append([(base[(j + i*2) % 7]) for j in range(7)])
# Verify it's a Latin square
for i in range(7):
    assert sorted(sol8[i]) == list(range(1,8)), f"Row {i} bad"
for j in range(7):
    col = [sol8[i][j] for i in range(7)]
    assert sorted(col) == list(range(1,8)), f"Col {j} bad"
h_mask8 = [[1,0,1,0,0,1],[0,1,0,1,0,0],[1,0,0,1,0,1],[0,1,0,0,1,0],[1,0,1,0,0,1],[0,1,0,1,0,0],[1,0,0,1,0,1]]
v_mask8 = [[1,0,1,0,0,1,0],[0,1,0,1,0,0,1],[1,0,0,1,0,1,0],[0,1,0,0,1,0,1],[1,0,1,0,0,1,0],[0,1,0,1,0,0,1]]
h8, v8 = derive_constraints(sol8, h_mask8, v_mask8)
ok, msg = verify_solution(sol8, h8, v8)
print(f"input-08 solution valid: {ok} {msg}")
all_cells8 = [(i,j) for i in range(7) for j in range(7)]
# Keep 20 cells (every other cell in a pattern)
keep8 = set()
for i in range(7):
    for j in range(7):
        if (i + j) % 3 == 0:
            keep8.add((i,j))
# Trim to exactly 20
keep8 = list(keep8)[:20]
keep8 = set(keep8)
hide8 = set(all_cells8) - keep8
n8, g8, hc8, vc8 = make_puzzle(sol8, h8, v8, hide8)
write_input("Inputs/input-08.txt", n8, g8, hc8, vc8)

# --- input-09: 9x9, >60% filled (55/81 cells given) ---
sol9 = []
base9 = list(range(1, 10))
# Use shift of 1 per row (guaranteed Latin square)
for i in range(9):
    sol9.append([(base9[(j + i) % 9]) for j in range(9)])
for i in range(9):
    assert sorted(sol9[i]) == list(range(1,10))
for j in range(9):
    col = [sol9[i][j] for i in range(9)]
    assert sorted(col) == list(range(1,10))
h_mask9 = [[1,0,1,0,0,1,0,1],[0,1,0,1,0,0,1,0],[1,0,0,1,0,1,0,0],[0,1,0,0,1,0,1,0],[1,0,1,0,0,1,0,1],[0,1,0,1,0,0,1,0],[1,0,0,1,0,1,0,0],[0,1,0,0,1,0,1,0],[1,0,1,0,0,1,0,1]]
v_mask9 = [[1,0,1,0,0,1,0,1,0],[0,1,0,1,0,0,1,0,1],[1,0,0,1,0,1,0,0,1],[0,1,0,0,1,0,1,0,0],[1,0,1,0,0,1,0,1,0],[0,1,0,1,0,0,1,0,1],[1,0,0,1,0,1,0,0,1],[0,1,0,0,1,0,1,0,0]]
h9, v9 = derive_constraints(sol9, h_mask9, v_mask9)
ok, msg = verify_solution(sol9, h9, v9)
print(f"input-09 solution valid: {ok} {msg}")
all_cells9 = [(i,j) for i in range(9) for j in range(9)]
# Hide 26 cells -> 55/81 given
hide9 = set()
for i in range(9):
    for j in range(9):
        if (i*9+j) % 3 == 1:
            hide9.add((i,j))
hide9 = set(list(hide9)[:26])
n9, g9, hc9, vc9 = make_puzzle(sol9, h9, v9, hide9)
write_input("Inputs/input-09.txt", n9, g9, hc9, vc9)

# --- input-10: 9x9, <30% filled (20/81 cells given) ---
sol10 = []
for i in range(9):
    sol10.append([(base9[(j + i*2) % 9]) for j in range(9)])
for i in range(9):
    assert sorted(sol10[i]) == list(range(1,10))
for j in range(9):
    col = [sol10[i][j] for i in range(9)]
    assert sorted(col) == list(range(1,10))
h_mask10 = [[1,1,0,1,1,0,1,1],[1,0,1,1,0,1,1,0],[0,1,1,0,1,1,0,1],[1,1,0,1,1,0,1,1],[1,0,1,1,0,1,1,0],[0,1,1,0,1,1,0,1],[1,1,0,1,1,0,1,1],[1,0,1,1,0,1,1,0],[0,1,1,0,1,1,0,1]]
v_mask10 = [[1,1,0,1,1,0,1,1,0],[1,0,1,1,0,1,1,0,1],[0,1,1,0,1,1,0,1,1],[1,1,0,1,1,0,1,1,0],[1,0,1,1,0,1,1,0,1],[0,1,1,0,1,1,0,1,1],[1,1,0,1,1,0,1,1,0],[1,0,1,1,0,1,1,0,1]]
h10, v10 = derive_constraints(sol10, h_mask10, v_mask10)
ok, msg = verify_solution(sol10, h10, v10)
print(f"input-10 solution valid: {ok} {msg}")
all_cells10 = [(i,j) for i in range(9) for j in range(9)]
# Keep only 20 cells
keep10 = [(i,j) for i in range(9) for j in range(9) if (i*9+j) % 4 == 0][:20]
keep10 = set(keep10)
hide10 = set(all_cells10) - keep10
n10, g10, hc10, vc10 = make_puzzle(sol10, h10, v10, hide10)
write_input("Inputs/input-10.txt", n10, g10, hc10, vc10)

print("\nAll input files generated!")
