# Verilog verification infrastructure

All testbench code is a repository addition. Run from the repository root because the standalone PIM tests load `lut/lut_1024.mem` and `lut/lut_2048.mem` relative to the process working directory. The Python comparison runner sets that directory itself.

- `tb_pim_phase_adder.v`: 10/11-bit cells, requested examples, unsigned port truncation, every LUT address, unchanged outputs before a rising edge, signed word bits, asynchronous output reset between edges, reset hold and post-reset lookup. Its expected data arrays read the same files; independent generator/word verification and Python comparison are also needed.
- `tb_phase_adders.v`: all 1,048,576 plus 4,194,304 legal arithmetic input pairs, with integer `% N` as a test-only independent oracle.
- `tb_reference_compare.v`: streams actual internal PIM indices and registered words. `compare_rtl_reference.py` verifies them against independently computed modulo and regenerated reference samples, and rejects missing, extra, malformed or unknown-word output rows.

Use the copyable compilation commands in the root [README](../README.md). `$fatal(1, ...)` produces nonzero simulation exit status on a mismatch. No simulator means the four dependent pytest cases are skipped with a reason, not silently passed. The explicit comparison command fails if Icarus is unavailable.

## Memory initialization and synthesis

The original Listing 1 has no SRAM initialization. This repository adds simulation-only `$readmemh` to avoid unknown data. It is excluded under `SYNTHESIS`; it is not a hardware SRAM programming interface. Reset clears the output only. The signed Q15 table is stored as unsigned hexadecimal bus words; for example the negative peak is `8001`.

## Large optional run

`python python/compare_rtl_reference.py --exhaustive` runs all pairs through clocked LUT reads and compares both the index and word. Its vectors/results are written under ignored `build/reference_compare/exhaustive/`; default comparison uses a separate `sampled/` directory. This takes more time and storage than default address coverage plus seeded random samples. It does not measure hardware throughput.
