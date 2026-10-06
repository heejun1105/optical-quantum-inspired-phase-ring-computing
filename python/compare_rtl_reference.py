"""Compile Icarus RTL and compare actual indices/registered words with Python."""

import argparse
from itertools import zip_longest
from pathlib import Path
import random
import shutil
import subprocess

from phase_ring import ROOT, SUPPORTED_MODULI, from_word, phase_add, sinusoidal_lut, verify_mem


def vectors(n_mod: int, exhaustive: bool = False, samples: int = 4096):
    if exhaustive:
        for tx in range(n_mod):
            for tw in range(n_mod):
                yield tx, tw
        return
    yield (750, 400) if n_mod == 1024 else (1500, 800)
    edges = (0, 1, n_mod // 4, n_mod // 2, n_mod - 2, n_mod - 1)
    for tx in edges:
        for tw in edges:
            yield tx, tw
    # Both passes visit every output address; the second exercises rollover.
    for tx in range(n_mod):
        yield tx, 0
        yield tx, n_mod - 1
    # Assignment into unsigned RTL ports discards higher bits.
    yield -1, 2
    yield 65537, n_mod + 1
    yield -n_mod - 1, 3 * n_mod + 2
    rng = random.Random(8 + n_mod)
    for _ in range(samples):
        yield rng.randrange(n_mod), rng.randrange(n_mod)


def compare_results(vector_file: Path, result_file: Path, n_mod: int) -> int:
    lut = sinusoidal_lut(n_mod)
    count = 0
    with vector_file.open(encoding="ascii") as inputs, result_file.open(encoding="ascii") as outputs:
        for row, (vector, result) in enumerate(zip_longest(inputs, outputs)):
            if vector is None or result is None:
                raise AssertionError("missing or extra RTL result rows")
            tx, tw = map(int, vector.split())
            fields = result.split()
            if len(fields) != 3:
                raise AssertionError(f"malformed RTL row {row}: {result.strip()}")
            try:
                number, actual_index = map(int, fields[:2])
                actual_value = from_word(int(fields[2], 16))
            except ValueError as exc:
                raise AssertionError(f"invalid/unknown RTL word at row {row}") from exc
            # Independent modulo oracle, including signed/oversized input cases.
            expected_index = (tx + tw) % n_mod
            if phase_add(tx, tw, n_mod) != expected_index:
                raise AssertionError(f"Python arithmetic mismatch at row {row}")
            if number != row or actual_index != expected_index or actual_value != lut[expected_index]:
                raise AssertionError(
                    f"N={n_mod} row={row} inputs=({tx},{tw}): "
                    f"RTL=({actual_index},{actual_value}), "
                    f"reference=({expected_index},{lut[expected_index]})"
                )
            count += 1
    if count == 0:
        raise AssertionError("no RTL vectors were checked")
    return count


def run_checked(command: list[str], timeout: int = 180) -> None:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    if result.returncode or "ERROR:" in result.stdout or "WARNING:" in result.stdout:
        raise RuntimeError(f"command failed: {command}\n{result.stdout}\n{result.stderr}")
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())


def run_comparison(n_mod: int, build_dir: Path, exhaustive: bool = False, samples: int = 4096) -> int:
    compiler, simulator = shutil.which("iverilog"), shutil.which("vvp")
    if not compiler or not simulator:
        raise RuntimeError("Install Icarus Verilog and put both iverilog and vvp on PATH")
    verify_mem(ROOT / "lut" / f"lut_{n_mod}.mem", n_mod)
    build_dir = build_dir.resolve()
    build_dir.mkdir(parents=True, exist_ok=True)
    vector_file = build_dir / f"vectors_{n_mod}.txt"
    result_file = build_dir / f"results_{n_mod}.txt"
    executable = build_dir / f"compare_{n_mod}.vvp"
    with vector_file.open("w", encoding="ascii", newline="\n") as output:
        for tx, tw in vectors(n_mod, exhaustive, samples):
            output.write(f"{tx} {tw}\n")
    run_checked([
        compiler, "-g2012", "-Wall", "-s", "tb_reference_compare",
        "-P", f"tb_reference_compare.N_MOD={n_mod}", "-o", str(executable),
        "rtl/phase_adder_1024.v", "rtl/phase_adder_2048.v",
        "rtl/pim_phase_adder_cell.v", "rtl/pim_phase_adder_cell_2048.v",
        "testbench/tb_reference_compare.v",
    ])
    run_checked([simulator, str(executable), f"+VECTORS={vector_file.as_posix()}", f"+OUTPUT={result_file.as_posix()}"])
    count = compare_results(vector_file, result_file, n_mod)
    print(f"PASS: N={n_mod}: {count:,} RTL/Python indices and signed Q15 words agree")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exhaustive", action="store_true", help="all pairs, including clocked LUT reads; creates large build files")
    parser.add_argument("--samples", type=int, default=4096, help="seeded random pairs per ring, in addition to coverage vectors")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build" / "reference_compare")
    args = parser.parse_args()
    if args.samples < 0:
        parser.error("--samples must be nonnegative")
    mode_dir = args.build_dir / ("exhaustive" if args.exhaustive else "sampled")
    for n_mod in SUPPORTED_MODULI:
        run_comparison(n_mod, mode_dir, args.exhaustive, args.samples)


if __name__ == "__main__":
    main()
