module alu (
    input  [7:0] A,
    input  [7:0] B,
    input  [3:0] OP,

    output reg [7:0] RESULT,
    output reg ZERO,
    output reg CARRY
);

always @(*) begin

    CARRY = 0;

    case(OP)

        4'b0000: RESULT = A;                 // NOP

        4'b0001: {CARRY, RESULT} = A + B;    // ADD

        4'b0010: {CARRY, RESULT} = A - B;    // SUB

        4'b0011: RESULT = A & B;             // AND

        4'b0100: RESULT = A | B;             // OR

        4'b0101: RESULT = A ^ B;             // XOR

        4'b0110: RESULT = ~A;                // NOT

        4'b0111: begin                       // CMP
            RESULT = A - B;
            CARRY = (A < B);
        end

        default: RESULT = 8'b00000000;

    endcase

    if (RESULT == 8'b00000000)
        ZERO = 1'b1;
    else
        ZERO = 1'b0;

end

endmodule
