# Arithmetic and fixed-width representation

Paper VIII Section II, Eq. (2), defines `theta_out = (theta_x + theta_w) mod N`. The complex unit-phase identity relates multiplication of `exp(i*theta)` values to angle addition. Integer phase indices represent quantized angles `2*pi*k/N`; they are not arbitrary input magnitudes.

## Carry truncation

For `N=1024`, retain ten bits. For `N=2048`, retain eleven. Since `N=2^W`, selecting the low `W` bits implements modulo `N`:

```text
10-bit: 750 + 400 = 1150 = 10001111110 (binary)
         retain 0001111110 -> 126
11-bit: 1500 + 800 = 2300 = 100011111100 (binary)
         retain 00011111100 -> 252
```

The RTL uses `assign phase_sum = in_phase_x + in_phase_w;` with the output width fixed. Arithmetic is unsigned bit-vector arithmetic. The paper calls this natural two's-complement overflow; retaining low bits is the same modulo operation for signed or unsigned representations, while the SRAM address itself is unsigned. No explicit divider, comparator or conditional subtractor is required for these power-of-two rings. This logic should not be generalized to `Z_360` by substituting `359` as a bit mask.

Python's arbitrary-width integers do not overflow automatically. `phase_add` first masks both operands and then the sum. Any signed or oversized integer is interpreted through its low input-port bits. For example `phase_add(-1, 2, 1024) == 1`. This normalization defines the repository API; no signed application-value encoding is implied.

## Q15 example LUT

Section VII.B Listing 2 generates `np.int16(np.sin(np.linspace(0, 2*np.pi, N, endpoint=False)) * 32767)`. The repository retains that expression's semantics: sampling excludes the repeated endpoint, conversion truncates toward zero, and the scale is **32767**, not 32768. Peaks are `+32767` and `-32767`; the table does not contain `-32768`. Quantization is an example convention from the supplied listing, not an application accuracy claim.

Files store each signed value as its 16-bit two's-complement hexadecimal word: `32767 -> 7fff`, `-32767 -> 8001`, `-1 -> ffff`. The RTL bus is unsigned; interpret it as signed int16 to compare with Python. There are exactly `N` words, one per address. The strict loader rejects malformed words and incorrect lengths; `--check` also detects altered values.

NumPy's floating-point transcendental evaluation supplies the example samples. The integer masks and committed hexadecimal words are exact. Regeneration is checked word-for-word against those files; the repository makes no cross-platform theorem about every floating-point library implementation near a truncation boundary.

## Timing

The arithmetic-only modules are combinational. The PIM cell computes the address combinationally and samples the table word on the rising edge; its output updates after the nonblocking assignment. Asserting `rst_n=0` clears the output asynchronously without clearing SRAM. There is no extra phase-sum register. The Python cycle model returns the newly sampled output from `clock()` and exposes `reset()`; it is not an event-driven analog simulator.

## Verification

Tests cover the requested `126` and `252` examples; carry boundaries; all ring pairs against `% N`; input truncation; signed LUT round-trips; all stored words; corrupted files; output reset; clock sampling; and actual RTL output compared with Python. The use of `%` in verification is an independent oracle; it is not part of the implemented RTL adder.
