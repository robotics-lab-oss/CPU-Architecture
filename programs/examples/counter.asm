; ============================================================
; counter.asm
;
; MiniCPU 8-bit CPU
;
; Counter Example
;
; Counts:
;   0, 1, 2, 3, 4, ...
;
; Memory:
;   0xF8 = Counter value
;   0xF9 = Constant 1
;
; ============================================================

        ORG 0x00

LOOP:
        LOAD 0xF8
        OUT

        ADD 0xF9
        STORE 0xF8

        JMP LOOP


; ============================================================
; DATA
; ============================================================

        ORG 0xF8

COUNTER:
        DB 0x00

ONE:
        DB 0x01
