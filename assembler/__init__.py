"""
assembler

MiniCPU 8-bit CPU Architecture
Assembler Package

This package provides the components required to
translate MiniCPU assembly source code into
machine code.

Modules:
    lexer
        Assembly source tokenization.

    parser
        Token parsing and instruction representation.

    opcode
        16-instruction opcode definitions and
        instruction metadata.

    symbol_table
        Label and symbol management.

    assembler
        Main assembler pipeline.

    cli
        Command-line assembler interface.
"""

from .opcode import (
    OPCODES,
    ONE_BYTE_INSTRUCTIONS,
    TWO_BYTE_INSTRUCTIONS,
    OPERAND_INSTRUCTIONS,
    INSTRUCTION_SIZES,
    INSTRUCTION_COUNT,
    normalize_instruction,
    is_valid_instruction,
    get_opcode,
    get_instruction_size,
    requires_operand,
    get_instruction_info,
)

from .symbol_table import (
    SymbolTable,
)


__version__ = "1.0.0"


__all__ = [
    # Package
    "__version__",

    # Opcode definitions
    "OPCODES",
    "ONE_BYTE_INSTRUCTIONS",
    "TWO_BYTE_INSTRUCTIONS",
    "OPERAND_INSTRUCTIONS",
    "INSTRUCTION_SIZES",
    "INSTRUCTION_COUNT",

    # Opcode helpers
    "normalize_instruction",
    "is_valid_instruction",
    "get_opcode",
    "get_instruction_size",
    "requires_operand",
    "get_instruction_info",

    # Symbol table
    "SymbolTable",
]
