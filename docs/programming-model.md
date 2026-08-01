# Programming Model

## Version

v0.1

## Overview

The programming model defines the resources visible to assembly programmers.

## CPU Registers

| Register | Size | Access |
|----------|------|--------|
| ACC | 8-bit | Read / Write |
| R0 | 8-bit | Read / Write |
| R1 | 8-bit | Read / Write |
| R2 | 8-bit | Read / Write |
| R3 | 8-bit | Read / Write |
| PC | 8-bit | Internal |
| SP | 8-bit | Read / Write |
| FLAGS | 8-bit | Read |

## Flags

| Flag | Meaning |
|------|---------|
| Z | Zero |
| C | Carry |
| N | Negative |
| O | Overflow |

## Memory

- Address Width: 8-bit
- Address Space: 256 Bytes

## Stack

- Stack grows downward.
- Stack Pointer (SP) points to the top of the stack.

## Instruction Length

- Fixed 8-bit instruction

## Reset State

ACC = 0x00

R0-R3 = 0x00

PC = 0x00

SP = 0x8F

FLAGS = 0x00

## Execution

Fetch

↓

Decode

↓

Execute

↓

Write Back

↓

Next Instruction
