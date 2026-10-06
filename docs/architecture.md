# Dual-layer architecture and implementation boundary

Paper VIII Sections I-IV describe a lower `Z_N` arithmetic layer and an upper PLP decision layer co-executing on a proposed PIM substrate. The lower layer works on already encoded phase states; the upper layer is intended to select/contract a task-relevant state before final memory access.

## Executable reference

`rtl/pim_phase_adder_cell.v` follows Section VII.A Listing 1: two 10-bit inputs, a ten-bit natural-overflow sum, `reg [15:0] sram_matrix [0:1023]`, and a registered SRAM lookup with asynchronous active-low output reset. The original external ports are preserved. Testbenches observe the internal address hierarchically rather than add a new public phase-output port.

The paper leaves SRAM uninitialized. The repository's `LUT_FILE` parameter and simulation-only `$readmemh` make simulation reproducible; they are explicitly additional infrastructure. Missing files or unknown outputs fail the repository's verification. With `SYNTHESIS` defined, initialization is excluded. The adder/register/array description remains a synthesizable behavioral reference, but an actual ASIC requires an SRAM macro and initialization/loading design. FPGA memory inference is tool/target dependent and has not been verified here.

`pim_phase_adder_cell_2048.v` is a repository adaptation using Eq. (4) and Listing 2's `N=2048` arithmetic. It is not quoted from the paper's RTL listing. Its LUT is 2048 x 16 bits, or 4 KiB. The arithmetic-only modules expose combinational phase sums for separate checking.

## Application contract

Inputs must already be valid phase encodings for the chosen application. The sine table simply maps an index to a signed signal sample. The unit-phase identity does not specify a universal encoding of real magnitudes, preservation of dynamic range, a conventional MAC accumulator, or application output semantics. Those require a workload-specific design.

The single-address LUT cell does not implement the PLP surface integrals, entropy processing, prime trajectory masks or Banach contraction. A ten-bit adder alone is not an implementation of high-dimensional PLP contraction. Those concepts remain described at the proposal level in [plp_overview.md](plp_overview.md).

## Evidence boundaries

Simulation establishes fixed-width index behavior, file-backed LUT reads and output timing/reset for these RTL descriptions. It does not establish transistor layout, SRAM compiler results, synthesis area/power, physical PIM integration, image quality, or a complete accelerator. The approximately 0.015 pJ/op figure is the paper's **estimated local phase-adder switching energy**; system-level SRAM/interconnect energy needs separate analysis.
