# Instruction Format

## Version

v0.1

## Overview

Each instruction is 8 bits wide.

## Instruction Layout

```
+------------+------------+
| Opcode     | Operand    |
| 4 bits     | 4 bits     |
+------------+------------+
```

## Bit Layout

| Bits | Field | Description |
|------|-------|-------------|
| 7-4 | Opcode | Instruction code |
| 3-0 | Operand | Register, Address, or Immediate value |

## Examples

| Binary | Meaning |
|--------|---------|
| 0001 0011 | LOAD 3 |
| 0100 0001 | ADD 1 |
| 1011 0101 | JMP 5 |
| 1111 0000 | HALT |

## Operand Types

- Register
- Memory Address
- Immediate Value

## Features

- Simple instruction decoding
- Fixed 8-bit instruction width
- Easy to implement
