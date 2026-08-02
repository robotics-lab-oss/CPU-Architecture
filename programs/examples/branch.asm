; ============================================================
; branch.asm
;
; MiniCPU 8-bit CPU
;
; Branch / Jump Test Program
;
; Instructions tested:
;   LOAD
;   STORE
;   SUB
;   CMP
;   JZ
;   JMP
;   OUT
;   HALT
;
; Expected Output:
;
;   3
;   2
;   1
;   0
;
; ============================================================


        ORG 0x00


START:

        ; Counter load करें
        LOAD COUNTER

        ; Counter output करें
        OUT

        ; Counter को 1 से कम करें
        SUB ONE

        ; नई Counter value save करें
        STORE COUNTER

        ; Zero check करें
        CMP ZERO

        ; अगर Counter == 0
        ; तो END पर jump करें
        JZ END

        ; अन्यथा START पर वापस जाएँ
        JMP START


END:

        HALT


; ============================================================
; DATA
; ============================================================

        ORG 0xF8


COUNTER:
        DB 0x03


ONE:
        DB 0x01


ZERO:
        DB 0x00
