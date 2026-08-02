; ============================================================
; loop.asm
;
; MiniCPU 8-bit CPU
;
; Simple Loop Example
;
; Program:
;   Counter को 5 से शुरू करता है।
;   हर iteration में 1 घटाता है।
;   Counter को OUT करता है।
;   जब Counter = 0 हो जाता है, program HALT करता है।
;
; Expected Output:
;
;   5
;   4
;   3
;   2
;   1
;   0
;
; Memory:
;   0xF8 = Counter
;   0xF9 = Constant 1
;
; ============================================================


        ORG 0x00


START:

        ; Counter की current value load करें
        LOAD 0xF8

        ; Counter output करें
        OUT

        ; Counter में से 1 घटाएँ
        SUB 0xF9

        ; नई value वापस memory में रखें
        STORE 0xF8

        ; Check करें कि Counter zero है या नहीं
        CMP 0xF8

        ; अगर Zero flag set है तो END पर जाएँ
        JZ END

        ; वापस loop में जाएँ
        JMP START


END:

        HALT


; ============================================================
; DATA
; ============================================================

        ORG 0xF8


COUNTER:
        DB 0x05


ONE:
        DB 0x01
