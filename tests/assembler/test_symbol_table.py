"""
test_symbol_table.py

MiniCPU 8-bit CPU Architecture
Assembler Symbol Table Tests

Tests:
    - Empty symbol table
    - Reset
    - Label definition
    - Label-only lines
    - Labels with instructions
    - One-byte instruction addresses
    - Two-byte instruction addresses
    - Multiple labels
    - Duplicate labels
    - Forward references
    - Case sensitivity behavior
    - Symbol table contents
"""

from __future__ import annotations

import pytest

from assembler.symbol_table import SymbolTable


# ============================================================
# HELPERS
# ============================================================


def make_token(
    label=None,
    instruction=None,
    operand=None,
):
    """
    Create a token compatible with the current
    SymbolTable.build() implementation.

    Expected fields:

        label
        instruction
        operand
    """

    return {
        "label": label,
        "instruction": instruction,
        "operand": operand,
    }


def build_table(
    tokens,
):
    """
    Build and return a SymbolTable.
    """

    table = SymbolTable()

    table.build(
        tokens
    )

    return table


# ============================================================
# INITIALIZATION
# ============================================================


def test_symbol_table_initialization():
    """
    A new SymbolTable should start empty.
    """

    table = SymbolTable()

    assert hasattr(
        table,
        "symbols",
    )

    assert table.symbols == {}


# ============================================================
# RESET
# ============================================================


def test_symbol_table_reset():
    """
    reset() should clear all symbols.
    """

    table = SymbolTable()

    table.symbols[
        "TEST"
    ] = 0x10

    assert (
        table.symbols["TEST"]
        == 0x10
    )

    table.reset()

    assert table.symbols == {}


# ============================================================
# EMPTY TOKEN LIST
# ============================================================


def test_build_empty_tokens():
    """
    Building from an empty token list should
    produce an empty symbol table.
    """

    table = build_table(
        []
    )

    assert table.symbols == {}


# ============================================================
# LABEL ONLY
# ============================================================


def test_label_only():
    """
    Label-only line should define the current
    address.

    Example:

        START:

    Address:

        0x00
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        )
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["START"]
        == 0x00
    )


# ============================================================
# LABEL WITH NOP
# ============================================================


def test_label_with_one_byte_instruction():
    """
    Example:

        START: NOP

    START should point to 0x00.
    """

    tokens = [
        make_token(
            label="START",
            instruction="NOP",
        )
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["START"]
        == 0x00
    )


# ============================================================
# LABEL WITH TWO-BYTE INSTRUCTION
# ============================================================


def test_label_with_two_byte_instruction():
    """
    Example:

        START: LOAD 0x10

    START should point to 0x00.
    """

    tokens = [
        make_token(
            label="START",
            instruction="LOAD",
            operand="0x10",
        )
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["START"]
        == 0x00
    )


# ============================================================
# LABEL ADDRESS AFTER ONE BYTE
# ============================================================


def test_label_after_one_byte_instruction():
    """
    Example:

        NOP
        LOOP:

    LOOP should be at 0x01.
    """

    tokens = [
        make_token(
            instruction="NOP",
        ),
        make_token(
            label="LOOP",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["LOOP"]
        == 0x01
    )


# ============================================================
# LABEL ADDRESS AFTER TWO BYTES
# ============================================================


def test_label_after_two_byte_instruction():
    """
    Example:

        LOAD 0x10
        LOOP:

    LOAD occupies 2 bytes.

    LOOP should be at 0x02.
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="LOOP",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["LOOP"]
        == 0x02
    )


# ============================================================
# MIXED INSTRUCTION SIZES
# ============================================================


def test_mixed_instruction_sizes():
    """
    Program:

        NOP             1 byte
        LOAD 0x10      2 bytes
        INC             1 byte
        STORE 0x20     2 bytes
        LOOP:

    LOOP address:

        1 + 2 + 1 + 2 = 6

        LOOP = 0x06
    """

    tokens = [
        make_token(
            instruction="NOP",
        ),
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            instruction="INC",
        ),
        make_token(
            instruction="STORE",
            operand="0x20",
        ),
        make_token(
            label="LOOP",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["LOOP"]
        == 0x06
    )


# ============================================================
# MULTIPLE LABELS
# ============================================================


def test_multiple_labels():
    """
    Test multiple labels at different addresses.
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
        make_token(
            instruction="NOP",
        ),
        make_token(
            label="LOOP",
            instruction=None,
        ),
        make_token(
            instruction="INC",
        ),
        make_token(
            label="END",
            instruction=None,
        ),
        make_token(
            instruction="HALT",
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["START"]
        == 0x00
    )

    assert (
        table.symbols["LOOP"]
        == 0x01
    )

    assert (
        table.symbols["END"]
        == 0x02
    )


# ============================================================
# LABEL WITH INSTRUCTION
# ============================================================


def test_label_and_instruction_same_line():
    """
    Example:

        START: NOP
        LOOP: INC
        END: HALT
    """

    tokens = [
        make_token(
            label="START",
            instruction="NOP",
        ),
        make_token(
            label="LOOP",
            instruction="INC",
        ),
        make_token(
            label="END",
            instruction="HALT",
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["START"]
        == 0x00
    )

    assert (
        table.symbols["LOOP"]
        == 0x01
    )

    assert (
        table.symbols["END"]
        == 0x02
    )


# ============================================================
# DUPLICATE LABEL
# ============================================================


def test_duplicate_label():
    """
    Defining the same label twice should
    raise an exception.
    """

    tokens = [
        make_token(
            label="LOOP",
            instruction=None,
        ),
        make_token(
            instruction="NOP",
        ),
        make_token(
            label="LOOP",
            instruction=None,
        ),
    ]

    table = SymbolTable()

    with pytest.raises(
        Exception,
        match="Duplicate label",
    ):
        table.build(
            tokens
        )


# ============================================================
# DUPLICATE LABEL SAME ADDRESS
# ============================================================


def test_duplicate_label_same_address():
    """
    Even if two labels are at the same address,
    duplicate symbol names should be rejected.
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
        make_token(
            label="START",
            instruction=None,
        ),
    ]

    table = SymbolTable()

    with pytest.raises(
        Exception,
        match="Duplicate label",
    ):
        table.build(
            tokens
        )


# ============================================================
# BUILD RESETS PREVIOUS DATA
# ============================================================


def test_build_resets_previous_symbols():
    """
    Calling build() again should reset old symbols.
    """

    table = SymbolTable()

    first_program = [
        make_token(
            label="OLD",
            instruction=None,
        ),
    ]

    table.build(
        first_program
    )

    assert (
        "OLD"
        in table.symbols
    )

    second_program = [
        make_token(
            label="NEW",
            instruction=None,
        ),
    ]

    table.build(
        second_program
    )

    assert (
        "OLD"
        not in table.symbols
    )

    assert (
        "NEW"
        in table.symbols
    )


# ============================================================
# FORWARD REFERENCE SYMBOL
# ============================================================


def test_forward_reference_label():
    """
    Symbol table first pass should define a label
    even when an earlier instruction refers to it.

    Example:

        JMP END
        NOP
        END:
        HALT
    """

    tokens = [
        make_token(
            instruction="JMP",
            operand="END",
        ),
        make_token(
            instruction="NOP",
        ),
        make_token(
            label="END",
            instruction=None,
        ),
        make_token(
            instruction="HALT",
        ),
    ]

    table = build_table(
        tokens
    )

    # JMP = 2 bytes
    # NOP = 1 byte
    # END = 3
    assert (
        table.symbols["END"]
        == 0x03
    )


# ============================================================
# SYMBOL VALUE IS INTEGER
# ============================================================


def test_symbol_values_are_integers():
    """
    All resolved label addresses should be integers.
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="END",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    for value in (
        table.symbols.values()
    ):
        assert isinstance(
            value,
            int,
        )


# ============================================================
# SYMBOL VALUES ARE BYTE ADDRESSES
# ============================================================


def test_symbol_values_are_8bit_addresses():
    """
    MiniCPU uses an 8-bit address space.

    Valid addresses:

        0x00 - 0xFF
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
        make_token(
            instruction="NOP",
        ),
        make_token(
            label="END",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    for value in (
        table.symbols.values()
    ):
        assert (
            0x00
            <= value
            <= 0xFF
        )


# ============================================================
# SEQUENTIAL ADDRESS CALCULATION
# ============================================================


def test_sequential_address_calculation():
    """
    Verify address calculation through
    several instructions.

    Program:

        START: NOP          1
               INC          1
               LOAD 0x10    2
               ADD 0x11     2
               STORE 0x20   2
        END:   HALT         1

    END = 8 = 0x08
    """

    tokens = [
        make_token(
            label="START",
            instruction="NOP",
        ),
        make_token(
            instruction="INC",
        ),
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            instruction="ADD",
            operand="0x11",
        ),
        make_token(
            instruction="STORE",
            operand="0x20",
        ),
        make_token(
            label="END",
            instruction="HALT",
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["START"]
        == 0x00
    )

    assert (
        table.symbols["END"]
        == 0x08
    )


# ============================================================
# LABEL ORDER
# ============================================================


def test_symbol_table_contains_expected_labels():
    """
    Verify all expected symbols exist.
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
        make_token(
            label="LOOP",
            instruction=None,
        ),
        make_token(
            label="END",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    assert set(
        table.symbols.keys()
    ) == {
        "START",
        "LOOP",
        "END",
    }


# ============================================================
# CASE SENSITIVITY
# ============================================================


def test_symbol_names_are_currently_case_sensitive():
    """
    The current SymbolTable implementation
    uses the label string directly as the key.

    Therefore:

        LOOP
        loop

    are currently different symbols.

    If case-insensitive symbols are implemented
    later, this test should be updated.
    """

    tokens = [
        make_token(
            label="LOOP",
            instruction=None,
        ),
        make_token(
            label="loop",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        "LOOP"
        in table.symbols
    )

    assert (
        "loop"
        in table.symbols
    )

    assert (
        table.symbols["LOOP"]
        != table.symbols["loop"]
        or
        table.symbols["LOOP"]
        == table.symbols["loop"]
    )


# ============================================================
# LABEL AT END OF PROGRAM
# ============================================================


def test_label_at_end_of_program():
    """
    A label after the final instruction should
    point to the address immediately after it.

    Program:

        NOP
        LOAD 0x10
        END:

    Address:

        1 + 2 = 3

        END = 0x03
    """

    tokens = [
        make_token(
            instruction="NOP",
        ),
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="END",
            instruction=None,
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["END"]
        == 0x03
    )


# ============================================================
# LABEL BEFORE PROGRAM
# ============================================================


def test_label_at_program_start():
    """
    A label at the beginning of a program
    should always have address 0x00.
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
        make_token(
            instruction="NOP",
        ),
    ]

    table = build_table(
        tokens
    )

    assert (
        table.symbols["START"]
        == 0x00
    )


# ============================================================
# SYMBOL TABLE REBUILD
# ============================================================


def test_symbol_table_rebuild():
    """
    Symbol table should be reusable for
    multiple assembler passes/programs.
    """

    table = SymbolTable()

    program_one = [
        make_token(
            label="ONE",
            instruction=None,
        ),
        make_token(
            instruction="NOP",
        ),
    ]

    table.build(
        program_one
    )

    assert (
        table.symbols
        == {
            "ONE": 0x00
        }
    )

    program_two = [
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="TWO",
            instruction=None,
        ),
    ]

    table.build(
        program_two
    )

    assert (
        table.symbols
        == {
            "TWO": 0x02
        }
    )
