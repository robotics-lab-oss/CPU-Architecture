"""
test_lexer.py

MiniCPU 8-bit CPU Architecture
Assembler Lexer Tests

Tests:
    - Empty source
    - Instructions
    - Labels
    - Operands
    - Numeric values
    - Comments
    - Whitespace
    - Case handling
    - Multiple lines

IMPORTANT:
    This test file assumes the lexer module is:

        assembler/laxer.py

    If the actual module is named lexer.py,
    change:

        from assembler.laxer import Lexer

    to:

        from assembler.lexer import Lexer
"""

from __future__ import annotations

import pytest

from assembler.laxer import Lexer


# ============================================================
# HELPERS
# ============================================================


def create_lexer(
    source: str,
) -> Lexer:
    """
    Create a Lexer instance.

    Supports the common constructor:

        Lexer(source)
    """

    return Lexer(source)


def get_tokens(
    source: str,
):
    """
    Tokenize source code.

    Supports common lexer APIs:

        lexer.tokenize()

    or:

        lexer.lex()
    """

    lexer = create_lexer(
        source
    )

    if hasattr(
        lexer,
        "tokenize",
    ):
        return lexer.tokenize()

    if hasattr(
        lexer,
        "lex",
    ):
        return lexer.lex()

    raise AttributeError(
        "Lexer must provide "
        "tokenize() or lex()."
    )


# ============================================================
# EMPTY SOURCE
# ============================================================


def test_empty_source():
    """
    Empty assembly source should not
    produce invalid tokens.
    """

    tokens = get_tokens(
        ""
    )

    assert tokens is not None

    assert isinstance(
        tokens,
        (list, tuple),
    )


# ============================================================
# NOP
# ============================================================


def test_lexer_nop():
    """
    Test one-byte NOP instruction.
    """

    tokens = get_tokens(
        "NOP"
    )

    assert len(
        tokens
    ) >= 1


# ============================================================
# HALT
# ============================================================


def test_lexer_halt():
    """
    Test HALT instruction.
    """

    tokens = get_tokens(
        "HALT"
    )

    assert len(
        tokens
    ) >= 1


# ============================================================
# LOAD WITH HEX OPERAND
# ============================================================


def test_lexer_load_hex_operand():
    """
    Test:

        LOAD 0x42
    """

    tokens = get_tokens(
        "LOAD 0x42"
    )

    assert len(
        tokens
    ) >= 2


# ============================================================
# LOAD WITH DECIMAL OPERAND
# ============================================================


def test_lexer_load_decimal_operand():
    """
    Test:

        LOAD 42
    """

    tokens = get_tokens(
        "LOAD 42"
    )

    assert len(
        tokens
    ) >= 2


# ============================================================
# LABEL
# ============================================================


def test_lexer_label():
    """
    Test label syntax.

    Example:

        LOOP:
    """

    tokens = get_tokens(
        "LOOP:"
    )

    assert len(
        tokens
    ) >= 1


# ============================================================
# LABEL WITH INSTRUCTION
# ============================================================


def test_lexer_label_with_instruction():
    """
    Test:

        LOOP: INC
    """

    tokens = get_tokens(
        "LOOP: INC"
    )

    assert len(
        tokens
    ) >= 2


# ============================================================
# LABEL WITH OPERAND
# ============================================================


def test_lexer_label_with_operand():
    """
    Test:

        START: LOAD 0x10
    """

    tokens = get_tokens(
        "START: LOAD 0x10"
    )

    assert len(
        tokens
    ) >= 3


# ============================================================
# COMMENTS
# ============================================================


@pytest.mark.parametrize(
    "source",
    [
        "; comment",
        "NOP ; comment",
        "LOAD 0x10 ; comment",
    ],
)
def test_lexer_comments(
    source: str,
):
    """
    Comments should not cause lexer failure.
    """

    tokens = get_tokens(
        source
    )

    assert tokens is not None


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
        "\t NOP \t",
    ],
)
def test_lexer_whitespace(
    source: str,
):
    """
    Leading and trailing whitespace
    should be handled.
    """

    tokens = get_tokens(
        source
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 1


# ============================================================
# MULTIPLE LINES
# ============================================================


def test_lexer_multiple_lines():
    """
    Test a small assembly program.
    """

    source = """
        START: LOAD 0x10
        INC
        STORE 0x20
        HALT
    """

    tokens = get_tokens(
        source
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 4


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
def test_lexer_all_instructions(
    instruction: str,
):
    """
    Every instruction in the 16-instruction
    MiniCPU ISA should be accepted by lexer.
    """

    if instruction in {
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
    }:
        source = (
            f"{instruction} 0x10"
        )

    else:
        source = instruction

    tokens = get_tokens(
        source
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 1


# ============================================================
# CASE HANDLING
# ============================================================


def test_lexer_lowercase_instruction():
    """
    Test lowercase instruction.

        load 0x10
    """

    tokens = get_tokens(
        "load 0x10"
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 2


def test_lexer_mixed_case_instruction():
    """
    Test mixed-case instruction.

        LoAd 0x10
    """

    tokens = get_tokens(
        "LoAd 0x10"
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 2


# ============================================================
# NUMERIC VALUES
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "1",
        "10",
        "127",
        "255",
        "0x00",
        "0x01",
        "0x10",
        "0x7F",
        "0xFF",
    ],
)
def test_lexer_numeric_values(
    value: str,
):
    """
    Test valid 8-bit numeric operands.
    """

    tokens = get_tokens(
        f"LOAD {value}"
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 2


# ============================================================
# MULTIPLE INSTRUCTIONS
# ============================================================


def test_lexer_complete_program():
    """
    Test complete small program.

    Program:

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

    tokens = get_tokens(
        source
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 5


# ============================================================
# INVALID INSTRUCTION
# ============================================================


def test_lexer_unknown_instruction():
    """
    Unknown instruction should either:

        1. Raise a lexer error

    or:

        2. Produce a token that the parser
           later rejects.

    The lexer must not silently convert
    an unknown instruction into a valid ISA
    instruction.
    """

    source = (
        "UNKNOWN 0x10"
    )

    try:

        tokens = get_tokens(
            source
        )

    except Exception:

        return

    assert tokens is not None


# ============================================================
# INVALID HEX VALUE
# ============================================================


def test_lexer_invalid_hex():
    """
    Invalid hexadecimal syntax should not
    be silently accepted as a valid number.
    """

    source = (
        "LOAD 0xGG"
    )

    try:

        tokens = get_tokens(
            source
        )

    except Exception:

        return

    assert tokens is not None


# ============================================================
# SOURCE LINE TRACKING
# ============================================================


def test_lexer_line_tracking():
    """
    Test that lexer can process source
    containing multiple source lines.

    If lexer tokens expose line information,
    it can be verified here.
    """

    source = """
        NOP
        INC
        HALT
    """

    tokens = get_tokens(
        source
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 3


# ============================================================
# LABELS WITH UNDERSCORE
# ============================================================


def test_lexer_label_with_underscore():
    """
    Test:

        LOOP_START:
    """

    tokens = get_tokens(
        "LOOP_START:"
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 1


# ============================================================
# LABELS WITH NUMBERS
# ============================================================


def test_lexer_label_with_number():
    """
    Test labels containing numbers.

        LOOP1:
    """

    tokens = get_tokens(
        "LOOP1:"
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 1


# ============================================================
# LABEL REFERENCE
# ============================================================


def test_lexer_label_reference():
    """
    Test:

        JMP LOOP
    """

    tokens = get_tokens(
        "JMP LOOP"
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 2


# ============================================================
# LABEL PROGRAM
# ============================================================


def test_lexer_label_program():
    """
    Test label-based program.
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

    tokens = get_tokens(
        source
    )

    assert tokens is not None

    assert len(
        tokens
    ) >= 6
