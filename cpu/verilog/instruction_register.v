module instruction_register (

    input  wire       clk,
    input  wire       reset,
    input  wire       load,

    input  wire [7:0] instruction_in,

    output reg  [7:0] instruction_out

);

always @(posedge clk or posedge reset) begin

    if (reset)
        instruction_out <= 8'h00;

    else if (load)
        instruction_out <= instruction_in;

end

endmodule
