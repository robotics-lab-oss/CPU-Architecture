# Control Unit

## Version

v0.1

## Overview

The Control Unit (CU) manages the execution of instructions by controlling the CPU components.

## Responsibilities

- Fetch instructions
- Decode instructions
- Execute instructions
- Control data flow
- Update Program Counter
- Generate control signals

## Instruction Cycle

### 1. Fetch

1. PC → MAR
2. Memory → MDR
3. MDR → IR
4. PC = PC + 1

### 2. Decode

- Read opcode from IR
- Determine instruction type
- Generate control signals

### 3. Execute

- Perform ALU operation
- Read or write memory
- Update registers
- Update FLAGS

## Control Signals

| Signal | Description |
|--------|-------------|
| MEM_READ | Read from memory |
| MEM_WRITE | Write to memory |
| REG_READ | Read register |
| REG_WRITE | Write register |
| ALU_ENABLE | Enable ALU |
| PC_INC | Increment Program Counter |
| PC_LOAD | Load Program Counter |
| IR_LOAD | Load Instruction Register |
| FLAGS_WRITE | Update status flags |

## State Machine

1. Fetch
2. Decode
3. Execute

## Features

- Single-cycle instruction control
- Simple control logic
- Sequential execution
- Expandable design
