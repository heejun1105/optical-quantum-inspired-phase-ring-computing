`timescale 1ns/1ps
// Stream actual RTL indices and LUT words for independent Python comparison.
module tb_reference_compare;
    parameter N_MOD = 1024;
    localparam WIDTH = (N_MOD == 1024) ? 10 : 11;
    reg clk = 0, rst_n = 1;
    reg [WIDTH-1:0] x = 0, w = 0;
    wire [WIDTH-1:0] phase_sum;
    wire [WIDTH-1:0] pim_index;
    wire [15:0] data;
    integer fi, fo, status, tx, tw, count = 0;
    reg [4095:0] vector_path, output_path;
    always #5 clk = ~clk;

    generate
        if (N_MOD == 1024) begin : ring10
            phase_adder_1024 adder(x, w, phase_sum);
            pim_phase_adder_cell cell10(clk, rst_n, x, w, data);
            assign pim_index = cell10.local_phase_sum;
        end else if (N_MOD == 2048) begin : ring11
            phase_adder_2048 adder(x, w, phase_sum);
            pim_phase_adder_cell_2048 cell11(clk, rst_n, x, w, data);
            assign pim_index = cell11.local_phase_sum;
        end else begin : invalid
            initial $fatal(1, "unsupported N_MOD");
        end
    endgenerate

    initial begin
        if (!$value$plusargs("VECTORS=%s", vector_path)) $fatal(1, "missing VECTORS");
        if (!$value$plusargs("OUTPUT=%s", output_path)) $fatal(1, "missing OUTPUT");
        fi = $fopen(vector_path, "r"); fo = $fopen(output_path, "w");
        if (!fi || !fo) $fatal(1, "cannot open vector/result file");
        #1; rst_n = 0; #1;
        if (data !== 0) $fatal(1, "reset mismatch");
        #1; rst_n = 1;
        status = $fscanf(fi, "%d %d\n", tx, tw);
        while (status == 2) begin
            @(negedge clk); x = tx; w = tw;
            @(posedge clk); #1;
            if (pim_index !== phase_sum) $fatal(1, "cell/adder index mismatch");
            $fdisplay(fo, "%0d %0d %04h", count, pim_index, data);
            count = count + 1;
            status = $fscanf(fi, "%d %d\n", tx, tw);
        end
        if (!$feof(fi)) $fatal(1, "malformed vector input");
        $fclose(fi); $fclose(fo);
        if (count == 0) $fatal(1, "empty vector input");
        $display("PASS: streamed %0d RTL vectors for N=%0d", count, N_MOD);
        $finish;
    end
endmodule
