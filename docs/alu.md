# Arithmetic Logic Unit (ALU)

## Version

v0.1

## Overview

The Arithmetic Logic Unit (ALU) performs arithmetic and logical operations on 8-bit data.

## Input

- Operand A (8-bit)
- Operand B (8-bit)

## Output

- Result (8-bit)
- Status Flags

## Supported Operations

| Operation | Description |
|-----------|-------------|
| ADD | Addition |
| SUB | Subtraction |
| AND | Bitwise AND |
| OR | Bitwise OR |
| XOR | Bitwise XOR |
| NOT | Bitwise NOT |
| CMP | Compare |

## Status Flags

| Flag | Description |
|------|-------------|
| Z | Zero Flag |
| C | Carry Flag |
| N | Negative Flag |
| O | Overflow Flag |

## ALU Block Diagram

```
        Operand A
            │
            ▼
      +-------------+
      |             |
      |     ALU     |──────► Result
      |             |
      +-------------+
            ▲
            │
        Operand B

           │
           ▼
      Status Flags
```

## Features

- 8-bit data processing
- Arithmetic operations
- Logical operations
- Status flag generation
- Simple combinational design

## Future Improvements

- Shift Left (SHL)
- Shift Right (SHR)
- Rotate Left (ROL)
- Rotate Right (ROR)
- Multiply (MUL)
- Divide (DIV)
