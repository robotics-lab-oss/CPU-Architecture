# Assembler Specification

## Version

v0.1

## Overview

The assembler converts human-readable assembly language into 8-bit machine code.

## Source File

.asm

Example:

START:
LOAD #5
ADD #3
STORE 0x20
HALT

## Output File

.bin

Example:

00010005
01000003
00100020
11110000

## Labels

Example:

START:
LOOP:
END:

Labels are translated into memory addresses.

## Comments

Example:

LOAD #5 ; Load value into ACC

Everything after ';' is ignored.

## Number Formats

Decimal

10

Hexadecimal

0x0A

Binary

0b00001010

## Error Detection

- Invalid instruction
- Invalid operand
- Undefined label
- Memory overflow
- Syntax error

## Design Goals

- Simple
- Fast
- Easy to read
- Easy to implement
