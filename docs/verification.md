# Verification record

Executed locally on **2026-10-06 (Asia/Seoul)** using Windows, Python **3.12.2**, NumPy **2.5.3**, pytest **9.1.1**, and Icarus Verilog **12.0 (devel)** from the Windows package `12.2022.06.11`. These are software simulation results, not chip measurements.

## Completed checks

- `python -m pip install -r requirements.txt`: succeeded in an isolated virtual environment.
- `python python/generate_lut.py`: generated both reference tables; `--check` verified all 1024 and 2048 words without rewriting them.
- `python python/verify_phase_ring.py`: both requested examples produced indices **126** and **252**, with signed example LUT value **22883**. The masked-arithmetic verifier checked **1,048,576** and **4,194,304** input pairs against integer modulo, plus scalar carry-boundary checks.
- `pytest -q`: **40 passed**, including all four simulator-dependent cases; **no skipped tests**.
- Standalone `tb_pim_phase_adder`: **2,054 paired cycles**, covering every LUT address, input truncation, registered timing, asynchronous reset/hold/recovery and signed-Q15 bit patterns.
- Standalone `tb_phase_adders`: **5,242,880 exhaustive RTL arithmetic input pairs** passed against the test-only integer modulo oracle.
- Default `compare_rtl_reference.py`: **6,184** 10-bit vectors and **8,232** 11-bit vectors matched Python phase indices and signed Q15 lookup values. Vectors include every address, wraparound boundaries, oversized/negative inputs and seeded random samples.
- `python python/compare_rtl_reference.py --exhaustive`: all **1,048,576** 10-bit and **4,194,304** 11-bit input pairs passed through the actual clocked RTL PIM cells; every emitted phase index and signed Q15 LUT word matched Python (**5,242,880 total**).
- Both README Python examples ran, including tests from an unrelated working directory.
- `CITATION.cff` validated against **CFF 1.2.0** using `cffconvert`; its full title, DOI, author, version and date were checked against Zenodo metadata.
- All three supplied DOI links resolved with HTTP 200. The supplied main PDF's MD5 matched Zenodo's deposited file checksum.
- The full source-file inventory and local Markdown links were checked; no missing local link targets were found.

The two comparison modes use separate `sampled/` and `exhaustive/` output directories to keep their vector/result files distinct.

## What these checks establish

The described RTL and Python agree on fixed-width addition, word representation and the example LUT cell's simulated timing/reset contract. They do not reproduce the paper's synthesis/energy estimates or independently validate PLP contraction, a full ISP, image-quality claims, arbitrary real-valued multiplication, fabricated PIM hardware or photonic devices.

## Repeat the verification

Run the commands in the root [README](../README.md). Icarus must be on `PATH` for RTL tests; otherwise pytest explicitly skips four simulator-dependent cases. GitHub Actions installs Icarus and runs the reference checks automatically. CI status should be assessed from the actual workflow run, not inferred from this local record.
