; ============================================================
; kernel.asm
;
; MiniOS Kernel
; MiniCPU 8-bit Architecture
;
; CPU:
;   - 8-bit data
;   - 8-bit address
;   - 256 bytes memory
;   - 16 instructions
;
; Kernel responsibilities:
;   - Kernel entry
;   - System initialization
;   - Initialize kernel state
;   - Start console
;   - Start shell
;
; Memory layout:
;
;   0x00 - Bootloader
;   0x20 - Kernel
;   0x60 - System Calls
;   0x80 - Console
;   0xA0 - Shell
;
; ============================================================


; ============================================================
; KERNEL ENTRY
; ============================================================

KERNEL_ENTRY:

    ; --------------------------------------------------------
    ; Kernel is now running.
    ;
    ; Clear accumulator using the predefined
    ; zero-value memory location.
    ; --------------------------------------------------------

    LOAD 0xFE


    ; --------------------------------------------------------
    ; Store kernel state.
    ;
    ; 0xF1 = Kernel state
    ; --------------------------------------------------------

    STORE 0xF1


    ; --------------------------------------------------------
    ; Initialize kernel stack state.
    ;
    ; Stack handling is currently performed
    ; by the CPU stack component.
    ; --------------------------------------------------------

    NOP


    ; --------------------------------------------------------
    ; Start console subsystem.
    ;
    ; Console entry point:
    ;   CONSOLE_INIT
    ; --------------------------------------------------------

    JMP CONSOLE_INIT


; ============================================================
; KERNEL MAIN
; ============================================================

KERNEL_MAIN:

    ; --------------------------------------------------------
    ; Kernel main loop.
    ;
    ; Control is transferred to shell.
    ; Shell is responsible for user commands.
    ; --------------------------------------------------------

    JMP SHELL_START


; ============================================================
; RETURN FROM SHELL
; ============================================================

KERNEL_RETURN:

    ; --------------------------------------------------------
    ; If shell returns to kernel,
    ; restart kernel main loop.
    ; --------------------------------------------------------

    JMP KERNEL_MAIN


; ============================================================
; KERNEL HALT
; ============================================================

KERNEL_HALT:

    HALT
