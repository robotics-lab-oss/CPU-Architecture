# Memory Map

## Version

v0.1

## Overview

The CPU uses an 8-bit address bus, allowing access to 256 bytes of memory.

## Memory Layout

| Address Range | Size | Purpose |
|---------------|------|---------|
| 0x00 - 0x0F | 16 B | Boot ROM |
| 0x10 - 0x3F | 48 B | Program Memory |
| 0x40 - 0x7F | 64 B | Data Memory (RAM) |
| 0x80 - 0x8F | 16 B | Stack |
| 0x90 - 0xEF | 96 B | Reserved |
| 0xF0 - 0xFF | 16 B | I/O Registers |

## Memory Details

### Boot ROM

Stores the first instructions executed after reset.

### Program Memory

Contains the executable program.

### Data Memory

Used for variables and temporary data.

### Stack

Stores return addresses and temporary values.

### Reserved

Reserved for future expansion.

### I/O Registers

Used for communication with external devices such as LEDs, switches, UART, timers, and sensors.

## Total Memory

256 Bytes
