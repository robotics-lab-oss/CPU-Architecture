`timescale 1ns / 1ps

module cpu_tb;

    reg clk;
    reg reset;

    // Instantiate CPU
    cpu DUT (
        .clk(clk),
        .reset(reset)
    );

    // Clock Generation (100 MHz)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test Sequence
    initial begin

        // Reset CPU
        reset = 1;

        #20;

        reset = 0;

        // Load Program into Memory
        DUT.MEM.mem[8'h00] = 8'b00010001; // LOAD
        DUT.MEM.mem[8'h01] = 8'b01000001; // ADD
        DUT.MEM.mem[8'h02] = 8'b11110000; // HALT

        // Run Simulation
        #200;

        $display("--------------------------------");
        $display("CPU Simulation Finished");
        $display("PC = %h", DUT.PC.pc);
        $display("IR = %h", DUT.IR.instruction_out);
        $display("ACC/R0 = %h", DUT.RF.registers[0]);
        $display("--------------------------------");

        $finish;

    end

endmodule
