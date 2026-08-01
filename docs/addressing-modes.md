# Addressing Modes

## Version

v0.1

## Overview

Addressing modes define how the CPU accesses operands during instruction execution.

## Supported Addressing Modes

### 1. Immediate Addressing

The operand is part of the instruction.

Example:

LOAD #5

Description:

Load the value 5 into the accumulator.

---

### 2. Register Addressing

The operand is stored in a register.

Example:

MOV R1

Description:

Move data from register R1.

---

### 3. Direct Addressing

The operand is located at a memory address.

Example:

LOAD 0x20

Description:

Load data from memory address 0x20.

---

### 4. Indirect Addressing

The register contains the memory address.

Example:

LOAD [R1]

Description:

Load data from the memory address stored in R1.

---

## Addressing Mode Summary

| Mode | Description |
|------|-------------|
| Immediate | Operand is inside the instruction |
| Register | Operand is stored in a register |
| Direct | Operand is stored at a memory address |
| Indirect | Register points to a memory address |

## Future Modes

- Indexed Addressing
- Relative Addressing
- Stack Addressing
