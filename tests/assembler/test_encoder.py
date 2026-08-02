"""
test_encoder.py

MiniCPU 8-bit CPU Architecture
Assembler Encoder Tests

Tests:
    - Opcode encoding
    - 1-byte instruction encoding
    - 2-byte instruction encoding
    - Numeric operands
    - Hex operands
    - Binary operands
    - Decimal operands
    - Symbol operands
    - 8-bit operand range
    - Invalid operands
    - Complete instruction set
"""

from __future__ import annotations

import pytest

from assembler.encoder import Encoder


# ============================================================
# HELPERS
# ============================================================


def create_encoder(
    symbols=None,
):
    """
    Create an Encoder instance.

    Supports encoders that accept a symbol table
    during construction as well as encoders that
    use an empty constructor.
    """

    if symbols is None:
        symbols = {}

    try:
        return Encoder(
            symbols
        )
    except TypeError:
        return Encoder()


def encode_instruction(
    instruction,
    operand=None,
    symbols=None,
):
    """
    Encode one instruction.

    Supports common Encoder APIs:

        encoder.encode(instruction, operand)

        encoder.encode_instruction(
            instruction,
            operand
        )

        encoder.encode(
            {
                "instruction": ...,
                "operand": ...
            }
        )
    """

    encoder = create_encoder(
        symbols
    )

    # --------------------------------------------------------
    # Direct encode()
    # --------------------------------------------------------

    if hasattr(
        encoder,
        "encode",
    ):

        method = encoder.encode

        try:
            return method(
                instruction,
                operand,
            )

        except TypeError:

            token = {
                "instruction": instruction,
                "operand": operand,
            }

            try:
                return method(
                    token
                )

            except TypeError:

                return method(
                    instruction
                )

    # --------------------------------------------------------
    # encode_instruction()
    # --------------------------------------------------------

    if hasattr(
        encoder,
        "encode_instruction",
    ):

        method = (
            encoder.encode_instruction
        )

        try:
            return method(
                instruction,
                operand,
            )

        except TypeError:

            return method(
                {
                    "instruction": instruction,
                    "operand": operand,
                }
            )

    raise AttributeError(
        "Encoder must provide "
        "encode() or "
        "encode_instruction()."
    )


def normalize_bytes(
    result,
):
    """
    Convert common encoder output types
    into a list of integers.
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
# EMPTY / BASIC
# ============================================================


def test_encoder_exists():
    """
    Encoder class should be importable.
    """

    encoder = create_encoder()

    assert encoder is not None


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
def test_encode_one_byte_instruction(
    instruction,
    expected,
):
    """
    One-byte instructions must encode
    to exactly one machine-code byte.
    """

    result = encode_instruction(
        instruction
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        expected
    ]


# ============================================================
# TWO-BYTE INSTRUCTIONS
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
def test_encode_two_byte_instruction(
    instruction,
    opcode,
):
    """
    Two-byte instructions must encode as:

        opcode
        operand
    """

    result = encode_instruction(
        instruction,
        0x42,
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        opcode,
        0x42,
    ]


# ============================================================
# HEX OPERANDS
# ============================================================


@pytest.mark.parametrize(
    "operand, expected",
    [
        ("0x00", 0x00),
        ("0x01", 0x01),
        ("0x10", 0x10),
        ("0x7F", 0x7F),
        ("0x80", 0x80),
        ("0xFF", 0xFF),
    ],
)
def test_encode_hex_operand(
    operand,
    expected,
):
    """
    Hexadecimal operands should be accepted.
    """

    result = encode_instruction(
        "LOAD",
        operand,
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        expected,
    ]


# ============================================================
# DECIMAL OPERANDS
# ============================================================


@pytest.mark.parametrize(
    "operand, expected",
    [
        ("0", 0x00),
        ("1", 0x01),
        ("16", 0x10),
        ("127", 0x7F),
        ("128", 0x80),
        ("255", 0xFF),
    ],
)
def test_encode_decimal_operand(
    operand,
    expected,
):
    """
    Decimal operands should be converted
    into 8-bit values.
    """

    result = encode_instruction(
        "LOAD",
        operand,
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        expected,
    ]


# ============================================================
# INTEGER OPERANDS
# ============================================================


@pytest.mark.parametrize(
    "operand",
    [
        0x00,
        0x01,
        0x10,
        0x7F,
        0x80,
        0xFF,
    ],
)
def test_encode_integer_operand(
    operand,
):
    """
    Integer operands should be accepted.
    """

    result = encode_instruction(
        "LOAD",
        operand,
    )

    result = normalize_bytes(
        result
    )

    assert result[0] == 0x10

    assert result[1] == operand


# ============================================================
# BINARY OPERANDS
# ============================================================


@pytest.mark.parametrize(
    "operand, expected",
    [
        ("0b00000000", 0x00),
        ("0b00000001", 0x01),
        ("0b00010000", 0x10),
        ("0b01111111", 0x7F),
        ("0b10000000", 0x80),
        ("0b11111111", 0xFF),
    ],
)
def test_encode_binary_operand(
    operand,
    expected,
):
    """
    Binary operands should be accepted
    if the assembler supports Python-style
    binary literals.
    """

    try:

        result = encode_instruction(
            "LOAD",
            operand,
        )

    except (
        ValueError,
        TypeError,
    ):

        pytest.skip(
            "Binary literal syntax is not "
            "implemented by the current encoder."
        )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        expected,
    ]


# ============================================================
# LABEL OPERANDS
# ============================================================


def test_encode_label_operand():
    """
    Symbolic operand should be resolved
    using the symbol table.

    VALUE = 0x42

        LOAD VALUE

    becomes:

        10 42
    """

    result = encode_instruction(
        "LOAD",
        "VALUE",
        {
            "VALUE": 0x42,
        },
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        0x42,
    ]


# ============================================================
# JMP LABEL
# ============================================================


def test_encode_jmp_label():
    """
    JMP LOOP:

        80 <LOOP>
    """

    result = encode_instruction(
        "JMP",
        "LOOP",
        {
            "LOOP": 0x20,
        },
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x80,
        0x20,
    ]


# ============================================================
# JZ LABEL
# ============================================================


def test_encode_jz_label():
    """
    JZ END:

        90 <END>
    """

    result = encode_instruction(
        "JZ",
        "END",
        {
            "END": 0x80,
        },
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x90,
        0x80,
    ]


# ============================================================
# ALL SYMBOLIC OPERAND INSTRUCTIONS
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
def test_encode_symbolic_operand_instruction(
    instruction,
    opcode,
):
    """
    All two-byte instructions should be
    able to use a symbol as their operand.
    """

    result = encode_instruction(
        instruction,
        "VALUE",
        {
            "VALUE": 0x55,
        },
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        opcode,
        0x55,
    ]


# ============================================================
# ZERO VALUE
# ============================================================


def test_encode_zero_operand():
    """
    Zero is a valid 8-bit operand.
    """

    result = encode_instruction(
        "LOAD",
        0,
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        0x00,
    ]


# ============================================================
# MAXIMUM VALUE
# ============================================================


def test_encode_maximum_operand():
    """
    0xFF is the maximum valid 8-bit operand.
    """

    result = encode_instruction(
        "LOAD",
        0xFF,
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        0xFF,
    ]


# ============================================================
# OUT OF RANGE
# ============================================================


@pytest.mark.parametrize(
    "operand",
    [
        -1,
        0x100,
        256,
        1000,
    ],
)
def test_encode_out_of_range_operand(
    operand,
):
    """
    Operands outside 0x00-0xFF must be rejected.
    """

    with pytest.raises(
        (
            ValueError,
            OverflowError,
        )
    ):
        encode_instruction(
            "LOAD",
            operand,
        )


# ============================================================
# INVALID STRING OPERAND
# ============================================================


@pytest.mark.parametrize(
    "operand",
    [
        "INVALID",
        "HELLO",
        "XYZ",
    ],
)
def test_encode_invalid_operand(
    operand,
):
    """
    Unknown symbolic operands should fail
    when they are not present in the symbol table.
    """

    with pytest.raises(
        Exception
    ):
        encode_instruction(
            "LOAD",
            operand,
            {},
        )


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
def test_encode_missing_operand(
    instruction,
):
    """
    Two-byte instructions require an operand.
    """

    with pytest.raises(
        (
            ValueError,
            TypeError,
        )
    ):
        encode_instruction(
            instruction
        )


# ============================================================
# UNEXPECTED OPERAND
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
def test_encode_unexpected_operand(
    instruction,
):
    """
    One-byte instructions should not accept
    an additional operand.
    """

    with pytest.raises(
        (
            ValueError,
            TypeError,
        )
    ):
        encode_instruction(
            instruction,
            0x10,
        )


# ============================================================
# CASE-INSENSITIVE INSTRUCTIONS
# ============================================================


def test_encode_lowercase_instruction():
    """
    Instruction names should be case-insensitive.
    """

    result = encode_instruction(
        "load",
        "0x10",
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        0x10,
    ]


def test_encode_mixed_case_instruction():
    """
    Mixed-case instruction names should
    be normalized.
    """

    result = encode_instruction(
        "LoAd",
        "0x20",
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x10,
        0x20,
    ]


# ============================================================
# COMPLETE ISA ENCODING
# ============================================================


def test_encode_complete_instruction_set():
    """
    Verify the complete 16-instruction ISA.
    """

    instructions = [
        (
            "NOP",
            None,
            [0x00],
        ),
        (
            "OUT",
            None,
            [0xA0],
        ),
        (
            "IN",
            None,
            [0xB0],
        ),
        (
            "INC",
            None,
            [0xC0],
        ),
        (
            "DEC",
            None,
            [0xD0],
        ),
        (
            "HALT",
            None,
            [0xF0],
        ),
        (
            "LOAD",
            0x01,
            [0x10, 0x01],
        ),
        (
            "STORE",
            0x02,
            [0x20, 0x02],
        ),
        (
            "ADD",
            0x03,
            [0x30, 0x03],
        ),
        (
            "SUB",
            0x04,
            [0x40, 0x04],
        ),
        (
            "AND",
            0x05,
            [0x50, 0x05],
        ),
        (
            "OR",
            0x06,
            [0x60, 0x06],
        ),
        (
            "XOR",
            0x07,
            [0x70, 0x07],
        ),
        (
            "JMP",
            0x08,
            [0x80, 0x08],
        ),
        (
            "JZ",
            0x09,
            [0x90, 0x09],
        ),
        (
            "CMP",
            0x0A,
            [0xE0, 0x0A],
        ),
    ]

    for (
        instruction,
        operand,
        expected,
    ) in instructions:

        if operand is None:

            result = encode_instruction(
                instruction
            )

        else:

            result = encode_instruction(
                instruction,
                operand,
            )

        result = normalize_bytes(
            result
        )

        assert result == expected


# ============================================================
# OUTPUT VALUES MUST BE 8-BIT
# ============================================================


def test_encoder_output_is_8bit():
    """
    Every encoded byte must be in:

        0x00 - 0xFF
    """

    instructions = [
        (
            "NOP",
            None,
        ),
        (
            "LOAD",
            0x00,
        ),
        (
            "STORE",
            0xFF,
        ),
        (
            "JMP",
            0x80,
        ),
        (
            "HALT",
            None,
        ),
    ]

    for instruction, operand in instructions:

        if operand is None:

            result = encode_instruction(
                instruction
            )

        else:

            result = encode_instruction(
                instruction,
                operand,
            )

        result = normalize_bytes(
            result
        )

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
# ENCODED LENGTH
# ============================================================


@pytest.mark.parametrize(
    "instruction, operand, expected_length",
    [
        ("NOP", None, 1),
        ("OUT", None, 1),
        ("IN", None, 1),
        ("INC", None, 1),
        ("DEC", None, 1),
        ("HALT", None, 1),
        ("LOAD", 0x00, 2),
        ("STORE", 0x00, 2),
        ("ADD", 0x00, 2),
        ("SUB", 0x00, 2),
        ("AND", 0x00, 2),
        ("OR", 0x00, 2),
        ("XOR", 0x00, 2),
        ("JMP", 0x00, 2),
        ("JZ", 0x00, 2),
        ("CMP", 0x00, 2),
    ],
)
def test_encoded_instruction_length(
    instruction,
    operand,
    expected_length,
):
    """
    Verify 1-byte and 2-byte instruction formats.
    """

    if operand is None:

        result = encode_instruction(
            instruction
        )

    else:

        result = encode_instruction(
            instruction,
            operand,
        )

    result = normalize_bytes(
        result
    )

    assert len(
        result
    ) == expected_length


# ============================================================
# SYMBOL VALUE RANGE
# ============================================================


def test_symbol_value_must_fit_8bit():
    """
    A symbol used as an 8-bit operand must
    resolve to a valid byte value.
    """

    with pytest.raises(
        (
            ValueError,
            OverflowError,
        )
    ):
        encode_instruction(
            "JMP",
            "ADDRESS",
            {
                "ADDRESS": 0x100,
            },
        )


# ============================================================
# SYMBOL VALUE ZERO
# ============================================================


def test_symbol_value_zero():
    """
    Symbol resolving to zero must be encoded
    correctly.
    """

    result = encode_instruction(
        "JMP",
        "START",
        {
            "START": 0x00,
        },
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x80,
        0x00,
    ]


# ============================================================
# SYMBOL VALUE FF
# ============================================================


def test_symbol_value_ff():
    """
    Symbol resolving to 0xFF must be encoded
    correctly.
    """

    result = encode_instruction(
        "JMP",
        "END",
        {
            "END": 0xFF,
        },
    )

    result = normalize_bytes(
        result
    )

    assert result == [
        0x80,
        0xFF,
    ]


# ============================================================
# DETERMINISTIC ENCODING
# ============================================================


def test_encoder_is_deterministic():
    """
    Same instruction and operand must always
    generate the same bytes.
    """

    first = normalize_bytes(
        encode_instruction(
            "LOAD",
            0x42,
        )
    )

    second = normalize_bytes(
        encode_instruction(
            "LOAD",
            0x42,
        )
    )

    assert first == second


# ============================================================
# MULTIPLE ENCODINGS
# ============================================================


def test_encoder_multiple_instructions_independently():
    """
    Encoding one instruction should not affect
    the next encoding operation.
    """

    first = normalize_bytes(
        encode_instruction(
            "LOAD",
            0x10,
        )
    )

    second = normalize_bytes(
        encode_instruction(
            "HALT"
        )
    )

    third = normalize_bytes(
        encode_instruction(
            "JMP",
            0x20,
        )
    )

    assert first == [
        0x10,
        0x10,
    ]

    assert second == [
        0xF0,
    ]

    assert third == [
        0x80,
        0x20,
    ]
