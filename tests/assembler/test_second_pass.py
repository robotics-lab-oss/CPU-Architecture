"""
test_second_pass.py

MiniCPU 8-bit CPU Architecture
Assembler Second-Pass Tests

Second Pass Responsibilities:
    - Resolve labels
    - Resolve numeric operands
    - Encode instructions
    - Generate final machine-code bytes
    - Detect undefined symbols
    - Preserve 1-byte / 2-byte instruction sizes

Expected ISA:
    1-byte:
        NOP
        OUT
        IN
        INC
        DEC
        HALT

    2-byte:
        LOAD
        STORE
        ADD
        SUB
        AND
        OR
        XOR
        JMP
        JZ
        CMP
"""

from __future__ import annotations

import pytest

from assembler.second_pass import SecondPass


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


def make_symbol_table(
    symbols=None,
):
    """
    Create a simple symbol table dictionary.
    """

    if symbols is None:
        return {}

    return dict(
        symbols
    )


def run_second_pass(
    tokens,
    symbols=None,
):
    """
    Run the second pass.

    Supports common APIs:

        SecondPass(symbols).run(tokens)

    or:

        SecondPass().run(tokens, symbols)

    or:

        SecondPass(symbols).process(tokens)

    or:

        SecondPass().process(tokens, symbols)

    or:

        SecondPass(symbols).encode(tokens)
    """

    symbol_table = make_symbol_table(
        symbols
    )

    try:
        second_pass = SecondPass(
            symbol_table
        )
    except TypeError:
        second_pass = SecondPass()

    methods = [
        "run",
        "process",
        "encode",
    ]

    for method_name in methods:

        if not hasattr(
            second_pass,
            method_name,
        ):
            continue

        method = getattr(
            second_pass,
            method_name,
        )

        try:
            return method(
                tokens
            )
        except TypeError:

            return method(
                tokens,
                symbol_table,
            )

    raise AttributeError(
        "SecondPass must provide "
        "run(), process(), or encode()."
    )


def normalize_output(
    result,
):
    """
    Normalize common machine-code output forms.

    Accepted:
        list
        tuple
        bytes
        bytearray
    """

    if isinstance(
        result,
        bytes,
    ):
        return list(
            result
        )

    if isinstance(
        result,
        bytearray,
    ):
        return list(
            result
        )

    if isinstance(
        result,
        tuple,
    ):
        return list(
            result
        )

    if isinstance(
        result,
        list,
    ):
        return result

    return result


# ============================================================
# EMPTY PROGRAM
# ============================================================


def test_second_pass_empty_program():
    """
    Empty program should produce empty machine code.
    """

    result = run_second_pass(
        []
    )

    result = normalize_output(
        result
    )

    assert result == []


# ============================================================
# NOP
# ============================================================


def test_second_pass_nop():
    """
    NOP:

        0x00
    """

    tokens = [
        make_token(
            instruction="NOP",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00
    ]


# ============================================================
# HALT
# ============================================================


def test_second_pass_halt():
    """
    HALT:

        0xF0
    """

    tokens = [
        make_token(
            instruction="HALT",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0xF0
    ]


# ============================================================
# ONE-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "instruction, expected",
    [
        ("NOP", 0x00),
        ("OUT", 0xA0),
        ("IN", 0xB0),
        ("INC", 0xC0),
        ("DEC", 0xD0),
        ("HALT", 0xF0),
    ],
)
def test_second_pass_one_byte_instructions(
    instruction: str,
    expected: int,
):
    """
    Verify every one-byte instruction.
    """

    tokens = [
        make_token(
            instruction=instruction,
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        expected
    ]


# ============================================================
# LOAD
# ============================================================


def test_second_pass_load():
    """
    LOAD 0x10:

        0x10 0x10
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
    ]


# ============================================================
# STORE
# ============================================================


def test_second_pass_store():
    """
    STORE 0x20:

        0x20 0x20
    """

    tokens = [
        make_token(
            instruction="STORE",
            operand="0x20",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x20,
        0x20,
    ]


# ============================================================
# ALL TWO-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "instruction, opcode",
    [
        ("LOAD", 0x10),
        ("STORE", 0x20),
        ("ADD", 0x30),
        ("SUB", 0x40),
        ("AND", 0x50),
        ("OR", 0x60),
        ("XOR", 0x70),
        ("JMP", 0x80),
        ("JZ", 0x90),
        ("CMP", 0xE0),
    ],
)
def test_second_pass_two_byte_instructions(
    instruction: str,
    opcode: int,
):
    """
    Every two-byte instruction must generate:

        opcode
        operand
    """

    tokens = [
        make_token(
            instruction=instruction,
            operand="0x42",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        opcode,
        0x42,
    ]


# ============================================================
# ZERO OPERAND
# ============================================================


def test_second_pass_zero_operand():
    """
    LOAD 0x00:

        0x10 0x00
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0x00",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x00,
    ]


# ============================================================
# MAXIMUM 8-BIT OPERAND
# ============================================================


def test_second_pass_ff_operand():
    """
    LOAD 0xFF:

        0x10 0xFF
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0xFF",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0xFF,
    ]


# ============================================================
# DECIMAL OPERAND
# ============================================================


def test_second_pass_decimal_operand():
    """
    LOAD 255 should encode the same as
    LOAD 0xFF.
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="255",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0xFF,
    ]


# ============================================================
# LABEL RESOLUTION
# ============================================================


def test_second_pass_label_resolution():
    """
    Symbol table:

        START = 0x00
        END   = 0x03

    Program:

        JMP END
        NOP
        END:
        HALT

    Expected:

        0x80 0x03
        0x00
        0xF0
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

    symbols = {
        "END": 0x03,
    }

    result = run_second_pass(
        tokens,
        symbols,
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x80,
        0x03,
        0x00,
        0xF0,
    ]


# ============================================================
# FORWARD LABEL
# ============================================================


def test_second_pass_forward_label():
    """
    Forward label must resolve correctly.
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

    symbols = {
        "END": 0x03,
    }

    result = run_second_pass(
        tokens,
        symbols,
    )

    result = normalize_output(
        result
    )

    assert result[0] == 0x80

    assert result[1] == 0x03


# ============================================================
# BACKWARD LABEL
# ============================================================


def test_second_pass_backward_label():
    """
    Backward label reference:

        START:
        NOP
        JMP START

    START = 0x00

    Expected:

        0x00
        0x80 0x00
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
            instruction="JMP",
            operand="START",
        ),
    ]

    symbols = {
        "START": 0x00,
    }

    result = run_second_pass(
        tokens,
        symbols,
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0x80,
        0x00,
    ]


# ============================================================
# JZ LABEL
# ============================================================


def test_second_pass_jz_label():
    """
    JZ END:

        0x90 <END_ADDRESS>
    """

    tokens = [
        make_token(
            instruction="JZ",
            operand="END",
        ),
    ]

    symbols = {
        "END": 0x20,
    }

    result = run_second_pass(
        tokens,
        symbols,
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x90,
        0x20,
    ]


# ============================================================
# LABEL IN ARITHMETIC INSTRUCTION
# ============================================================


@pytest.mark.parametrize(
    "instruction, opcode",
    [
        ("LOAD", 0x10),
        ("STORE", 0x20),
        ("ADD", 0x30),
        ("SUB", 0x40),
        ("AND", 0x50),
        ("OR", 0x60),
        ("XOR", 0x70),
        ("CMP", 0xE0),
    ],
)
def test_second_pass_symbol_operand(
    instruction: str,
    opcode: int,
):
    """
    Symbolic operands must be resolved
    for all two-byte instructions.
    """

    tokens = [
        make_token(
            instruction=instruction,
            operand="VALUE",
        ),
    ]

    symbols = {
        "VALUE": 0x80,
    }

    result = run_second_pass(
        tokens,
        symbols,
    )

    result = normalize_output(
        result
    )

    assert result == [
        opcode,
        0x80,
    ]


# ============================================================
# UNDEFINED SYMBOL
# ============================================================


def test_second_pass_undefined_symbol():
    """
    Undefined symbols must not silently encode
    as zero.

    Example:

        JMP UNKNOWN
    """

    tokens = [
        make_token(
            instruction="JMP",
            operand="UNKNOWN",
        ),
    ]

    with pytest.raises(
        Exception
    ):
        run_second_pass(
            tokens,
            {},
        )


# ============================================================
# LABEL-ONLY LINE
# ============================================================


def test_second_pass_label_only_line():
    """
    Label-only lines produce no machine-code byte.
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

    symbols = {
        "START": 0x00,
    }

    result = run_second_pass(
        tokens,
        symbols,
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00
    ]


# ============================================================
# MULTIPLE INSTRUCTIONS
# ============================================================


def test_second_pass_multiple_instructions():
    """
    Program:

        NOP
        INC
        DEC
        HALT

    Expected:

        00 C0 D0 F0
    """

    tokens = [
        make_token(
            instruction="NOP",
        ),
        make_token(
            instruction="INC",
        ),
        make_token(
            instruction="DEC",
        ),
        make_token(
            instruction="HALT",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0xC0,
        0xD0,
        0xF0,
    ]


# ============================================================
# MIXED PROGRAM
# ============================================================


def test_second_pass_mixed_program():
    """
    Program:

        LOAD 0x10
        INC
        STORE 0x20
        OUT
        HALT

    Expected:

        10 10
        C0
        20 20
        A0
        F0
    """

    tokens = [
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
            instruction="OUT",
        ),
        make_token(
            instruction="HALT",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0xC0,
        0x20,
        0x20,
        0xA0,
        0xF0,
    ]


# ============================================================
# COMPLETE PROGRAM
# ============================================================


def test_second_pass_complete_program():
    """
    Program:

        START: LOAD 0x10
        LOOP:  INC
               JZ END
               JMP LOOP
        END:   HALT

    Symbol table:

        START = 0x00
        LOOP  = 0x02
        END   = 0x07

    Expected:

        10 10
        C0
        90 07
        80 02
        F0
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

    symbols = {
        "START": 0x00,
        "LOOP": 0x02,
        "END": 0x07,
    }

    result = run_second_pass(
        tokens,
        symbols,
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0xC0,
        0x90,
        0x07,
        0x80,
        0x02,
        0xF0,
    ]


# ============================================================
# OUTPUT MUST CONTAIN ONLY BYTE VALUES
# ============================================================


def test_second_pass_output_is_8bit():
    """
    Every generated machine-code value must
    fit into one byte.
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0xFF",
        ),
        make_token(
            instruction="HALT",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result is not None

    for value in result:

        assert isinstance(
            value,
            int,
        )

        assert (
            0x00
            <= value
            <= 0xFF
        )


# ============================================================
# OUTPUT LENGTH
# ============================================================


def test_second_pass_output_length():
    """
    Verify byte count.

    Program:

        NOP          1
        LOAD 0x10    2
        INC          1
        HALT         1

    Total = 5 bytes.
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
            instruction="HALT",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert len(
        result
    ) == 5


# ============================================================
# CASE INSENSITIVE INSTRUCTIONS
# ============================================================


def test_second_pass_case_insensitive():
    """
    Lowercase/mixed-case instructions should
    resolve if the assembler ISA is case-insensitive.
    """

    tokens = [
        make_token(
            instruction="load",
            operand="0x10",
        ),
        make_token(
            instruction="NoP",
        ),
        make_token(
            instruction="hAlT",
        ),
    ]

    result = run_second_pass(
        tokens
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0x00,
        0xF0,
    ]


# ============================================================
# SYMBOL TABLE DOES NOT CHANGE
# ============================================================


def test_second_pass_does_not_modify_symbols():
    """
    Second pass should resolve symbols without
    modifying the original symbol table.
    """

    tokens = [
        make_token(
            instruction="JMP",
            operand="END",
        ),
    ]

    symbols = {
        "END": 0x20,
    }

    original = dict(
        symbols
    )

    run_second_pass(
        tokens,
        symbols,
    )

    assert symbols == original


# ============================================================
# DETERMINISTIC OUTPUT
# ============================================================


def test_second_pass_deterministic():
    """
    Same input and symbols must generate
    identical machine code.
    """

    tokens = [
        make_token(
            instruction="LOAD",
            operand="0x10",
        ),
        make_token(
            instruction="JMP",
            operand="END",
        ),
        make_token(
            label="END",
            instruction="HALT",
        ),
    ]

    symbols = {
        "END": 0x03,
    }

    first = normalize_output(
        run_second_pass(
            tokens,
            symbols,
        )
    )

    second = normalize_output(
        run_second_pass(
            tokens,
            symbols,
        )
    )

    assert first == second
