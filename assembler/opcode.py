# opcode.py

OPCODES = {

    # 1 Byte Instructions
    "NOP":   0x00,
    "OUT":   0xA0,
    "IN":    0xB0,
    "INC":   0xC0,
    "DEC":   0xD0,
    "HALT":  0xF0,

    # 2 Byte Instructions
    "LOAD":  0x10,
    "STORE": 0x20,
    "ADD":   0x30,
    "SUB":   0x40,
    "AND":   0x50,
    "OR":    0x60,
    "XOR":   0x70,
    "JMP":   0x80,
    "JZ":    0x90,
    "CMP":   0xE0,

}
