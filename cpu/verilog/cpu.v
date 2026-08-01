module cpu (

    input wire clk,
    input wire reset

);

    // Program Counter
    wire [7:0] pc;

    // Memory
    wire [7:0] instruction;

    // Control Signals
    wire mem_read;
    wire mem_write;
    wire reg_write;
    wire alu_enable;
    wire pc_increment;
    wire pc_load;
    wire ir_load;
    wire flags_load;

    // Register File
    wire [7:0] reg_a;
    wire [7:0] reg_b;
    wire [7:0] alu_result;

    // Flags
    wire zero;
    wire carry;
    wire negative;
    wire overflow;

    //------------------------------------
    // Program Counter
    //------------------------------------

    program_counter PC (

        .clk(clk),
        .reset(reset),
        .load(pc_load),
        .increment(pc_increment),
        .next_pc(8'h00),
        .pc(pc)

    );

    //------------------------------------
    // Memory
    //------------------------------------

    memory MEM (

        .clk(clk),

        .read_enable(mem_read),
        .write_enable(mem_write),

        .address(pc),
        .write_data(reg_a),

        .read_data(instruction)

    );

    //------------------------------------
    // Instruction Register
    //------------------------------------

    wire [7:0] ir;

    instruction_register IR (

        .clk(clk),
        .reset(reset),
        .load(ir_load),

        .instruction_in(instruction),
        .instruction_out(ir)

    );

    //------------------------------------
    // Control Unit
    //------------------------------------

    control_unit CU (

        .clk(clk),
        .reset(reset),

        .instruction(ir),

        .mem_read(mem_read),
        .mem_write(mem_write),

        .reg_write(reg_write),

        .alu_enable(alu_enable),

        .pc_increment(pc_increment),
        .pc_load(pc_load),

        .ir_load(ir_load),

        .flags_load(flags_load)

    );

    //------------------------------------
    // Register File
    //------------------------------------

    register_file RF (

        .clk(clk),
        .reset(reset),

        .write_enable(reg_write),

        .read_addr1(3'b000),
        .read_addr2(3'b001),
        .write_addr(3'b000),

        .write_data(alu_result),

        .read_data1(reg_a),
        .read_data2(reg_b)

    );

    //------------------------------------
    // ALU
    //------------------------------------

    alu ALU (

        .A(reg_a),
        .B(reg_b),

        .OP(ir[7:4]),

        .RESULT(alu_result),

        .ZERO(zero),
        .CARRY(carry)

    );

    //------------------------------------
    // Flags Register
    //------------------------------------

    flags_register FLAGS (

        .clk(clk),
        .reset(reset),

        .load(flags_load),

        .zero_in(zero),
        .carry_in(carry),
        .negative_in(1'b0),
        .overflow_in(1'b0),

        .zero(),
        .carry(),
        .negative(),
        .overflow()

    );

endmodule
