`timescale 1ns/1ps
// Repository arithmetic-only module implementing Paper VIII Eq. (2)-(3).
module phase_adder_1024 (
    input wire [9:0] in_phase_x,
    input wire [9:0] in_phase_w,
    output wire [9:0] phase_sum
);
    assign phase_sum = in_phase_x + in_phase_w;
endmodule
