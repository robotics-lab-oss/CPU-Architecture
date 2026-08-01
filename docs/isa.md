# Instruction Set Architecture (ISA)

## Version

v0.1

## CPU Overview

- Data Width: 8-bit
- Address Width: 8-bit
- Memory Size: 256 Bytes
- Instruction Width: 8-bit
- Opcode Width: 4-bit
- Operand Width: 4-bit

## Registers

- ACC
- R0
- R1
- R2
- R3
- PC
- IR
- SP
- FLAGS

## Instruction Categories

### Data Transfer

- LOAD
- STORE
- MOV

### Arithmetic

- ADD
- SUB

### Logic

- AND
- OR
- XOR
- NOT

### Compare

- CMP

### Branch

- JMP
- JZ
- JNZ

### Input / Output

- IN

### System

- HALT

## Flags

| Flag | Description |
|------|-------------|
| Z | Zero |
| C | Carry |
| N | Negative |
| O | Overflow |

## Addressing Modes

- Immediate
- Register
- Direct
- Indirect

## Execution Model

Fetch

↓

Decode

↓

Execute

↓

Write Back

↓

Next Instruction

## Design Goals

- Simple
- Educational
- Modular
- Open Source
- Easy to implement
