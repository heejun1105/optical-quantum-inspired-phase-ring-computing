`timescale 1ns/1ps
// Repository 11-bit adaptation of Listing 1, guided by Eq. (4)/Listing 2.
// This module is not an RTL listing supplied in the paper.
// Its 2048 x 16-bit example LUT occupies 4 KiB (not the 10-bit cell's 2 KiB).
module pim_phase_adder_cell_2048 #(
    parameter LUT_FILE = "lut/lut_2048.mem"
) (
    input wire clk,
    input wire rst_n,
    input wire [10:0] in_phase_x,
    input wire [10:0] in_phase_w,
    output reg [15:0] sram_data_out
);
    wire [10:0] local_phase_sum;
    assign local_phase_sum = in_phase_x + in_phase_w;
    reg [15:0] sram_matrix [0:2047];

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
