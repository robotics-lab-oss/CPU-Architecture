; ============================================================
; MiniCPU 8-bit CPU
; programs/branch.asm
;
; Branch / Jump Instruction Test
;
; Instructions tested:
;   LOAD
;   CMP
;   JZ
;   JMP
;   OUT
;   HALT
;
; Current ISA:
;   JMP address  -> PC = address
;   JZ address   -> Jump when Zero Flag = 1
;   CMP address  -> Compare A with MEM[address]
; ============================================================


; ------------------------------------------------------------
; Load value into accumulator
;
; A = MEM[0xF0]
; ------------------------------------------------------------

LOAD 0xF0


; ------------------------------------------------------------
; Compare accumulator with memory
;
; Compare:
;   A == MEM[0xF1]
;
; If equal:
;   Zero Flag = 1
; ------------------------------------------------------------

CMP 0xF1


; ------------------------------------------------------------
; Jump if Zero Flag is set
;
; NOTE:
; Replace 0x08 with the actual byte address
; of the EQUAL label after assembly.
; ------------------------------------------------------------

JZ 0x08


; ------------------------------------------------------------
; Values are not equal
; Output current accumulator
; ------------------------------------------------------------

OUT


; ------------------------------------------------------------
; Stop CPU
; ------------------------------------------------------------

HALT


; ------------------------------------------------------------
; EQUAL
;
; Execution reaches here when:
;
;   A == MEM[0xF1]
;
; ------------------------------------------------------------

OUT

HALT
