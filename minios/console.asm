; ============================================================
; console.asm
;
; MiniOS Console
; MiniCPU 8-bit Architecture
;
; Responsibilities:
;   - Console initialization
;   - Character input
;   - Character output
;   - New line
;   - Console clear request
;
; System interface:
;
;   A Register:
;       Character / value
;
; Memory:
;
;   0xF3 = System Call Argument
;   0xF4 = System Call Result
;
; ============================================================


; ============================================================
; CONSOLE INITIALIZATION
; ============================================================

CONSOLE_INIT:

    ; --------------------------------------------------------
    ; Initialize console state.
    ; --------------------------------------------------------

    NOP


    ; --------------------------------------------------------
    ; Start shell.
    ; --------------------------------------------------------

    JMP SHELL_START


; ============================================================
; CONSOLE OUTPUT
;
; Input:
;   A = value / character
;
; Operation:
;   OUT
; ============================================================

CONSOLE_PUTCHAR:

    OUT

    JMP CONSOLE_RETURN


; ============================================================
; CONSOLE INPUT
;
; Output:
;   A = input value / character
; ============================================================

CONSOLE_GETCHAR:

    IN

    STORE 0xF4

    JMP CONSOLE_RETURN


; ============================================================
; CONSOLE NEW LINE
;
; The actual terminal implementation determines
; the meaning of the newline value.
;
; Newline:
;   0x0A
;
; NOTE:
; The current ISA has no immediate-value instruction.
; Therefore the newline value must be provided
; through a predefined memory location.
; ============================================================

CONSOLE_NEWLINE:

    LOAD 0xFD

    OUT

    JMP CONSOLE_RETURN


; ============================================================
; CONSOLE CLEAR
;
; Hardware-dependent operation.
;
; The current MiniCPU ISA does not define a
; dedicated terminal clear instruction.
; ============================================================

CONSOLE_CLEAR:

    NOP

    JMP CONSOLE_RETURN


; ============================================================
; CONSOLE RETURN
; ============================================================

CONSOLE_RETURN:

    JMP KERNEL_MAIN
