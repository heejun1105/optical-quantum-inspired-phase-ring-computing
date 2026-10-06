"""Generate or verify Paper VIII Listing 2's example sinusoidal LUT files."""

import argparse
from pathlib import Path

from phase_ring import ROOT, SUPPORTED_MODULI, sinusoidal_lut, verify_mem, write_mem


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify without rewriting files")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "lut")
    args = parser.parse_args()
    for n_mod in SUPPORTED_MODULI:
        path = args.output_dir / f"lut_{n_mod}.mem"
        if not args.check:
            write_mem(path, sinusoidal_lut(n_mod))
        verify_mem(path, n_mod)
        print(f"PASS: {path.name}: {n_mod} signed Q15 reference words")


if __name__ == "__main__":
    main()
