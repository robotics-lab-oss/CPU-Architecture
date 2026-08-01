# Boot Process

## Version

v0.1

## Overview

The boot process describes how the CPU starts execution after reset.

## Reset Sequence

1. Reset signal is activated.
2. All registers are initialized.
3. Program Counter (PC) is set to 0x00.
4. Stack Pointer (SP) is initialized.
5. FLAGS register is cleared.
6. Control Unit enters Fetch state.

## Boot Flow

Reset

↓

Initialize Registers

↓

PC = 0x00

↓

Fetch First Instruction

↓

Decode Instruction

↓

Execute Instruction

↓

Continue Program Execution

## Initial Register Values

| Register | Value |
|----------|-------|
| ACC | 0x00 |
| R0 | 0x00 |
| R1 | 0x00 |
| R2 | 0x00 |
| R3 | 0x00 |
| PC | 0x00 |
| SP | 0x8F |
| FLAGS | 0x00 |

## First Instruction

The CPU begins execution from memory address 0x00.

## Boot Goals

- Reliable startup
- Predictable initialization
- Simple execution flow
