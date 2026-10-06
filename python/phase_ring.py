"""Paper VIII, Section VII Listing 2: integer phase addition and example Q15 LUT.

Validation, file I/O and the cycle model are repository additions. No PLP or
numerical-value-to-phase encoder is implemented here.
"""

from dataclasses import dataclass
from operator import index
from pathlib import Path

import numpy as np

SUPPORTED_MODULI = (1024, 2048)
ROOT = Path(__file__).resolve().parents[1]


def _integer(value: int, name: str) -> int:
    if isinstance(value, (bool, np.bool_)):
        raise TypeError(f"{name} must be an integer, not a boolean")
    try:
        return index(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be an integer") from exc


def phase_width(n_mod: int) -> int:
    """Restrict this reference to the two moduli in Paper VIII's Listing 2."""
    n_mod = _integer(n_mod, "n_mod")
    if n_mod not in SUPPORTED_MODULI:
        raise ValueError("n_mod must be 1024 (10 bits) or 2048 (11 bits)")
    return n_mod.bit_length() - 1


def phase_add(theta_x: int, theta_w: int, n_mod: int = 1024) -> int:
    """Add low-width bit patterns, discarding carry; no division is used.

    Negative or oversized integers are reduced to the low 10/11 input bits,
    matching assignment to unsigned Verilog ports. Float inputs are rejected.
    """
    mask = (1 << phase_width(n_mod)) - 1
    tx = _integer(theta_x, "theta_x") & mask
    tw = _integer(theta_w, "theta_w") & mask
    return (tx + tw) & mask


def sinusoidal_lut(n_mod: int = 1024) -> tuple[int, ...]:
    """Listing 2's example LUT: trunc(sin(2*pi*k/N)*32767), signed int16.

    NumPy linspace/sin and conversion match the supplied example. This is a
    reference signal LUT, not a general multiplication or production ISP LUT.
    """
    phase_width(n_mod)
    phases = np.linspace(0, 2 * np.pi, n_mod, endpoint=False)
    return tuple(int(v) for v in (np.sin(phases) * 32767).astype(np.int16))


def to_word(value: int) -> int:
    value = _integer(value, "value")
    if not -32768 <= value <= 32767:
        raise ValueError("value is outside signed 16-bit range")
    return value & 0xFFFF


def from_word(word: int) -> int:
    word = _integer(word, "word")
    if not 0 <= word <= 0xFFFF:
        raise ValueError("word is outside unsigned 16-bit range")
    return word if word < 0x8000 else word - 0x10000


def write_mem(path: Path, values: tuple[int, ...]) -> None:
    """Write one 16-bit two's-complement hexadecimal word per line."""
    words = [f"{to_word(v):04x}\n" for v in values]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(words), encoding="ascii")


def read_mem(path: Path, n_mod: int) -> tuple[int, ...]:
    """Read repository .mem format strictly, detecting missing/invalid words."""
    phase_width(n_mod)
    lines = Path(path).read_text(encoding="ascii").splitlines()
    if len(lines) != n_mod:
        raise ValueError(f"{path}: expected {n_mod} words, got {len(lines)}")
    values = []
    for row, line in enumerate(lines, 1):
        if len(line) != 4 or any(c not in "0123456789abcdefABCDEF" for c in line):
            raise ValueError(f"{path}:{row}: expected exactly four hexadecimal digits")
        values.append(from_word(int(line, 16)))
    return tuple(values)


def verify_mem(path: Path, n_mod: int) -> None:
    actual, expected = read_mem(path, n_mod), sinusoidal_lut(n_mod)
    for address, (got, want) in enumerate(zip(actual, expected)):
        if got != want:
            raise AssertionError(f"{path}: address {address}: {got} != {want}")


def pim_phase_step(tx: int, tw: int, n_mod: int = 1024) -> tuple[int, int]:
    """Compatible result with Listing 2: (phase index, signed Q15 value)."""
    address = phase_add(tx, tw, n_mod)
    return address, sinusoidal_lut(n_mod)[address]


@dataclass
class PhaseAdderCell:
    """Repository cycle model for Listing 1 (and the 11-bit adaptation).

    A clock samples the current combinational address and returns the newly
    registered SRAM word. reset() represents asynchronous active-low reset.
    Reset clears the output register, not the stored LUT.
    """

    n_mod: int = 1024
    lut: tuple[int, ...] | None = None
    output_word: int = 0

    def __post_init__(self) -> None:
        phase_width(self.n_mod)
        self.lut = sinusoidal_lut(self.n_mod) if self.lut is None else tuple(self.lut)
        if len(self.lut) != self.n_mod:
            raise ValueError("LUT length must equal n_mod")
        for value in self.lut:
            to_word(value)
        self.reset()

    def reset(self) -> None:
        self.output_word = 0

    def clock(self, tx: int, tw: int, rst_n: bool = True) -> int:
        if not rst_n:
            self.reset()
        else:
            address = phase_add(tx, tw, self.n_mod)
            self.output_word = to_word(self.lut[address])
        return self.output_word
