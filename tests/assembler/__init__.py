"""
tests.assembler

MiniCPU 8-bit CPU Architecture
Assembler Test Suite

This package contains automated tests for
the MiniCPU assembler.

Test modules:

    test_lexer.py
        Tests source-code tokenization.

    test_parser.py
        Tests assembly syntax parsing.

    test_opcode.py
        Tests the 16-instruction opcode table.

    test_symbol_table.py
        Tests labels and symbol resolution.

    test_first_pass.py
        Tests first-pass address calculation.

    test_second_pass.py
        Tests second-pass symbol resolution.

    test_encoder.py
        Tests machine-code encoding.

    test_assembler.py
        Tests the complete assembler pipeline.

Assembler pipeline:

    Assembly Source
          │
          ▼
        Lexer
          │
          ▼
        Parser
          │
          ▼
     First Pass
          │
          ▼
    Symbol Table
          │
          ▼
    Second Pass
          │
          ▼
       Encoder
          │
          ▼
     Machine Code

The tests in this package verify each stage
independently and also verify the complete
assembler workflow.
"""

from __future__ import annotations


# ============================================================
# PACKAGE INFORMATION
# ============================================================

PACKAGE_NAME = "tests.assembler"

PROJECT_NAME = "MiniCPU"

CPU_ARCHITECTURE = "8-bit"

INSTRUCTION_COUNT = 16


# ============================================================
# TEST PACKAGE VERSION
# ============================================================

__version__ = "1.0.0"


# ============================================================
# SUPPORTED INSTRUCTION SIZES
# ============================================================

ONE_BYTE_INSTRUCTION_SIZE = 1

TWO_BYTE_INSTRUCTION_SIZE = 2


# ============================================================
# TEST MODULES
# ============================================================

TEST_MODULES = (
    "test_lexer",
    "test_parser",
    "test_opcode",
    "test_symbol_table",
    "test_first_pass",
    "test_second_pass",
    "test_encoder",
    "test_assembler",
)


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "PACKAGE_NAME",
    "PROJECT_NAME",
    "CPU_ARCHITECTURE",
    "INSTRUCTION_COUNT",
    "ONE_BYTE_INSTRUCTION_SIZE",
    "TWO_BYTE_INSTRUCTION_SIZE",
    "TEST_MODULES",
    "__version__",
]
