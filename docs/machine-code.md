# Machine Code Specification

## Version

v0.1

## Overview

Each instruction is 8 bits wide.

+------------+------------+
| Opcode     | Operand    |
| 4 bits     | 4 bits     |
+------------+------------+

## Instruction Encoding

| Binary | Mnemonic |
|--------|----------|
| 0000 | NOP |
| 0001 | LOAD |
| 0010 | STORE |
| 0011 | MOV |
| 0100 | ADD |
| 0101 | SUB |
| 0110 | AND |
| 0111 | OR |
| 1000 | XOR |
| 1001 | NOT |
| 1010 | CMP |
| 1011 | JMP |
| 1100 | JZ |
| 1101 | JNZ |
| 1110 | IN |
| 1111 | HALT |

## Examples

Assembly

LOAD #5

Machine Code

00010101

Assembly

ADD #3

Machine Code

01000011

Assembly

HALT

Machine Code

11110000

## Execution

1. Fetch instruction
2. Decode opcode
3. Read operand
4. Execute instruction
5. Update registers
6. Update flags
7. Increment Program Counter

## Future Extensions

- 16-bit instructions
- Extended opcode table
- Multi-byte operands
