# CPU Core Design

## Version

v0.1

## Overview

The CPU Core integrates all internal components required to execute instructions.

## Core Components

- Program Counter (PC)
- Instruction Register (IR)
- Register File
- Arithmetic Logic Unit (ALU)
- Control Unit (CU)
- Flags Register
- Memory Interface

## Execution Pipeline

1. Fetch
2. Decode
3. Execute
4. Write Back

## Internal Connections

Memory
  │
  ▼
 MAR
  │
  ▼
 MDR
  │
  ▼
 IR
  │
  ▼
 Control Unit
  │
  ▼
 Register File
  │
  ▼
 ALU
  │
  ▼
 FLAGS
  │
  ▼
 Register File

## Clock

- Single Clock
- Rising Edge Triggered

## Reset

- PC = 0x00
- ACC = 0x00
- R0-R3 = 0x00
- FLAGS = 0x00

## Future Improvements

- Pipeline Execution
- Interrupt Controller
- DMA Support
- Cache
