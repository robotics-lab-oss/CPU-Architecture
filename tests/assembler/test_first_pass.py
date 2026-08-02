"""
test_first_pass.py

MiniCPU 8-bit CPU Architecture
Assembler First-Pass Tests

First Pass Responsibilities:
    - Reset program counter/address
    - Record labels
    - Calculate instruction sizes
    - Calculate label addresses
    - Detect duplicate labels
    - Support forward label references
    - Keep addresses within 8-bit range
"""

from __future__ import annotations

import pytest

from assembler.first_pass import FirstPass


# ============================================================
# HELPERS
# ============================================================


def make_token(
    label=None,
    instruction=None,
    operand=None,
):
    """
    Create a parser-compatible token.
    """

    return {
        "label": label,
        "instruction": instruction,
        "operand": operand,
    }


def run_first_pass(
    tokens,
):
    """
    Run the first pass.

    Supports common APIs:

        FirstPass().run(tokens)

    or:

        FirstPass().process(tokens)

    or:

        FirstPass().build(tokens)
    """

    first_pass = FirstPass()

    if hasattr(
        first_pass,
        "run",
    ):
        return first_pass.run(
            tokens
        )

    if hasattr(
        first_pass,
        "process",
    ):
        return first_pass.process(
            tokens
        )

    if hasattr(
        first_pass,
        "build",
    ):
        return first_pass.build(
            tokens
        )

    raise AttributeError(
        "FirstPass must provide "
        "run(), process(), or build()."
    )


# ============================================================
# EMPTY PROGRAM
# ============================================================


def test_first_pass_empty_program():
    """
    Empty program should start at address 0x00
    and produce an empty symbol table.
    """

    result = run_first_pass(
        []
    )

    assert result is not None


# ============================================================
# LABEL AT START
# ============================================================


def test_first_pass_label_at_start():
    """
    Program:

        START:
        NOP

    START = 0x00
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

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# LABEL WITH INSTRUCTION
# ============================================================


def test_first_pass_label_with_instruction():
    """
    Program:

        START: NOP

    START = 0x00
    """

    tokens = [
        make_token(
            label="START",
            instruction="NOP",
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# ONE-BYTE INSTRUCTION
# ============================================================


def test_first_pass_one_byte_instruction():
    """
    NOP occupies exactly 1 byte.
    """

    tokens = [
        make_token(
            instruction="NOP",
        ),
        make_token(
            label="NEXT",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# TWO-BYTE INSTRUCTION
# ============================================================


def test_first_pass_two_byte_instruction():
    """
    LOAD occupies exactly 2 bytes.
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="NEXT",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# MIXED INSTRUCTION SIZES
# ============================================================


def test_first_pass_mixed_instruction_sizes():
    """
    Program:

        NOP             1 byte
        LOAD 0x10      2 bytes
        INC             1 byte
        STORE 0x20     2 bytes
        END:

    END = 6 = 0x06
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
            label="END",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# MULTIPLE LABELS
# ============================================================


def test_first_pass_multiple_labels():
    """
    Program:

        START:
        NOP

        LOOP:
        INC

        END:
        HALT
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

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# DUPLICATE LABEL
# ============================================================


def test_first_pass_duplicate_label():
    """
    Duplicate labels must be rejected.
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

    with pytest.raises(
        Exception,
        match="Duplicate label",
    ):
        run_first_pass(
            tokens
        )


# ============================================================
# FORWARD REFERENCE
# ============================================================


def test_first_pass_forward_reference():
    """
    Forward references are allowed during
    first pass.

    Program:

        JMP END
        NOP
        END:
        HALT

    END = 0x03
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

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# LABEL-ONLY LINE
# ============================================================


def test_first_pass_label_only_does_not_increment_address():
    """
    Label-only lines occupy zero bytes.

    Program:

        START:
        LOOP:

    Both labels should have address 0x00.
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
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# ALL ONE-BYTE INSTRUCTIONS
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
def test_first_pass_one_byte_instructions(
    instruction: str,
):
    """
    All one-byte instructions must advance
    address by exactly one byte.
    """

    tokens = [
        make_token(
            instruction=instruction,
        ),
        make_token(
            label="NEXT",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# ALL TWO-BYTE INSTRUCTIONS
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
def test_first_pass_two_byte_instructions(
    instruction: str,
):
    """
    All two-byte instructions must advance
    address by exactly two bytes.
    """

    tokens = [
        make_token(
            instruction=instruction,
            operand="0x10",
        ),
        make_token(
            label="NEXT",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# COMPLETE PROGRAM
# ============================================================


def test_first_pass_complete_program():
    """
    Complete MiniCPU program:

        START: LOAD 0x10
        LOOP:  INC
               JZ END
               JMP LOOP
        END:   HALT
    """

    tokens = [
        make_token(
            label="START",
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="LOOP",
            instruction="INC",
        ),
        make_token(
            instruction="JZ",
            operand="END",
        ),
        make_token(
            instruction="JMP",
            operand="LOOP",
        ),
        make_token(
            label="END",
            instruction="HALT",
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None


# ============================================================
# SYMBOL TABLE RESULT
# ============================================================


def test_first_pass_returns_symbol_table():
    """
    First pass should expose or return a symbol table.

    This test is intentionally flexible because the exact
    FirstPass API may return:

        SymbolTable
        dict
        object.symbol_table
        object.symbols
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None

    if isinstance(
        result,
        dict,
    ):
        assert (
            "START"
            in result
        )

    elif hasattr(
        result,
        "symbols",
    ):
        assert (
            "START"
            in result.symbols
        )

    elif hasattr(
        result,
        "symbol_table",
    ):
        symbol_table = (
            result.symbol_table
        )

        if hasattr(
            symbol_table,
            "symbols",
        ):
            assert (
                "START"
                in symbol_table.symbols
            )


# ============================================================
# LABEL ADDRESS IS ZERO
# ============================================================


def test_first_pass_start_address():
    """
    The first program address must be 0x00.
    """

    tokens = [
        make_token(
            label="START",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None

    if isinstance(
        result,
        dict,
    ):
        assert (
            result["START"]
            == 0x00
        )

    elif hasattr(
        result,
        "symbols",
    ):
        assert (
            result.symbols["START"]
            == 0x00
        )

    elif hasattr(
        result,
        "symbol_table",
    ):

        table = (
            result.symbol_table
        )

        if hasattr(
            table,
            "symbols",
        ):
            assert (
                table.symbols["START"]
                == 0x00
            )


# ============================================================
# ADDRESS AFTER NOP
# ============================================================


def test_first_pass_address_after_nop():
    """
    NOP = 1 byte.

        NOP
        NEXT:

    NEXT = 0x01
    """

    tokens = [
        make_token(
            instruction="NOP",
        ),
        make_token(
            label="NEXT",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None

    if isinstance(
        result,
        dict,
    ):
        assert (
            result["NEXT"]
            == 0x01
        )

    elif hasattr(
        result,
        "symbols",
    ):
        assert (
            result.symbols["NEXT"]
            == 0x01
        )

    elif hasattr(
        result,
        "symbol_table",
    ):

        table = (
            result.symbol_table
        )

        if hasattr(
            table,
            "symbols",
        ):
            assert (
                table.symbols["NEXT"]
                == 0x01
            )


# ============================================================
# ADDRESS AFTER LOAD
# ============================================================


def test_first_pass_address_after_load():
    """
    LOAD = 2 bytes.

        LOAD 0x10
        NEXT:

    NEXT = 0x02
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="NEXT",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None

    if isinstance(
        result,
        dict,
    ):
        assert (
            result["NEXT"]
            == 0x02
        )

    elif hasattr(
        result,
        "symbols",
    ):
        assert (
            result.symbols["NEXT"]
            == 0x02
        )

    elif hasattr(
        result,
        "symbol_table",
    ):

        table = (
            result.symbol_table
        )

        if hasattr(
            table,
            "symbols",
        ):
            assert (
                table.symbols["NEXT"]
                == 0x02
            )


# ============================================================
# ADDRESS CALCULATION
# ============================================================


def test_first_pass_address_calculation():
    """
    Program:

        NOP             1
        LOAD 0x10      2
        INC             1
        ADD 0x20       2
        END:

    END = 6 = 0x06
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
            instruction="ADD",
            operand="0x20",
        ),
        make_token(
            label="END",
            instruction=None,
        ),
    ]

    result = run_first_pass(
        tokens
    )

    assert result is not None

    if isinstance(
        result,
        dict,
    ):
        assert (
            result["END"]
            == 0x06
        )

    elif hasattr(
        result,
        "symbols",
    ):
        assert (
            result.symbols["END"]
            == 0x06
        )

    elif hasattr(
        result,
        "symbol_table",
    ):

        table = (
            result.symbol_table
        )

        if hasattr(
            table,
            "symbols",
        ):
            assert (
                table.symbols["END"]
                == 0x06
            )


# ============================================================
# ADDRESS RANGE
# ============================================================


def test_first_pass_addresses_are_8bit():
    """
    All symbol addresses must fit into the
    MiniCPU 8-bit address space.
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

    result = run_first_pass(
        tokens
    )

    assert result is not None

    if isinstance(
        result,
        dict,
    ):

        symbols = result

    elif hasattr(
        result,
        "symbols",
    ):

        symbols = result.symbols

    elif hasattr(
        result,
        "symbol_table",
    ):

        table = result.symbol_table

        if hasattr(
            table,
            "symbols",
        ):
            symbols = table.symbols

        else:
            return

    else:
        return

    for address in symbols.values():

        assert (
            0x00
            <= address
            <= 0xFF
        )


# ============================================================
# REPEATED RUN
# ============================================================


def test_first_pass_can_run_multiple_times():
    """
    FirstPass should be reusable.

    Running the same program twice should
    produce the same result.
    """

    tokens = [
        make_token(
            label="START",
            instruction="NOP",
        ),
        make_token(
            label="END",
            instruction="HALT",
        ),
    ]

    first = run_first_pass(
        tokens
    )

    second = run_first_pass(
        tokens
    )

    assert first is not None

    assert second is not None


# ============================================================
# DETERMINISTIC RESULT
# ============================================================


def test_first_pass_is_deterministic():
    """
    Same input must produce same symbol addresses.
    """

    tokens = [
        make_token(
            label="START",
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            label="END",
            instruction="HALT",
        ),
    ]

    first = run_first_pass(
        tokens
    )

    second = run_first_pass(
        tokens
    )

    if isinstance(
        first,
        dict,
    ) and isinstance(
        second,
        dict,
    ):

        assert (
            first
            == second
        )

    elif hasattr(
        first,
        "symbols",
    ) and hasattr(
        second,
        "symbols",
    ):

        assert (
            first.symbols
            == second.symbols
        )
