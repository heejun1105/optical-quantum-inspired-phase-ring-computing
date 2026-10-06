# Phase-Ring PLP PIM

[![Reference verification](https://github.com/heejun1105/phase-ring-plp-pim/actions/workflows/verify.yml/badge.svg?branch=main)](https://github.com/heejun1105/phase-ring-plp-pim/actions/workflows/verify.yml?query=branch%3Amain)
[License: Apache-2.0](LICENSE)

In simple terms, the proposed architecture represents values as phase indices, adds those indices with a small modular adder, and reads the SRAM value at the resulting address. The proposed Point-Line-Plane (PLP) layer filters and contracts higher-dimensional states before the final lookup. This repository provides an executable reference for the phase arithmetic and LUT cell, with documentation of the broader proposal.

## Implementation status

**Implemented and verified in simulation:**

- `Z_1024` / `Z_2048` fixed-width modular phase arithmetic and Verilog RTL phase adders.
- SRAM LUT reference cells and signed Q15 sinusoidal example tables.
- Python reference model and Python-to-RTL phase-index/LUT-output comparison.
- Automated tests, including exhaustive arithmetic verification and clock/reset checks.

**Proposed / documented only; not implemented or independently validated:**

- Complete value-to-phase encoding for arbitrary workloads and arbitrary real-valued multiplication.
- Full PLP hardware and its state-contraction assumptions.
- Complete neural-network MAC/accumulation architecture.
- Fabricated PIM chips and photonic integrated-circuit implementations.
- Fabricated-chip energy/performance measurements and the paper's system-level performance claims.

The implementation source of truth is **Kim Chul, Paper VIII, Version 2.0 (2026)**: [Dual-Layer Topological Neuromorphic and Signal Processing Architecture](https://doi.org/10.5281/zenodo.22782241). See [source provenance](docs/source_provenance.md) for section/listing references and the Zenodo reference PDF identity. Paper IX and Paper X are theoretical background, not implementation specifications.

## What changes in the proposed data path?

```text
Conventional conceptual path:
input x weight -> multiplier / MAC -> result

Proposed architectural path:
input / weight -> phase encoding -> modular phase addition
               -> proposed PLP filtering / state contraction
               -> SRAM address -> domain-specific LUT output

Implemented reference cell:
already encoded phase indices -> fixed-width addition
                             -> SRAM LUT index -> registered 16-bit LUT word
```

The architecture trades conventional multiplier complexity for phase encoding, integer addition, quantization and memory lookup. The complex unit-phase identity `exp(i*theta_x) * exp(i*theta_w) = exp(i*(theta_x + theta_w))` supports addition of phase angles; it does not by itself reconstruct arbitrary real-valued multiplication or a complete MAC. Encoding, amplitude handling, accumulation and the application-specific LUT must be designed for the workload. No general-purpose encoder or PLP RTL is provided here.

## Reference implementation details

- **Implemented:** `Z_1024` and `Z_2048` arithmetic, 10/11-bit overflow/truncation, signed Q15 sinusoidal example LUTs, SRAM-array lookup and one-clock registered outputs with asynchronous active-low output reset.
- **Paper-based:** the 10-bit PIM cell preserves Section VII.A Listing 1's ports, 10-bit `local_phase_sum`, 1024 x 16-bit `sram_matrix` and output register behavior; Python follows Listing 2.
- **Repository additions:** simulation LUT initialization, an 11-bit PIM-cell adaptation, arithmetic-only modules, validation, testbenches, Python/RTL comparison, CI and an illustrative pixel LUT demo.
- **Documented proposals:** the PLP decision layer and prospective photonic extensions. These are not implemented or independently validated by the arithmetic tests.

## Quick start

Use Python 3.10 or newer. The commands below run from the repository root. A virtual environment is recommended.

```sh
git clone https://github.com/heejun1105/phase-ring-plp-pim.git
cd phase-ring-plp-pim
python -m venv .venv
```

Activate it using `source .venv/bin/activate` on Linux/macOS, or `.\.venv\Scripts\Activate.ps1` in Windows PowerShell. Then:

```sh
python -m pip install -r requirements.txt
python python/verify_phase_ring.py
python python/generate_lut.py --check
pytest
python examples/basic_phase_addition.py
python examples/image_lut_example.py
```

Expected arithmetic examples:

```text
N=1024: 750 + 400 -> 126; signed Q15 LUT=22883
N=2048: 1500 + 800 -> 252; signed Q15 LUT=22883
```

`verify_phase_ring.py` checks masked arithmetic against independent integer modulo for all **1,048,576** 10-bit pairs and **4,194,304** 11-bit pairs, with scalar API checks at carry boundaries. It also verifies every committed LUT word against the reference generator. Python phase operands may be signed or oversized integers; the model truncates them to the unsigned port width. Floating-point inputs and unsupported moduli are rejected.

`pytest` includes RTL integration when `iverilog` and `vvp` are on `PATH`; otherwise the four simulator-dependent tests are explicitly reported as skipped. A Python-only pass therefore does not establish RTL verification.

## Verilog compilation and simulation

Install [Icarus Verilog](https://steveicarus.github.io/iverilog/usage/installation.html) and ensure both `iverilog` and `vvp` are on `PATH`. For example, on Debian/Ubuntu use `sudo apt-get install iverilog`; on Windows, `winget install --id Icarus.Verilog --exact --source winget`, then open a new terminal or add the installation's `bin` directory to `PATH`.

The cross-language runner compiles both cells and compares actual phase indices and registered signed Q15 outputs with Python. Its default vectors cover every address, boundary/wraparound cases, input-port truncation and 4,096 seeded random pairs per ring:

```sh
python python/compare_rtl_reference.py
```

For standalone self-checking simulation:

```sh
python -c "from pathlib import Path; Path('build').mkdir(exist_ok=True)"
iverilog -g2012 -Wall -s tb_pim_phase_adder -o build/tb_pim.vvp rtl/pim_phase_adder_cell.v rtl/pim_phase_adder_cell_2048.v rtl/phase_adder_1024.v rtl/phase_adder_2048.v testbench/tb_pim_phase_adder.v
vvp build/tb_pim.vvp
iverilog -g2012 -Wall -s tb_phase_adders -o build/tb_adders.vvp rtl/phase_adder_1024.v rtl/phase_adder_2048.v testbench/tb_phase_adders.v
vvp build/tb_adders.vvp
```

The second testbench exhaustively checks **5,242,880** arithmetic input pairs. To compare all pairs through both clocked PIM cells as well:

```sh
python python/compare_rtl_reference.py --exhaustive
```

This optional run writes large text vector/result files under ignored `build/`. Run standalone `vvp` from the repository root so relative LUT paths resolve. The Python runner selects that working directory automatically. See [testbench notes](testbench/README.md) and the [verification record](docs/verification.md).

## Arithmetic and example LUT format

For `N = 2^W`, the low `W` bits of `theta_x + theta_w` equal `(theta_x + theta_w) mod N`. The RTL expresses this as a fixed-width assignment with the carry discarded; there is no divider, comparator or conditional subtraction in the adders.

- `750 + 400 = 1150`; the low 10 bits are `126`.
- `1500 + 800 = 2300`; the low 11 bits are `252`.
- `1023 + 1 -> 0`, and `2047 + 1 -> 0`.

The reference LUT is `trunc(sin(2*pi*k/N) * 32767)`, matching Listing 2's NumPy `int16` conversion (truncation toward zero). Each `.mem` line contains one four-digit hexadecimal two's-complement word. Python returns signed values; RTL exposes the same bits on an unsigned 16-bit data port. This sinusoidal LUT is an example/reference, not every application's final LUT. The 1024-entry table is **2 KiB**; the repository's 2048-entry adaptation is **4 KiB**. Regenerate with `python python/generate_lut.py` and verify with `--check`.

The paper's original SRAM array has no initialization or programming interface. This repository adds simulation-only `$readmemh`, explicitly marked as an addition. Defining `SYNTHESIS` excludes it; a physical implementation needs a target SRAM macro, a loading/programming mechanism, and timing closure. The behavioral array does not establish fabricated PIM hardware. See [arithmetic](docs/arithmetic.md) and [architecture](docs/architecture.md).

## Point-Line-Plane decision mechanics

Paper VIII, Sections III-IV, proposes PLP as a **state-space contraction mechanism** for the state/address explosion associated with higher-dimensional LUT mappings:

- **Plane:** account for phase-field variation and noise through surface-action/entropy terms.
- **Line:** filter non-resonant or invalid trajectories through the proposed prime-orbit conditions.
- **Point:** localize/contract the remaining state toward a deterministic SRAM address.

The intended role goes beyond an ordinary standalone filter: select a task-relevant address before memory access. The repository does not establish the mathematical/physical assumptions, general lossless dimensionality reduction, or the paper's convergence claims. [PLP overview](docs/plp_overview.md) explains this boundary.

## Illustrative image lookup

The reference PDF associated with Paper VIII's Zenodo record includes a Paper IX appendix (Appendix D), which describes `RGB / pixel data -> 10-bit Z_1024 phase state -> phase processing -> SRAM LUT`, mentioning tone mapping, gamma correction and color-space transformation. This is background context, not a Paper VIII code specification.

`examples/image_lut_example.py` demonstrates the address/LUT pattern using an explicitly repository-chosen linear 8-bit-to-10-bit encoding, zero phase offset, and a gamma-2.2 lookup. It does not implement PLP denoising, tone mapping or multi-channel color-space conversion. It produces no PSNR/SSIM, image-quality, throughput or energy benchmark. A production color-space mapping needs application-specific multi-channel encoding and storage; a single per-channel gamma table is not sufficient.

## Prospective photonic roadmap

**PROPOSED / PROSPECTIVE / FUTURE IMPLEMENTATION CONCEPTS:** Paper VIII, Section V.C, discusses Plane-stage monitoring intended to reduce detector loss/heating; phase-margin handling for scattering/thermal drift; Line-stage cancellation of optical crosstalk; phase-selective routing intended to reduce active switching; and passive optical phase operations intended to reduce CMOS capacitive charging. These five concepts are documented in [photonic roadmap](docs/photonic_roadmap.md). No fabricated photonic chip, device model or experimental validation is provided. Ordinary wave superposition does not by itself establish a working modular phase-adder device.

## Energy claims and verification level

Paper VIII reports approximately **0.015 pJ/op as estimated local phase-adder switching energy** (Sections II.B, V.B and VI). This is an attributed paper estimate, not a measured full-system/accelerator result and not a result produced by this repository. SRAM/LUT reads and global interconnect can be major contributors to system-level energy, as the paper itself discusses. Arithmetic simulation alone cannot reproduce synthesis area, power, process-corner or fabricated-chip measurements.

## Limitations

- Domain-specific architecture; not a general-purpose CPU replacement.
- Phase quantization error and finite phase resolution; the ring spacing is `360/N` degrees.
- Aliasing and dynamic range depend on the phase encoding and amplitude representation.
- Phase encoding overhead and workload-dependent LUT design remain necessary.
- LUT scaling can grow exponentially with independent input dimensions; selecting one address does not automatically preserve an arbitrary multi-input function.
- SRAM access cost and memory/interconnect bottlenecks can dominate total cost.
- PLP state-contraction assumptions require independent validation and a concrete discrete implementation.
- Photonic implementation remains prospective.
- No complete encoder, MAC accumulator, programmable physical SRAM macro, PLP hardware, image benchmark, chip synthesis or measured energy is included.

## Repository layout

```text
phase-ring-plp-pim/
  README.md, LICENSE, CITATION.cff, requirements.txt, pytest.ini
  rtl/          10/11-bit adders and PIM LUT cells
  testbench/    self-checking timing/reset, exhaustive adders, comparison harness
  python/       arithmetic model, LUT tools, verifier, RTL comparison
  lut/          1024/2048-entry hexadecimal sinusoidal reference tables
  examples/     basic phase addition and illustrative image LUT
  docs/         architecture, arithmetic, PLP, photonics, provenance, verification
  tests/        arithmetic/LUT/example/RTL and comparator failure tests
  .github/      automatic Python and Icarus verification workflow
```

## Citation, license and contact

Please cite Paper VIII; bibliographic metadata is provided in [CITATION.cff](CITATION.cff).

New code authored for this repository is licensed under the **[Apache License 2.0](LICENSE)**. The referenced research papers remain subject to their own publication licenses; Paper VIII's [Zenodo record](https://zenodo.org/records/22782241) lists **CC BY 4.0** for the deposited paper. The repository code license does not replace or modify the papers' licenses. Attribution to paper-based listings is retained in the source and documentation; no code copyright-holder identity is assigned to the paper author.

For questions regarding the theory presented in the paper, please contact the author at [voodoo6000@daum.net](mailto:voodoo6000@daum.net). The paper author and repository maintainer are separate roles; no identity between them is assumed.

## References

- **Main implementation source:** Kim, Chul (2026). *Information-Causality Field and the Unified Field Theory Based on 11-Dimensional T^3 Torus Fractal Geometry -- Paper VIII: Dual-Layer Topological Neuromorphic and Signal Processing Architecture: Z_N Phase-Ring Hardware Isomorphism and Integrated Point-Line-Plane (PLP) Decision Mechanics*. Version 2.0. [DOI: 10.5281/zenodo.22782241](https://doi.org/10.5281/zenodo.22782241).
- **Related theoretical background only:** [Paper IX, DOI: 10.5281/zenodo.22726125](https://doi.org/10.5281/zenodo.22726125).
- **Related theoretical background only:** [Paper X, DOI: 10.5281/zenodo.23004844](https://doi.org/10.5281/zenodo.23004844).
