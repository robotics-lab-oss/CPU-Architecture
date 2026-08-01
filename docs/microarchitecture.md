# Microarchitecture

## Version

v0.1

## Overview

The microarchitecture defines the internal organization of the 8-bit CPU.

## Main Components

- Control Unit (CU)
- Arithmetic Logic Unit (ALU)
- Register File
- Program Counter (PC)
- Instruction Register (IR)
- Memory Address Register (MAR)
- Memory Data Register (MDR)
- Stack Pointer (SP)
- Flags Register
- Instruction Decoder
- System Bus
- Memory Interface

## Block Diagram

                  +------------------+
                  |   Control Unit   |
                  +--------+---------+
                           |
                           |
                 +---------v---------+
                 | Instruction       |
                 | Decoder           |
                 +---------+---------+
                           |
        +------------------+------------------+
        |                                     |
        v                                     v
+---------------+                     +---------------+
| Register File |-------------------->|      ALU      |
+---------------+                     +-------+-------+
        ^                                     |
        |                                     |
        +------------------+------------------+
                           |
                    +------+------+
                    |    FLAGS    |
                    +-------------+

        +-------------+
        |      PC     |
        +------+------+
               |
               v
        +-------------+
        |     MAR     |
        +------+------+
               |
               v
        +-------------+
        |   Memory    |
        +------+------+
               |
               v
        +-------------+
        |     MDR     |
        +------+------+
               |
               v
        +-------------+
        |      IR     |
        +-------------+

## Execution Flow

1. Fetch instruction
2. Decode instruction
3. Read operands
4. Execute operation
5. Update registers
6. Update flags
7. Move to next instruction

## Bus Structure

- 8-bit Data Bus
- 8-bit Address Bus
- Control Bus

## Clock

Single clock source

## Design Goals

- Simple
- Easy to understand
- Modular
- Expandable
