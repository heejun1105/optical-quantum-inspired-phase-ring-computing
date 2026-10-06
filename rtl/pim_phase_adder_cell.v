`timescale 1ns/1ps
// Adapted from Paper VIII, Section VII.A, Listing 1.
// Repository addition: simulation-only LUT_FILE/$readmemh initialization.
// SYNTHESIS removes initialization; an ASIC must supply its SRAM macro/loading.
module pim_phase_adder_cell #(
    parameter LUT_FILE = "lut/lut_1024.mem"
) (
    input wire clk,
    input wire rst_n,
    input wire [9:0] in_phase_x,
    input wire [9:0] in_phase_w,
    output reg [15:0] sram_data_out
);
    wire [9:0] local_phase_sum;
    assign local_phase_sum = in_phase_x + in_phase_w;
    reg [15:0] sram_matrix [0:1023];

`ifndef SYNTHESIS
    initial begin
        $readmemh(LUT_FILE, sram_matrix);
    end
`endif

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            sram_data_out <= 16'h0000;
        else
            sram_data_out <= sram_matrix[local_phase_sum];
    end
endmodule
