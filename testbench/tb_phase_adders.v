`timescale 1ns/1ps
// Exhaustive repository test of both arithmetic-only RTL modules.
module tb_phase_adders;
    reg [9:0] x10, w10;
    reg [10:0] x11, w11;
    wire [9:0] sum10;
    wire [10:0] sum11;
    integer x, w, count = 0;
    phase_adder_1024 dut10(x10, w10, sum10);
    phase_adder_2048 dut11(x11, w11, sum11);
    initial begin
        for (x = 0; x < 1024; x = x + 1)
            for (w = 0; w < 1024; w = w + 1) begin
                x10 = x; w10 = w; #1;
                if (sum10 !== ((x + w) % 1024)) $fatal(1, "N=1024 x=%0d w=%0d", x, w);
                count = count + 1;
            end
        for (x = 0; x < 2048; x = x + 1)
            for (w = 0; w < 2048; w = w + 1) begin
                x11 = x; w11 = w; #1;
                if (sum11 !== ((x + w) % 2048)) $fatal(1, "N=2048 x=%0d w=%0d", x, w);
                count = count + 1;
            end
        $display("PASS: %0d exhaustive RTL arithmetic pairs", count);
        $finish;
    end
endmodule
