# Prospective photonic extension

**Status: PROPOSED / PROSPECTIVE / FUTURE IMPLEMENTATION CONCEPTS.** These concepts summarize Paper VIII Section V.C (including Eqs. (7)-(11)). None is a fabricated-chip result, a device implementation, or a finding of this repository's simulation.

## 1. Detector loss and heating reduction

The paper proposes a Plane-stage power/flux formulation for non-destructive monitoring, intended to reduce reliance on absorbing photodetector taps and their insertion-loss/heating costs. The repository supplies no optical sensor design or experimental demonstration of non-destructive power measurement. A physical monitoring mechanism, calibration and its disturbance must be established independently.

## 2. Scattering and thermal-drift robustness

The proposed Plane-stage variation/entropy treatment is intended to absorb small phase jitter and thermal drift before they cause address-decoding errors. Phase margins, operating ranges and stability under realistic optical disturbances need a concrete device/decoder model and validation. No tested drift tolerance is reported here.

## 3. Optical crosstalk suppression

The paper links Line-stage phase-locking/orthogonality conditions with time-averaged destructive interference of non-resonant leakage. This is a proposed passive cancellation mechanism. It does not establish a general physical cancellation guarantee; waveguide geometry, coherence, coupling, finite observation time and imperfect phase control need independent analysis.

## 4. Lower-switching-power optical routing

Phase-selective routing is proposed to direct optical power to a target channel/neuron, with cluster activation also discussed, instead of relying on an active switch at every junction. No router layout, insertion loss, routing correctness or switching-power measurement is supplied. Those engineering properties remain to be determined.

## 5. Reduction of the CMOS capacitive charging bottleneck

The paper proposes optical phase operations through passive wave superposition as an alternative to transistor charging/discharging for `theta_x + theta_w`. Ordinary superposition adds optical fields; its phase does not automatically equal the sum of their phases. A physical device mechanism for the intended phase operation, discretization, modulo wraparound and electronic/optical readout must therefore be specified and independently verified. No optical speed or energy figure is measured or reproduced here.

## Research progression

A future implementation would need device-level models, finite-resolution phase encoding/decoding, loss/drift/crosstalk measurements and system-level integration with memory and interconnect. These are engineering validation needs, not extra features claimed by Paper VIII or tasks completed by the current reference implementation. The CMOS RTL tests establish no evidence about optical feasibility.
