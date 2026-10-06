`timescale 1ns/1ps
// Repository self-checking infrastructure; not a paper listing.
module tb_pim_phase_adder;
    reg clk = 0;
    reg rst_n = 1;
    reg [9:0] x10 = 0, w10 = 0;
    reg [10:0] x11 = 0, w11 = 0;
    wire [15:0] out10, out11;
    wire [9:0] sum10;
    wire [10:0] sum11;
    reg [15:0] expected10 [0:1023];
    reg [15:0] expected11 [0:2047];
    integer i, cases = 0;

    always #5 clk = ~clk;
    pim_phase_adder_cell dut10(clk, rst_n, x10, w10, out10);
    pim_phase_adder_cell_2048 dut11(clk, rst_n, x11, w11, out11);
    phase_adder_1024 adder10(x10, w10, sum10);
    phase_adder_2048 adder11(x11, w11, sum11);

    task check_pair;
        input integer a10, b10, a11, b11;
        integer address10, address11;
        reg [15:0] held10, held11;
        begin
            @(negedge clk);
            held10 = out10;
            held11 = out11;
            x10 = a10; w10 = b10; x11 = a11; w11 = b11;
            address10 = ((a10 & 1023) + (b10 & 1023)) % 1024;
            address11 = ((a11 & 2047) + (b11 & 2047)) % 2048;
            #1;
            if (sum10 !== address10 || sum11 !== address11)
                $fatal(1, "arithmetic mismatch in case %0d", cases);
            if (dut10.local_phase_sum !== sum10 || dut11.local_phase_sum !== sum11)
                $fatal(1, "PIM index mismatch");
            if (out10 !== held10 || out11 !== held11)
                $fatal(1, "output changed before sampling clock");
            @(posedge clk); #1;
            if (out10 !== expected10[address10] || out11 !== expected11[address11])
                $fatal(1, "registered LUT mismatch in case %0d", cases);
            cases = cases + 1;
        end
    endtask

    initial begin
        $readmemh("lut/lut_1024.mem", expected10);
        $readmemh("lut/lut_2048.mem", expected11);
        #1; rst_n = 0; #1;
        if (out10 !== 0 || out11 !== 0) $fatal(1, "initial async reset failed");
        #1; rst_n = 1;
        check_pair(750, 400, 1500, 800);
        if (sum10 !== 126 || sum11 !== 252) $fatal(1, "paper examples failed");
        check_pair(1023, 1, 2047, 1);
        check_pair(1023, 1023, 2047, 2047);
        check_pair(-1, 2, -1, 2);
        check_pair(65537, 1025, 65537, 2049);
        // Full address coverage, with carry and positive/negative Q15 values.
        for (i = 0; i < 2048; i = i + 1)
            check_pair(i, 400, i, 800);
        // Reset assertion between clock edges; ROM/LUT contents remain intact.
        @(negedge clk); #2; rst_n = 0; #1;
        if (out10 !== 0 || out11 !== 0) $fatal(1, "mid-run async reset failed");
        @(posedge clk); #1;
        if (out10 !== 0 || out11 !== 0) $fatal(1, "reset hold failed");
        rst_n = 1;
        check_pair(768, 0, 1536, 0);
        if (out10 !== 16'h8001 || out11 !== 16'h8001) $fatal(1, "signed Q15 bits failed");
        $display("PASS: PIM cells: %0d paired cycles, complete address coverage, reset/timing", cases);
        $finish;
    end
endmodule
