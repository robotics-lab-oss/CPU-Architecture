# CPU Architecture

## Version

v0.1

## Registers

| Register | Size | Purpose |
|----------|------|---------|
| PC | 8-bit | Program Counter |
| IR | 8-bit | Instruction Register |
| ACC | 8-bit | Accumulator |
| MAR | 8-bit | Memory Address Register |
| MDR | 8-bit | Memory Data Register |
| FLAGS | 4-bit | Zero, Carry, Sign, Overflow |

## ALU

Operations:

- ADD
- SUB
- AND
- OR
- XOR
- NOT
- CMP

## Memory

- Address Bus: 8-bit
- Data Bus: 8-bit
- Memory Size: 256 Bytes

## Fetch Cycle

1. PC → MAR
2. Memory → MDR
3. MDR → IR
4. PC = PC + 1

## Execute Cycle

Instruction in IR is decoded and executed.

## Bus System

- Address Bus
- Data Bus
- Control Bus

## Clock

Single Clock Architecture
