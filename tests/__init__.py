"""
tests

MiniCPU 8-bit CPU Architecture
Test Suite

This package contains automated tests for
the complete MiniCPU project.

Test categories include:

    - Assembler tests
    - Lexer tests
    - Parser tests
    - Opcode tests
    - Symbol table tests
    - First-pass assembler tests
    - Second-pass assembler tests
    - Encoder tests
    - Complete assembler tests
    - CPU tests
    - Memory tests
    - ALU tests
    - Register tests
    - Control Unit tests
    - Instruction Decoder tests
    - Instruction Executor tests

The test suite is designed to verify that
each MiniCPU component works independently
and that all components work together.

Project architecture:

    Source Code
        │
        ├── Assembler
        │
        └── CPU
              │
              ▼
        Automated Tests

Run all tests with:

    python -m pytest

Or:

    pytest

Run assembler tests only:

    python -m pytest tests/assembler

Run a specific test file:

    python -m pytest tests/assembler/test_lexer.py

Run with verbose output:

    python -m pytest -v

Run with coverage:

    python -m pytest --cov=assembler --cov=cpu
"""

from __future__ import annotations


# ============================================================
# TEST PACKAGE VERSION
# ============================================================

__version__ = "1.0.0"


# ============================================================
# PROJECT INFORMATION
# ============================================================

PROJECT_NAME = "MiniCPU"

CPU_ARCHITECTURE = "8-bit"

INSTRUCTION_COUNT = 16


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "__version__",
    "PROJECT_NAME",
    "CPU_ARCHITECTURE",
    "INSTRUCTION_COUNT",
]
