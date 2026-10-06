from pathlib import Path

import numpy as np
import pytest

from phase_ring import (
    ROOT, PhaseAdderCell, from_word, phase_add, phase_width,
    pim_phase_step, read_mem, sinusoidal_lut, to_word, verify_mem, write_mem,
)
from verify_phase_ring import verify_arithmetic


@pytest.mark.parametrize("n_mod,tx,tw,expected", [
    (1024, 750, 400, 126), (2048, 1500, 800, 252),
    (1024, 1023, 1, 0), (2048, 2047, 1, 0),
    (1024, 1023, 1023, 1022), (2048, 2047, 2047, 2046),
])
def test_examples_and_carry(n_mod, tx, tw, expected):
    assert phase_add(tx, tw, n_mod) == expected


@pytest.mark.parametrize("n_mod", [1024, 2048])
def test_full_ring_and_scalar_boundaries(n_mod):
    assert verify_arithmetic(n_mod) == n_mod**2
    assert phase_width(n_mod) in (10, 11)


@pytest.mark.parametrize("n_mod", [1024, 2048])
def test_port_truncation_and_group_properties(n_mod):
    for tx in (-2**100, -n_mod - 1, -1, 0, 1, n_mod, 2**100 + 7):
        for tw in (-n_mod, -1, 0, 400, 2**80):
            assert phase_add(tx, tw, n_mod) == (tx + tw) % n_mod
            assert phase_add(tx, tw, n_mod) == phase_add(tw, tx, n_mod)
        assert phase_add(tx, -tx, n_mod) == 0
        assert phase_add(phase_add(tx, 400, n_mod), 750, n_mod) == phase_add(tx, 1150, n_mod)
    assert phase_add(np.uint16(n_mod - 1), np.uint16(1), n_mod) == 0
    assert phase_add(2**100 + 1, 1, np.uint16(n_mod)) == 2


@pytest.mark.parametrize("n_mod", [0, -1, 360, 1000, 4096])
def test_unsupported_modulus(n_mod):
    with pytest.raises(ValueError):
        phase_add(1, 2, n_mod)


@pytest.mark.parametrize("args", [(1.5, 2, 1024), (1, '2', 1024), (True, 2, 1024), (1, 2, 1024.0)])
def test_invalid_types(args):
    with pytest.raises(TypeError):
        phase_add(*args)


@pytest.mark.parametrize("n_mod", [1024, 2048])
def test_lut_matches_paper_listing_and_committed_words(n_mod):
    # Literal expression from Listing 2 is the independent LUT oracle.
    expected = np.int16(np.sin(np.linspace(0, 2*np.pi, n_mod, endpoint=False)) * 32767)
    lut = sinusoidal_lut(n_mod)
    assert tuple(int(v) for v in expected) == lut
    assert (lut[0], lut[n_mod//4], lut[n_mod//2], lut[3*n_mod//4]) == (0, 32767, 0, -32767)
    verify_mem(ROOT / "lut" / f"lut_{n_mod}.mem", n_mod)
    for address in range(n_mod):
        assert from_word(to_word(lut[address])) == lut[address]
    assert pim_phase_step(n_mod - 1, 1, n_mod) == (0, 0)


@pytest.mark.parametrize("n_mod", [1024, 2048])
def test_mem_roundtrip_and_corruption(tmp_path, n_mod):
    path = tmp_path / "nested" / "lut.mem"
    lut = sinusoidal_lut(n_mod)
    write_mem(path, lut)
    assert read_mem(path, n_mod) == lut
    lines = path.read_text().splitlines()
    lines[7] = "ffff"
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(AssertionError):
        verify_mem(path, n_mod)
    lines[7] = "xxxx"
    path.write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError):
        read_mem(path, n_mod)
    path.write_text("0000\n")
    with pytest.raises(ValueError):
        read_mem(path, n_mod)


@pytest.mark.parametrize("n_mod", [1024, 2048])
def test_registered_cell_and_reset(n_mod):
    cell = PhaseAdderCell(n_mod)
    assert cell.output_word == 0
    assert cell.clock(3*n_mod//4, 0) == 0x8001
    cell.reset()
    assert cell.output_word == 0
    assert cell.clock(0, 0, rst_n=False) == 0
    assert cell.clock(n_mod//4, 0) == 0x7fff
    with pytest.raises(ValueError):
        PhaseAdderCell(n_mod, (0,))


@pytest.mark.parametrize("value", [-32769, 32768])
def test_signed_word_range(value):
    with pytest.raises(ValueError):
        to_word(value)


@pytest.mark.parametrize("word", [-1, 65536])
def test_unsigned_word_range(word):
    with pytest.raises(ValueError):
        from_word(word)
