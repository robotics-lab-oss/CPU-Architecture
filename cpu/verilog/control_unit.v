module control_unit (

    input wire clk,
    input wire reset,

    input wire [7:0] instruction,

    output reg mem_read,
    output reg mem_write,

    output reg reg_write,

    output reg alu_enable,

    output reg pc_increment,
    output reg pc_load,

    output reg ir_load,

    output reg flags_load

);

wire [3:0] opcode;

assign opcode = instruction[7:4];

always @(*) begin

    mem_read     = 0;
    mem_write    = 0;
    reg_write    = 0;
    alu_enable   = 0;
    pc_increment = 0;
    pc_load      = 0;
    ir_load      = 0;
    flags_load   = 0;

    case(opcode)

        4'b0000: begin // NOP
            pc_increment = 1;
        end

        4'b0001: begin // LOAD
            mem_read = 1;
            reg_write = 1;
            pc_increment = 1;
        end

        4'b0010: begin // STORE
            mem_write = 1;
            pc_increment = 1;
        end

        4'b0011: begin // MOV
            reg_write = 1;
            pc_increment = 1;
        end

        4'b0100: begin // ADD
            alu_enable = 1;
            reg_write = 1;
            flags_load = 1;
            pc_increment = 1;
        end

        4'b0101: begin // SUB
            alu_enable = 1;
            reg_write = 1;
            flags_load = 1;
            pc_increment = 1;
        end

        4'b0110: begin // AND
            alu_enable = 1;
            reg_write = 1;
            flags_load = 1;
            pc_increment = 1;
        end

        4'b0111: begin // OR
            alu_enable = 1;
            reg_write = 1;
            flags_load = 1;
            pc_increment = 1;
        end

        4'b1000: begin // XOR
            alu_enable = 1;
            reg_write = 1;
            flags_load = 1;
            pc_increment = 1;
        end

        4'b1001: begin // NOT
            alu_enable = 1;
            reg_write = 1;
            flags_load = 1;
            pc_increment = 1;
        end

        4'b1010: begin // CMP
            alu_enable = 1;
            flags_load = 1;
            pc_increment = 1;
        end

        4'b1011: begin // JMP
            pc_load = 1;
        end

        4'b1100: begin // JZ
            pc_load = 1;
        end

        4'b1101: begin // JNZ
            pc_load = 1;
        end

        4'b1110: begin // IN
            reg_write = 1;
            pc_increment = 1;
        end

        4'b1111: begin // HALT
        end

    endcase

end

endmodule
