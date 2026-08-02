"""
tests/integration/__init__.py

MiniCPU 8-bit CPU Architecture
Integration Test Package

This package contains integration tests
that verify communication between major
MiniCPU components.

Test layers include:

    Assembler
        ↓
    Machine Code
        ↓
    CPU
        ↓
    Simulator

Integration test modules:

    test_assembler_cpu.py
        Tests Assembler + CPU integration.

    test_programs.py
        Tests complete assembly programs
        from source code to CPU execution.
"""

__version__ = "1.0.0"
__author__ = "MiniCPU Project"

__all__ = [
    "test_assembler_cpu",
    "test_programs",
]
