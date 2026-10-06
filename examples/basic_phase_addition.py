"""Run from any directory; no installed Python package is needed."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
from phase_ring import phase_add, pim_phase_step

for tx, tw, n_mod, expected in ((750, 400, 1024, 126), (1500, 800, 2048, 252)):
    address, q15 = pim_phase_step(tx, tw, n_mod)
    assert address == expected
    print(f"({tx} + {tw}) mod {n_mod} = {address}; example sine LUT = {q15}")
for n_mod in (1024, 2048):
    assert phase_add(n_mod - 1, 1, n_mod) == 0
    print(f"{n_mod - 1} + 1 -> 0 by fixed-width carry truncation")
