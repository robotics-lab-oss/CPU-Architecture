; ============================================================
; system_calls.asm
;
; MiniOS System Calls
; MiniCPU 8-bit Architecture
;
; CPU:
;   - 8-bit data
;   - 8-bit address
;   - 256 bytes memory
;   - 16 instructions
;
; System Call Convention:
;
;   A Register:
;       System call number
;
;   Memory:
;       0xF2 = System Call Number
;       0xF3 = System Call Argument
;       0xF4 = System Call Result
;
; System Calls:
;
;   0x01  SYS_PRINT
;   0x02  SYS_INPUT
;   0x03  SYS_EXIT
;   0x04  SYS_CLEAR
;
; ============================================================


; ============================================================
; SYSTEM CALL ENTRY
; ============================================================

SYSCALL_ENTRY:

    ; --------------------------------------------------------
    ; Save system call number.
    ; --------------------------------------------------------

    STORE 0xF2


    ; --------------------------------------------------------
    ; Check SYS_PRINT
    ;
    ; Compare A with value stored at SYS_PRINT_ID.
    ; --------------------------------------------------------

    CMP SYS_PRINT_ID

    JZ SYSCALL_PRINT


    ; --------------------------------------------------------
    ; Check SYS_INPUT
    ; --------------------------------------------------------

    LOAD 0xF2

    CMP SYS_INPUT_ID

    JZ SYSCALL_INPUT


    ; --------------------------------------------------------
    ; Check SYS_EXIT
    ; --------------------------------------------------------

    LOAD 0xF2

    CMP SYS_EXIT_ID

    JZ SYSCALL_EXIT


    ; --------------------------------------------------------
    ; Check SYS_CLEAR
    ; --------------------------------------------------------

    LOAD 0xF2

    CMP SYS_CLEAR_ID

    JZ SYSCALL_CLEAR


    ; --------------------------------------------------------
    ; Unknown system call.
    ; --------------------------------------------------------

    JMP SYSCALL_UNKNOWN


; ============================================================
; SYS_PRINT
;
; Print value stored in SYS_ARG.
; ============================================================

SYSCALL_PRINT:

    LOAD 0xF3

    OUT

    LOAD 0xF2

    JMP SYSCALL_RETURN


; ============================================================
; SYS_INPUT
;
; Read input into accumulator.
; Store result in SYS_RESULT.
; ============================================================

SYSCALL_INPUT:

    IN

    STORE 0xF4

    JMP SYSCALL_RETURN


; ============================================================
; SYS_EXIT
;
; Stop the current operating system execution.
; ============================================================

SYSCALL_EXIT:

    HALT


; ============================================================
; SYS_CLEAR
;
; Console clear operation.
;
; Actual console implementation will be
; connected later.
; ============================================================

SYSCALL_CLEAR:

    NOP

    JMP SYSCALL_RETURN


; ============================================================
; UNKNOWN SYSTEM CALL
; ============================================================

SYSCALL_UNKNOWN:

    ; Unknown syscall is ignored for now.

    NOP

    JMP SYSCALL_RETURN


; ============================================================
; SYSTEM CALL RETURN
; ============================================================

SYSCALL_RETURN:

    JMP KERNEL_RETURN


; ============================================================
; SYSTEM CALL IDs
; ============================================================

SYS_PRINT_ID:

    NOP


SYS_INPUT_ID:

    NOP


SYS_EXIT_ID:

    NOP


SYS_CLEAR_ID:

    NOP
