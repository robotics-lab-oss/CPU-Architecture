module flags_register (

    input  wire clk,
    input  wire reset,
    input  wire load,

    input  wire zero_in,
    input  wire carry_in,
    input  wire negative_in,
    input  wire overflow_in,

    output reg zero,
    output reg carry,
    output reg negative,
    output reg overflow

);

always @(posedge clk or posedge reset) begin

    if (reset) begin
        zero     <= 1'b0;
        carry    <= 1'b0;
        negative <= 1'b0;
        overflow <= 1'b0;
    end

    else if (load) begin
        zero     <= zero_in;
        carry    <= carry_in;
        negative <= negative_in;
        overflow <= overflow_in;
    end

end

endmodule
