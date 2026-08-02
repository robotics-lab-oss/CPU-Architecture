; ============================================================
; boot.asm
;
; MiniOS Bootloader
; MiniCPU 8-bit Architecture
;
; CPU:
;   - 8-bit data
;   - 8-bit address
;   - 256 bytes memory
;   - 16 instructions
;
; Boot flow:
;
;   RESET
;      |
;      v
;   BOOT
;      |
;      v
;   Initialize CPU state
;      |
;      v
;   Jump to Kernel
;
; Memory:
;
;   0x00 - Boot entry
;   0x20 - Kernel entry
;
; ============================================================


; ============================================================
; BOOT ENTRY
; ============================================================

BOOT:

    ; --------------------------------------------------------
    ; Initialize accumulator
    ;
    ; A = 0
    ;
    ; MiniCPU does not currently have an
    ; immediate LOAD instruction.
    ;
    ; Therefore memory address 0xFE is used
    ; as a zero-value system location.
    ; --------------------------------------------------------

    LOAD 0xFE


    ; --------------------------------------------------------
    ; Store initial value in kernel state
    ; --------------------------------------------------------

    STORE 0xF0


    ; --------------------------------------------------------
    ; Jump to kernel
    ; --------------------------------------------------------

    JMP KERNEL_START


; ============================================================
; BOOT DATA
; ============================================================

BOOT_ZERO:

    ; Reserved zero-value memory location

    NOP


; ============================================================
; KERNEL ENTRY ADDRESS
;
; The assembler resolves this symbol.
; ============================================================

KERNEL_START:

    JMP KERNEL_ENTRY


; ============================================================
; BOOT END
; ============================================================

BOOT_END:

    HALT
