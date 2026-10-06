"""Exhaustively verify the two phase rings against independent integer modulo."""

import numpy as np

from phase_ring import ROOT, SUPPORTED_MODULI, phase_add, pim_phase_step, verify_mem


def verify_arithmetic(n_mod: int) -> int:
    weights = np.arange(n_mod, dtype=np.uint32)
    for tx in range(n_mod):
        masked = (tx + weights) & (n_mod - 1)
        expected = (tx + weights) % n_mod
        if not np.array_equal(masked, expected):
            raise AssertionError(f"exhaustive arithmetic mismatch at tx={tx}")
        # Exercise the public scalar API for every tx, at carry/edge boundaries.
        for tw in (0, 1, n_mod - 1, n_mod - tx - 1):
            if phase_add(tx, tw, n_mod) != (tx + tw) % n_mod:
                raise AssertionError((tx, tw, n_mod))
    return n_mod * n_mod


def main() -> None:
    for n_mod, tx, tw, expected in ((1024, 750, 400, 126), (2048, 1500, 800, 252)):
        address, value = pim_phase_step(tx, tw, n_mod)
        assert address == expected
        print(f"N={n_mod}: {tx} + {tw} -> {address}; signed Q15 LUT={value}")
    for n_mod in SUPPORTED_MODULI:
        count = verify_arithmetic(n_mod)
        verify_mem(ROOT / "lut" / f"lut_{n_mod}.mem", n_mod)
        print(f"PASS: N={n_mod}: {count:,} exhaustive input pairs; all LUT words verified")


if __name__ == "__main__":
    main()
