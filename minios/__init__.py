"""
minios

MiniOS for MiniCPU 8-bit Architecture.

MiniOS components:

    kernel.asm
        Main operating system kernel.

    boot.asm
        System boot and initialization code.

    system_calls.asm
        Operating system system-call interface.

    console.asm
        Console input/output routines.

    shell.asm
        Basic command shell.

Architecture:
    - 8-bit CPU
    - 8-bit addresses
    - 256-byte address space
    - 16 instructions
    - 1-byte and 2-byte instructions

This package contains the assembly source files
used to build the MiniOS system image.
"""

from __future__ import annotations


# ============================================================
# OS INFORMATION
# ============================================================

OS_NAME = "MiniOS"

OS_VERSION = "0.1.0"

OS_ARCHITECTURE = "MiniCPU-8"

CPU_DATA_WIDTH = 8

CPU_ADDRESS_WIDTH = 8

CPU_MEMORY_SIZE = 256

CPU_INSTRUCTION_COUNT = 16


# ============================================================
# OS MEMORY LAYOUT
# ============================================================

# Bootloader starts at address 0x00.
BOOT_START = 0x00

# Kernel starts after boot code.
# This address can be changed when the
# final linker/layout is implemented.
KERNEL_START = 0x20

# System call routines.
SYSCALL_START = 0x60

# Console routines.
CONSOLE_START = 0x80

# Shell starts at this address.
SHELL_START = 0xA0


# ============================================================
# OS STATES
# ============================================================

OS_RESET = "RESET"

OS_BOOTING = "BOOTING"

OS_RUNNING = "RUNNING"

OS_SHELL = "SHELL"

OS_HALTED = "HALTED"


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "OS_NAME",
    "OS_VERSION",
    "OS_ARCHITECTURE",
    "CPU_DATA_WIDTH",
    "CPU_ADDRESS_WIDTH",
    "CPU_MEMORY_SIZE",
    "CPU_INSTRUCTION_COUNT",
    "BOOT_START",
    "KERNEL_START",
    "SYSCALL_START",
    "CONSOLE_START",
    "SHELL_START",
    "OS_RESET",
    "OS_BOOTING",
    "OS_RUNNING",
    "OS_SHELL",
    "OS_HALTED",
]


# ============================================================
# DEBUG INFORMATION
# ============================================================

def get_os_info() -> dict:
    """
    Return MiniOS information.
    """

    return {
        "name": OS_NAME,
        "version": OS_VERSION,
        "architecture": OS_ARCHITECTURE,
        "data_width": CPU_DATA_WIDTH,
        "address_width": CPU_ADDRESS_WIDTH,
        "memory_size": CPU_MEMORY_SIZE,
        "instruction_count": (
            CPU_INSTRUCTION_COUNT
        ),
    }


def get_memory_layout() -> dict:
    """
    Return MiniOS memory layout.
    """

    return {
        "boot": BOOT_START,
        "kernel": KERNEL_START,
        "system_calls": SYSCALL_START,
        "console": CONSOLE_START,
        "shell": SHELL_START,
    }


if __name__ == "__main__":

    print(
        f"{OS_NAME} "
        f"v{OS_VERSION}"
    )

    print(
        f"Architecture: "
        f"{OS_ARCHITECTURE}"
    )

    print(
        f"CPU Width: "
        f"{CPU_DATA_WIDTH}-bit"
    )

    print(
        f"Memory: "
        f"{CPU_MEMORY_SIZE} bytes"
    )

    print(
        f"Instructions: "
        f"{CPU_INSTRUCTION_COUNT}"
    )

    print()

    print(
        "Memory Layout:"
    )

    for name, address in (
        get_memory_layout()
        .items()
    ):

        print(
            f"  {name:<15} "
            f"0x{address:02X}"
        )
