; ============================================================
; hello.asm
;
; MiniCPU 8-bit CPU
; Basic Hello / Output Test
;
; Purpose:
;   Test accumulator and OUT instruction.
;
; Instruction format:
;   LOAD address  -> 2 bytes
;   OUT          -> 1 byte
;   HALT         -> 1 byte
;
; Memory:
;   0xF0 = Output value
; ============================================================


        LOAD 0xF0      ; Load value from memory[0xF0] into A
        OUT             ; Output accumulator
        HALT            ; Stop CPU


; ============================================================
; DATA
; ============================================================

        ORG 0xF0

VALUE:
        DB 0x48         ; ASCII 'H'
