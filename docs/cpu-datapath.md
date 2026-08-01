# CPU Datapath

## Version

v0.1

## Overview

The CPU datapath defines how data moves between registers, memory, the ALU, and the Control Unit during instruction execution.

## Main Components

- Program Counter (PC)
- Memory Address Register (MAR)
- Memory Data Register (MDR)
- Instruction Register (IR)
- Accumulator (ACC)
- General Purpose Registers (R0-R3)
- Arithmetic Logic Unit (ALU)
- Flags Register
- Control Unit
- Memory

## Datapath Diagram

                +----------------------+
                |     Control Unit     |
                +----------+-----------+
                           |
                           |
+---------+      +---------v---------+
|   PC    |----->|        MAR        |
+---------+      +---------+---------+
                           |
                           v
                     +-----------+
                     |  Memory   |
                     +-----+-----+
                           |
                           v
                     +-----------+
                     |    MDR    |
                     +-----+-----+
                           |
                           v
                     +-----------+
                     |    IR     |
                     +-----+-----+
                           |
                           v
                   +---------------+
                   | Instruction   |
                   |    Decoder    |
                   +-------+-------+
                           |
        +------------------+------------------+
        |                                     |
        v                                     v
+---------------+                     +---------------+
| Registers     |-------------------->|      ALU      |
| ACC,R0,R1,R2  |<--------------------|               |
| R3            |                     +-------+-------+
+---------------+                             |
                                               v
                                         +-----------+
                                         |  FLAGS    |
                                         +-----------+

## Data Flow

1. PC sends address to MAR.
2. MAR accesses Memory.
3. Memory sends instruction to MDR.
4. MDR loads instruction into IR.
5. Control Unit decodes the instruction.
6. Registers provide operands.
7. ALU executes the operation.
8. Result is written back to registers.
9. FLAGS register is updated.
10. PC moves to the next instruction.

## Bus System

- 8-bit Data Bus
- 8-bit Address Bus
- Control Bus

## Features

- Simple architecture
- Easy to understand
- Modular design
- Expandable for future versions
