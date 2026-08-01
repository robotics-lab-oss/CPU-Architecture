module memory (

    input wire clk,

    input wire read_enable,
    input wire write_enable,

    input wire [7:0] address,
    input wire [7:0] write_data,

    output reg [7:0] read_data

);

    // 256 x 8-bit Memory
    reg [7:0] mem [0:255];

    integer i;

    // Initialize Memory
    initial begin
        for(i = 0; i < 256; i = i + 1)
            mem[i] = 8'h00;
    end

    // Read Operation
    always @(*) begin
        if(read_enable)
            read_data = mem[address];
        else
            read_data = 8'h00;
    end

    // Write Operation
    always @(posedge clk) begin
        if(write_enable)
            mem[address] <= write_data;
    end

endmodule
