`timescale 1ns/1ps
// Repository arithmetic-only module implementing Paper VIII Eq. (2), (4).
module phase_adder_2048 (
    input wire [10:0] in_phase_x,
    input wire [10:0] in_phase_w,
    output wire [10:0] phase_sum
);
    assign phase_sum = in_phase_x + in_phase_w;
endmodule
