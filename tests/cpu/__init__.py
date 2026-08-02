"""
tests/cpu/__init__.py

MiniCPU 8-bit CPU Architecture
CPU Test Package

This package contains automated tests for
the MiniCPU CPU core and its components.

Test modules:

    test_cpu.py
    test_registers.py
    test_alu.py
    test_control_unit.py
    test_instruction_decoder.py
    test_instruction_executor.py
    test_flags.py
    test_memory.py
    test_bus.py
    test_program_counter.py
    test_stack.py

The CPU test suite verifies:

- 8-bit data operations
- Register behavior
- ALU arithmetic
- ALU logical operations
- CPU flags
- Program counter
- Memory access
- Stack operations
- Bus communication
- Instruction decoding
- Instruction execution
- Control unit behavior
- Complete CPU fetch-decode-execute cycle

Expected CPU architecture:

    Data width:
        8-bit

    Address width:
        8-bit

    Address space:
        256 bytes

    Address range:
        0x00 - 0xFF

    Instruction count:
        16

Instruction format:

    1-byte instruction:
        [ OPCODE ]

    2-byte instruction:
        [ OPCODE ][ OPERAND ]

The test package intentionally contains no
runtime CPU logic. It only provides package
metadata and test namespace organization.
"""

from __future__ import annotations


# ============================================================
# TEST PACKAGE METADATA
# ============================================================

__title__ = "MiniCPU CPU Test Suite"

__description__ = (
    "Automated tests for the MiniCPU "
    "8-bit CPU architecture."
)

__architecture__ = "8-bit"

__address_width__ = 8

__data_width__ = 8

__address_space__ = 256

__instruction_count__ = 16


# ============================================================
# ARCHITECTURE CONSTANTS
# ============================================================

MIN_VALUE = 0x00

MAX_VALUE = 0xFF

MEMORY_SIZE = 0x100

ADDRESS_MASK = 0xFF

BYTE_MASK = 0xFF


# ============================================================
# TEST MODULES
# ============================================================

TEST_MODULES = (
    "test_cpu",
    "test_registers",
    "test_alu",
    "test_control_unit",
    "test_instruction_decoder",
    "test_instruction_executor",
    "test_flags",
    "test_memory",
    "test_bus",
    "test_program_counter",
    "test_stack",
)


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "__title__",
    "__description__",
    "__architecture__",
    "__address_width__",
    "__data_width__",
    "__address_space__",
    "__instruction_count__",
    "MIN_VALUE",
    "MAX_VALUE",
    "MEMORY_SIZE",
    "ADDRESS_MASK",
    "BYTE_MASK",
    "TEST_MODULES",
]
