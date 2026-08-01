module register_file (

    input wire clk,
    input wire reset,

    input wire write_enable,

    input wire [2:0] read_addr1,
    input wire [2:0] read_addr2,
    input wire [2:0] write_addr,

    input wire [7:0] write_data,

    output wire [7:0] read_data1,
    output wire [7:0] read_data2

);

    // 8 Registers × 8-bit
    reg [7:0] registers [7:0];

    integer i;

    // Reset and Write
    always @(posedge clk or posedge reset) begin

        if (reset) begin

            for(i = 0; i < 8; i = i + 1)
                registers[i] <= 8'b00000000;

        end

        else if (write_enable) begin

            registers[write_addr] <= write_data;

        end

    end

    // Read Ports
    assign read_data1 = registers[read_addr1];
    assign read_data2 = registers[read_addr2];

endmodule
