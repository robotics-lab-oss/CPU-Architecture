module program_counter (

    input wire clk,
    input wire reset,

    input wire load,
    input wire increment,

    input wire [7:0] next_pc,

    output reg [7:0] pc

);

always @(posedge clk or posedge reset) begin

    if (reset)
        pc <= 8'h00;

    else if (load)
        pc <= next_pc;

    else if (increment)
        pc <= pc + 8'h01;

end

endmodule
