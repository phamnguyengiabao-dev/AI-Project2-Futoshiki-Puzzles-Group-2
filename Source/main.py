"""
Main CLI entry point for the Futoshiki Puzzle Solver.

Usage:
    python main.py --input Inputs/input-01.txt --algorithm backtracking
    python main.py --input Inputs/input-01.txt --algorithm all
    python main.py --input Inputs/input-01.txt --algorithm astar --output Outputs/my-out.txt
"""

import argparse
import os
import sys
import time
from typing import List, Optional

from models import KnowledgeBase, Puzzle, SolverResult
from parser import parse_puzzle
from kb_generator import generate_kb
from output_formatter import format_solution, write_output


ALGORITHMS = ["forward", "backward", "astar", "backtracking", "bruteforce", "all"]


def _run_algorithm(name: str, puzzle: Puzzle, kb: KnowledgeBase,
                   timeout_sec: float = 60.0) -> SolverResult:
    """Dispatch to the appropriate solver with timeout."""
    import threading

    result_holder = [None]
    exception_holder = [None]

    def _run():
        try:
            if name == "forward":
                from forward_chaining import solve
                result_holder[0] = solve(kb, puzzle)
            elif name == "backward":
                from backward_chaining import solve
                result_holder[0] = solve(kb, puzzle)
            elif name == "astar":
                from astar import solve
                result_holder[0] = solve(puzzle)
            elif name == "backtracking":
                from backtracking import solve
                result_holder[0] = solve(puzzle)
            elif name == "bruteforce":
                from bruteforce import solve
                result_holder[0] = solve(puzzle)
            else:
                result_holder[0] = SolverResult(
                    algorithm=name, solution=None, solved=False,
                    time_ms=0.0, message=f"Unknown algorithm: {name}")
        except Exception as e:
            exception_holder[0] = e

    t = threading.Thread(target=_run, daemon=True)
    start = time.time()
    t.start()
    t.join(timeout=timeout_sec)
    elapsed = (time.time() - start) * 1000

    if t.is_alive():
        return SolverResult(
            algorithm=_algo_display_name(name),
            solution=None, solved=False,
            time_ms=elapsed,
            message=f"Timeout after {timeout_sec:.0f}s")
    if exception_holder[0]:
        return SolverResult(
            algorithm=_algo_display_name(name),
            solution=None, solved=False,
            time_ms=elapsed,
            message=f"Error: {exception_holder[0]}")
    return result_holder[0]


def _algo_display_name(name: str) -> str:
    mapping = {
        "forward": "Forward Chaining",
        "backward": "Backward Chaining",
        "astar": "A* Search",
        "backtracking": "Backtracking",
        "bruteforce": "Brute-Force",
    }
    return mapping.get(name, name)


def _print_comparison_table(results: List[SolverResult]) -> None:
    """Print a comparison table of all algorithm results."""
    print("\n" + "=" * 60)
    print(f"{'Algorithm':<20} {'Status':<10} {'Time (ms)':>12}")
    print("-" * 60)
    for r in results:
        status = "SOLVED" if r.solved else "FAILED"
        print(f"{r.algorithm:<20} {status:<10} {r.time_ms:>12.2f}")
    print("=" * 60 + "\n")


def _default_output_path(input_path: str) -> str:
    """Derive default output path from input path."""
    basename = os.path.basename(input_path)
    # input-01.txt → output-01.txt
    if basename.startswith("input-"):
        out_name = "output-" + basename[len("input-"):]
    else:
        out_name = "output-" + basename
    return os.path.join(os.path.dirname(input_path), "..", "Outputs", out_name)


def main():
    parser = argparse.ArgumentParser(
        description="Futoshiki Puzzle Solver — solve using multiple AI algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Algorithms:
  forward      Forward Chaining (CNF KB propagation)
  backward     Backward Chaining (SLD resolution)
  astar        A* Search with AC3 constraint propagation
  backtracking Backtracking with MRV + forward checking
  bruteforce   Brute-force exhaustive enumeration
  all          Run all algorithms and show comparison table

Examples:
  python main.py --input Inputs/input-01.txt --algorithm backtracking
  python main.py --input Inputs/input-03.txt --algorithm all
        """,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the input puzzle file (e.g. Inputs/input-01.txt)",
    )
    parser.add_argument(
        "--algorithm", "-a",
        default="backtracking",
        choices=ALGORITHMS,
        help="Algorithm to use (default: backtracking)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write the output file (default: Outputs/output-XX.txt)",
    )

    args = parser.parse_args()

    # Load puzzle
    try:
        puzzle = parse_puzzle(args.input)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded puzzle: {args.input} (N={puzzle.n})")

    # Generate KB (needed for forward/backward chaining)
    kb = generate_kb(puzzle)

    # Determine output path
    output_path = args.output or _default_output_path(args.input)

    if args.algorithm == "all":
        results = []
        # Use shorter timeout for bruteforce on large puzzles
        bf_timeout = 30.0 if puzzle.n <= 5 else 10.0
        timeouts = {"bruteforce": bf_timeout}
        for alg in ["forward", "backward", "astar", "backtracking", "bruteforce"]:
            print(f"Running {alg}...", end=" ", flush=True)
            t = timeouts.get(alg, 60.0)
            result = _run_algorithm(alg, puzzle, kb, timeout_sec=t)
            results.append(result)
            status = "✓" if result.solved else ("⏱" if "Timeout" in result.message else "✗")
            print(f"{status} ({result.time_ms:.1f} ms)")

        _print_comparison_table(results)

        # Write output from first successful solver
        for result in results:
            if result.solved and result.solution:
                formatted = format_solution(puzzle, result.solution)
                print(formatted)
                write_output(formatted, output_path)
                print(f"\nOutput written to: {output_path}")
                break
    else:
        result = _run_algorithm(args.algorithm, puzzle, kb, timeout_sec=120.0)

        if result.solved and result.solution:
            formatted = format_solution(puzzle, result.solution)
            print(f"\nSolution ({result.algorithm}, {result.time_ms:.2f} ms):")
            print(formatted)
            write_output(formatted, output_path)
            print(f"\nOutput written to: {output_path}")
        else:
            print(f"\n{result.algorithm}: No solution found. {result.message}")
            sys.exit(1)


if __name__ == "__main__":
    main()
