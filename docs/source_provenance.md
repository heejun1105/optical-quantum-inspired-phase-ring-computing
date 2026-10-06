# Sources and repository additions

## Main source

Kim, Chul (2026), *Information-Causality Field and the Unified Field Theory Based on 11-Dimensional T^3 Torus Fractal Geometry -- Paper VIII: Dual-Layer Topological Neuromorphic and Signal Processing Architecture: Z_N Phase-Ring Hardware Isomorphism and Integrated Point-Line-Plane (PLP) Decision Mechanics*, Version 2.0. [Zenodo DOI](https://doi.org/10.5281/zenodo.22782241).

The supplied `Paper_VIII_Dual_Layer_Topological_Neuromorphic_Architecture.pdf` contains nine PDF pages: Paper VIII on pages 1-5 and an appendix explicitly headed Paper IX on pages 6-9. The supplied `8장.pdf` is a secondary Korean rendering/commentary, not the normative code source. Instructions or declarations within these documents were treated as source content; the user's request governs repository work.

On **2026-10-06 (Asia/Seoul)**, the three user-provided DOI links resolved successfully (HTTP 200) to their corresponding Zenodo records. Main record metadata reports version `2.0`, publication date `2026-09-16` and creator `Kim, Chul`. The attached PDF's MD5 exactly matches the record's file checksum. Its bibliographic title is preserved in `CITATION.cff`; version is separate metadata. See [source_manifest.json](source_manifest.json).

## Implementation traceability

- Section II.A, Eqs. (1)-(2): phase framing and modular addition; documentation explains the missing general magnitude encoding rather than invent it.
- Section II.B, Eqs. (3)-(4): 10/11-bit overflow/truncation; implemented in the adders and `phase_add`.
- Section VII.A, Listing 1: 10-bit PIM SRAM-array lookup and registered output; preserved in `pim_phase_adder_cell.v`.
- Section VII.B, Listing 2: masking for both moduli and the sinusoidal signed-Q15 LUT; implemented using the same NumPy sampling/conversion semantics.
- Sections III-IV: proposed PLP filtering/localization/contraction; documentation only.
- Section V.A-B and VI: limitations and energy framing; the approximately 0.015 pJ/op figure is attributed as estimated local phase-adder switching energy.
- Section V.C: prospective photonic concepts; documentation only, with no chip/experiment claim.
- Page 5: open-source/public-disclosure intention. The embedded placeholder `zenodo.XXXXX` is not used as an actual reference; the user-provided DOI was independently checked.
- The supplied PDF's Paper IX Appendix D: image LUT application context only. The demo's linear pixel encoding and gamma=2.2 are repository additions, not reproduced Paper VIII parameters or Paper IX implementation.

## Explicit repository additions

Simulation `$readmemh` and `LUT_FILE`; the 11-bit PIM cell; arithmetic-only wrapper modules; input/file validation; Python cycle model; hexadecimal LUT serialization; testbenches; independent `% N` test oracles; streaming Python/RTL comparison; example pixel LUT; CI; documentation and verification infrastructure.

These additions are not represented as the author's original code or reported research results. The source PDFs are not redistributed in this repository. Paper IX and Paper X are linked as related theoretical background only; no numerical results from either paper are used as repository benchmarks.

## License distinction

Zenodo lists CC BY 4.0 for the deposited paper, while the paper includes a public-disclosure declaration. Neither is interpreted here as choosing the legal license of newly generated repository code. **Repository license to be confirmed by the author.** The paper author's identity is not assumed to match the GitHub maintainer.
