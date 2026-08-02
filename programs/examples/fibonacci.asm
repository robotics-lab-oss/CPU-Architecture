; ============================================================
; fibonacci.asm
;
; MiniCPU 8-bit CPU
;
; Fibonacci sequence:
;
;   0, 1, 1, 2, 3, 5, 8, 13 ...
;
; Registers:
;   Accumulator (A)
;
; Memory:
;   0xF8 = First Fibonacci value
;   0xF9 = Second Fibonacci value
;   0xFA = Temporary next value
;
; ============================================================

        LOAD 0xF8
        OUT

        LOAD 0xF9
        OUT

LOOP:
        LOAD 0xF8
        ADD  0xF9
        STORE 0xFA

        LOAD 0xF9
        STORE 0xF8

        LOAD 0xFA
        STORE 0xF9

        OUT

        JMP LOOP
