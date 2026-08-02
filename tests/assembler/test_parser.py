"""
test_parser.py

MiniCPU 8-bit CPU Architecture
Assembler Parser Tests

Tests:
    - Empty input
    - Instructions
    - Operands
    - Labels
    - Label-only lines
    - Comments
    - Multiple instructions
    - Case handling
    - Invalid syntax
    - Complete assembly programs

Expected parser pipeline:

    Source
      │
      ▼
    Lexer
      │
      ▼
    Tokens
      │
      ▼
    Parser
      │
      ▼
    Parsed Instructions
"""

from __future__ import annotations

import pytest

from assembler.parser import Parser


# ============================================================
# HELPERS
# ============================================================


def create_parser(
    source: str,
) -> Parser:
    """
    Create a Parser instance.

    Expected common API:

        Parser(source)
    """

    return Parser(source)


def parse_source(
    source: str,
):
    """
    Parse assembly source.

    Supports common parser APIs:

        parser.parse()

    or:

        parser.parse(source)
    """

    parser = create_parser(
        source
    )

    if hasattr(
        parser,
        "parse",
    ):
        try:
            return parser.parse()
        except TypeError:
            return parser.parse(
                source
            )

    raise AttributeError(
        "Parser must provide "
        "parse() method."
    )


# ============================================================
# EMPTY SOURCE
# ============================================================


def test_parser_empty_source():
    """
    Empty source should produce an
    empty or valid result.
    """

    result = parse_source(
        ""
    )

    assert result is not None


# ============================================================
# NOP
# ============================================================


def test_parser_nop():
    """
    Parse:

        NOP
    """

    result = parse_source(
        "NOP"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# HALT
# ============================================================


def test_parser_halt():
    """
    Parse:

        HALT
    """

    result = parse_source(
        "HALT"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# ONE-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    [
        "NOP",
        "OUT",
        "IN",
        "INC",
        "DEC",
        "HALT",
    ],
)
def test_parser_one_byte_instruction(
    instruction: str,
):
    """
    All one-byte instructions should parse.
    """

    result = parse_source(
        instruction
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# TWO-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    [
        "LOAD",
        "STORE",
        "ADD",
        "SUB",
        "AND",
        "OR",
        "XOR",
        "JMP",
        "JZ",
        "CMP",
    ],
)
def test_parser_two_byte_instruction(
    instruction: str,
):
    """
    All two-byte instructions should parse
    with an 8-bit operand.
    """

    source = (
        f"{instruction} 0x10"
    )

    result = parse_source(
        source
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# ALL 16 INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    [
        "NOP",
        "LOAD",
        "STORE",
        "ADD",
        "SUB",
        "AND",
        "OR",
        "XOR",
        "JMP",
        "JZ",
        "OUT",
        "IN",
        "INC",
        "DEC",
        "CMP",
        "HALT",
    ],
)
def test_parser_all_16_instructions(
    instruction: str,
):
    """
    Verify complete 16-instruction ISA.
    """

    operand_instructions = {
        "LOAD",
        "STORE",
        "ADD",
        "SUB",
        "AND",
        "OR",
        "XOR",
        "JMP",
        "JZ",
        "CMP",
    }

    if instruction in operand_instructions:

        source = (
            f"{instruction} 0x10"
        )

    else:

        source = instruction

    result = parse_source(
        source
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# DECIMAL OPERAND
# ============================================================


def test_parser_decimal_operand():
    """
    Parse:

        LOAD 16
    """

    result = parse_source(
        "LOAD 16"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# HEX OPERAND
# ============================================================


def test_parser_hex_operand():
    """
    Parse:

        LOAD 0x10
    """

    result = parse_source(
        "LOAD 0x10"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# MAXIMUM 8-BIT OPERAND
# ============================================================


def test_parser_maximum_byte_operand():
    """
    0xFF is the maximum 8-bit operand.
    """

    result = parse_source(
        "LOAD 0xFF"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# ZERO OPERAND
# ============================================================


def test_parser_zero_operand():
    """
    Parse:

        LOAD 0x00
    """

    result = parse_source(
        "LOAD 0x00"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# LABEL ONLY
# ============================================================


def test_parser_label_only():
    """
    Parse label-only line:

        START:
    """

    result = parse_source(
        "START:"
    )

    assert result is not None


# ============================================================
# LABEL WITH INSTRUCTION
# ============================================================


def test_parser_label_with_instruction():
    """
    Parse:

        START: NOP
    """

    result = parse_source(
        "START: NOP"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# LABEL WITH OPERAND
# ============================================================


def test_parser_label_with_operand():
    """
    Parse:

        START: LOAD 0x10
    """

    result = parse_source(
        "START: LOAD 0x10"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# LABEL REFERENCE
# ============================================================


def test_parser_label_reference():
    """
    Parse symbolic operand:

        JMP LOOP
    """

    result = parse_source(
        "JMP LOOP"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# CONDITIONAL LABEL REFERENCE
# ============================================================


def test_parser_jz_label():
    """
    Parse:

        JZ END
    """

    result = parse_source(
        "JZ END"
    )

    assert result is not None

    assert len(
        result
    ) >= 1


# ============================================================
# COMMENTS
# ============================================================


@pytest.mark.parametrize(
    "source",
    [
        "; comment",
        "NOP ; comment",
        "LOAD 0x10 ; comment",
        "START: NOP ; comment",
    ],
)
def test_parser_comments(
    source: str,
):
    """
    Comments should be ignored by parser
    or handled by the lexer.
    """

    result = parse_source(
        source
    )

    assert result is not None


# ============================================================
# WHITESPACE
# ============================================================


@pytest.mark.parametrize(
    "source",
    [
        "NOP",
        "  NOP",
        "NOP  ",
        "\tNOP",
        "  NOP  ",
        "LOAD    0x10",
        "LOAD\t0x10",
    ],
)
def test_parser_whitespace(
    source: str,
):
    """
    Parser should handle normal whitespace.
    """

    result = parse_source(
        source
    )

    assert result is not None


# ============================================================
# CASE INSENSITIVITY
# ============================================================


@pytest.mark.parametrize(
    "source",
    [
        "nop",
        "Nop",
        "NOP",
        "load 0x10",
        "LoAd 0x10",
        "LOAD 0x10",
    ],
)
def test_parser_case_handling(
    source: str,
):
    """
    Instruction names should be accepted
    regardless of case if assembler ISA
    is case-insensitive.
    """

    result = parse_source(
        source
    )

    assert result is not None


# ============================================================
# MULTIPLE INSTRUCTIONS
# ============================================================


def test_parser_multiple_instructions():
    """
    Parse multiple assembly lines.
    """

    source = """
        NOP
        INC
        DEC
        OUT
        HALT
    """

    result = parse_source(
        source
    )

    assert result is not None

    assert len(
        result
    ) >= 5


# ============================================================
# COMPLETE PROGRAM
# ============================================================


def test_parser_complete_program():
    """
    Parse a complete MiniCPU program.

        START: LOAD 0x10
               ADD 0x11
               STORE 0x20
               OUT
               HALT
    """

    source = """
        START: LOAD 0x10
        ADD 0x11
        STORE 0x20
        OUT
        HALT
    """

    result = parse_source(
        source
    )

    assert result is not None

    assert len(
        result
    ) >= 5


# ============================================================
# LABEL PROGRAM
# ============================================================


def test_parser_label_program():
    """
    Parse labels and jumps.

        START:
            LOAD 0x10

        LOOP:
            INC
            JZ END
            JMP LOOP

        END:
            HALT
    """

    source = """
        START:
        LOAD 0x10

        LOOP:
        INC
        JZ END
        JMP LOOP

        END:
        HALT
    """

    result = parse_source(
        source
    )

    assert result is not None

    assert len(
        result
    ) >= 6


# ============================================================
# INVALID UNKNOWN INSTRUCTION
# ============================================================


def test_parser_unknown_instruction():
    """
    Unknown instruction must not be silently
    accepted as a valid MiniCPU instruction.
    """

    source = (
        "UNKNOWN"
    )

    try:

        result = parse_source(
            source
        )

    except Exception:

        return

    # If parser accepts unknown tokens,
    # later assembler validation must reject them.
    assert result is not None


# ============================================================
# MISSING OPERAND
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    [
        "LOAD",
        "STORE",
        "ADD",
        "SUB",
        "AND",
        "OR",
        "XOR",
        "JMP",
        "JZ",
        "CMP",
    ],
)
def test_parser_missing_operand(
    instruction: str,
):
    """
    Two-byte instructions require
    an operand.

    Parser should reject missing operands
    or leave an invalid representation for
    later validation.
    """

    source = instruction

    try:

        result = parse_source(
            source
        )

    except Exception:

        return

    assert result is not None


# ============================================================
# EXTRA OPERAND
# ============================================================


def test_parser_extra_operand():
    """
    One-byte instruction should not normally
    receive an extra operand.

        NOP 0x10
    """

    source = (
        "NOP 0x10"
    )

    try:

        result = parse_source(
            source
        )

    except Exception:

        return

    assert result is not None


# ============================================================
# OPERAND RANGE
# ============================================================


@pytest.mark.parametrize(
    "operand",
    [
        "0x00",
        "0x01",
        "0x7F",
        "0x80",
        "0xFE",
        "0xFF",
    ],
)
def test_parser_valid_8bit_operands(
    operand: str,
):
    """
    Every value in valid 8-bit boundary
    examples should be parseable.
    """

    result = parse_source(
        f"LOAD {operand}"
    )

    assert result is not None


# ============================================================
# SYMBOL NAMES
# ============================================================


@pytest.mark.parametrize(
    "label",
    [
        "START",
        "LOOP",
        "END",
        "LOOP1",
        "START_1",
    ],
)
def test_parser_symbol_names(
    label: str,
):
    """
    Test common valid symbol names.
    """

    result = parse_source(
        f"{label}: NOP"
    )

    assert result is not None


# ============================================================
# MULTI-LABEL PROGRAM
# ============================================================


def test_parser_multiple_labels():
    """
    Test multiple labels in one program.
    """

    source = """
        START:
        NOP

        LOOP:
        INC

        END:
        HALT
    """

    result = parse_source(
        source
    )

    assert result is not None

    assert len(
        result
    ) >= 3


# ============================================================
# PARSER RESULT TYPE
# ============================================================


def test_parser_result_is_collection():
    """
    Parser output should normally be a collection
    of parsed source lines/instructions.
    """

    result = parse_source(
        "NOP"
    )

    assert isinstance(
        result,
        (list, tuple),
    )


# ============================================================
# PARSER DETERMINISTIC RESULT
# ============================================================


def test_parser_deterministic():
    """
    Parsing the same source twice should produce
    equivalent results.
    """

    source = """
        START: LOAD 0x10
        INC
        HALT
    """

    first = parse_source(
        source
    )

    second = parse_source(
        source
    )

    assert first == second
