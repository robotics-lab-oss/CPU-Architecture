; ============================================================
; MiniCPU 8-bit CPU
; programs/test.asm
;
; General CPU Instruction Test
; ============================================================

; Load value from memory address 0xF0
LOAD 0xF0

; Store accumulator into memory address 0xF1
STORE 0xF1

; Add value from memory address 0xF2
ADD 0xF2

; Subtract value from memory address 0xF3
SUB 0xF3

; Bitwise AND with memory address 0xF4
AND 0xF4

; Bitwise OR with memory address 0xF5
OR 0xF5

; Bitwise XOR with memory address 0xF6
XOR 0xF6

; Increment accumulator
INC

; Decrement accumulator
DEC

; Compare accumulator with memory address 0xF7
CMP 0xF7

; Output accumulator
OUT

; Stop CPU
HALT
