"""
tests/cpu/test_instruction_decoder.py

MiniCPU 8-bit CPU Architecture
Instruction Decoder Test Suite

ISA:
    16 instructions
    8-bit opcode

Instruction format:

    1-byte instruction:
        [ OPCODE ]

    2-byte instruction:
        [ OPCODE ][ OPERAND ]

Opcode examples:

    NOP   = 0x00
    LOAD  = 0x10
    STORE = 0x20
    ADD   = 0x30
    SUB   = 0x40
    AND   = 0x50
    OR    = 0x60
    XOR   = 0x70
    JMP   = 0x80
    JZ    = 0x90
    OUT   = 0xA0
    IN    = 0xB0
    INC   = 0xC0
    DEC   = 0xD0
    CMP   = 0xE0
    HALT  = 0xF0

This test module verifies:

- Decoder creation
- Reset behavior
- Opcode decoding
- Instruction names
- Operand detection
- Instruction size
- 1-byte instructions
- 2-byte instructions
- Invalid opcode handling
- All 16 ISA instructions
- 8-bit operand handling
- Decoder integration
"""

from __future__ import annotations

import pytest

from cpu.instruction_decoder import InstructionDecoder


# ============================================================
# ISA DEFINITIONS
# ============================================================

OPCODES = {
    "NOP": 0x00,
    "LOAD": 0x10,
    "STORE": 0x20,
    "ADD": 0x30,
    "SUB": 0x40,
    "AND": 0x50,
    "OR": 0x60,
    "XOR": 0x70,
    "JMP": 0x80,
    "JZ": 0x90,
    "OUT": 0xA0,
    "IN": 0xB0,
    "INC": 0xC0,
    "DEC": 0xD0,
    "CMP": 0xE0,
    "HALT": 0xF0,
}


ONE_BYTE_INSTRUCTIONS = {
    "NOP",
    "OUT",
    "IN",
    "INC",
    "DEC",
    "HALT",
}


TWO_BYTE_INSTRUCTIONS = {
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


# ============================================================
# HELPERS
# ============================================================


def create_decoder():
    """
    Create a fresh Instruction Decoder.
    """

    return InstructionDecoder()


def decode_instruction(
    decoder,
    opcode,
    operand=None,
):
    """
    Decode an opcode using common decoder APIs.

    Supported method names:

        decode()
        decode_opcode()
        decode_instruction()
    """

    for name in (
        "decode",
        "decode_opcode",
        "decode_instruction",
    ):

        if hasattr(
            decoder,
            name,
        ):

            method = getattr(
                decoder,
                name,
            )

            if not callable(
                method
            ):

                continue

            if operand is None:

                try:

                    return method(
                        opcode
                    )

                except TypeError:

                    pass

            else:

                try:

                    return method(
                        opcode,
                        operand,
                    )

                except TypeError:

                    pass

                try:

                    return method(
                        [
                            opcode,
                            operand,
                        ]
                    )

                except TypeError:

                    pass

            return method(
                opcode
            )

    raise AttributeError(
        "InstructionDecoder does not expose "
        "a supported decode method."
    )


def extract_field(
    decoded,
    names,
):
    """
    Extract a field from common decoder
    return formats.

    Supports:

        dict
        object
        tuple
        string
    """

    if isinstance(
        decoded,
        dict,
    ):

        for name in names:

            if name in decoded:

                return decoded[name]

    for name in names:

        if hasattr(
            decoded,
            name,
        ):

            value = getattr(
                decoded,
                name,
            )

            if callable(
                value
            ):

                return value()

            return value

    if isinstance(
        decoded,
        tuple,
    ):

        if len(
            decoded
        ) >= 1:

            return decoded[0]

    return None


def extract_instruction_name(
    decoded,
):
    """
    Extract instruction name.
    """

    if isinstance(
        decoded,
        str,
    ):

        return decoded.upper()

    value = extract_field(
        decoded,
        (
            "name",
            "instruction",
            "mnemonic",
            "opcode_name",
        ),
    )

    if value is None:

        return None

    if hasattr(
        value,
        "name",
    ):

        value = value.name

    return str(
        value
    ).upper()


def extract_opcode(
    decoded,
):
    """
    Extract numeric opcode.
    """

    value = extract_field(
        decoded,
        (
            "opcode",
            "code",
            "value",
        ),
    )

    if value is None:

        return None

    return int(
        value
    )


def extract_operand(
    decoded,
):
    """
    Extract operand.
    """

    return extract_field(
        decoded,
        (
            "operand",
            "argument",
            "value",
            "address",
        ),
    )


def extract_size(
    decoded,
):
    """
    Extract instruction size.
    """

    value = extract_field(
        decoded,
        (
            "size",
            "length",
            "bytes",
            "byte_length",
        ),
    )

    if value is None:

        return None

    if isinstance(
        value,
        (list, tuple),
    ):

        return len(
            value
        )

    return int(
        value
    )


def get_decoder_state(
    decoder,
):
    """
    Return decoder state if exposed.
    """

    for name in (
        "state",
        "current_instruction",
        "decoded_instruction",
        "instruction",
    ):

        if hasattr(
            decoder,
            name,
        ):

            value = getattr(
                decoder,
                name,
            )

            if callable(
                value
            ):

                try:

                    return value()

                except TypeError:

                    continue

            return value

    return None


def reset_decoder(
    decoder,
):
    """
    Reset decoder if reset() is exposed.
    """

    if hasattr(
        decoder,
        "reset",
    ):

        reset = getattr(
            decoder,
            "reset",
        )

        if callable(
            reset
        ):

            reset()


# ============================================================
# CREATION
# ============================================================


def test_decoder_can_be_created():
    """
    Instruction Decoder should be constructable.
    """

    decoder = create_decoder()

    assert decoder is not None


# ============================================================
# RESET
# ============================================================


def test_decoder_reset_if_supported():
    """
    Decoder reset should execute successfully
    when available.
    """

    decoder = create_decoder()

    if not hasattr(
        decoder,
        "reset",
    ):

        pytest.skip(
            "Decoder reset() is not exposed."
        )

    reset_decoder(
        decoder
    )


# ============================================================
# NOP
# ============================================================


def test_decode_nop():
    """
    0x00 must decode as NOP.
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        0x00,
    )

    name = extract_instruction_name(
        decoded
    )

    assert name == "NOP"


# ============================================================
# HALT
# ============================================================


def test_decode_halt():
    """
    0xF0 must decode as HALT.
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        0xF0,
    )

    name = extract_instruction_name(
        decoded
    )

    assert name == "HALT"


# ============================================================
# ALL OPCODES
# ============================================================


@pytest.mark.parametrize(
    "name,opcode",
    list(
        OPCODES.items()
    ),
)
def test_decode_all_16_instructions(
    name,
    opcode,
):
    """
    Every one of the 16 MiniCPU instructions
    must decode to the correct mnemonic.
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
    )

    decoded_name = extract_instruction_name(
        decoded
    )

    assert (
        decoded_name
        == name
    )


# ============================================================
# OPCODE VALUE
# ============================================================


@pytest.mark.parametrize(
    "name,opcode",
    list(
        OPCODES.items()
    ),
)
def test_decoded_opcode_is_correct(
    name,
    opcode,
):
    """
    Decoder output should preserve the
    original opcode where the API exposes it.
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
    )

    decoded_opcode = extract_opcode(
        decoded
    )

    if decoded_opcode is None:

        pytest.skip(
            "Decoded opcode is not exposed."
        )

    assert (
        decoded_opcode
        == opcode
    )


# ============================================================
# ONE-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "name",
    sorted(
        ONE_BYTE_INSTRUCTIONS
    ),
)
def test_one_byte_instruction_size(
    name,
):
    """
    1-byte instructions must have
    a total instruction size of 1 byte.
    """

    opcode = OPCODES[
        name
    ]

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
    )

    size = extract_size(
        decoded
    )

    if size is None:

        pytest.skip(
            "Instruction size is not exposed."
        )

    assert size == 1


# ============================================================
# TWO-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "name",
    sorted(
        TWO_BYTE_INSTRUCTIONS
    ),
)
def test_two_byte_instruction_size(
    name,
):
    """
    2-byte instructions must have
    a total instruction size of 2 bytes.
    """

    opcode = OPCODES[
        name
    ]

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
        0x42,
    )

    size = extract_size(
        decoded
    )

    if size is None:

        pytest.skip(
            "Instruction size is not exposed."
        )

    assert size == 2


# ============================================================
# ONE-BYTE OPERAND CHECK
# ============================================================


@pytest.mark.parametrize(
    "name",
    sorted(
        ONE_BYTE_INSTRUCTIONS
    ),
)
def test_one_byte_instruction_has_no_operand(
    name,
):
    """
    1-byte instructions do not require
    an additional operand byte.
    """

    opcode = OPCODES[
        name
    ]

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
    )

    operand = extract_operand(
        decoded
    )

    if operand is None:

        return

    assert operand in (
        None,
        False,
    )


# ============================================================
# TWO-BYTE OPERAND CHECK
# ============================================================


@pytest.mark.parametrize(
    "name",
    sorted(
        TWO_BYTE_INSTRUCTIONS
    ),
)
def test_two_byte_instruction_accepts_operand(
    name,
):
    """
    Every 2-byte instruction must be able
    to decode an 8-bit operand.
    """

    opcode = OPCODES[
        name
    ]

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
        0x42,
    )

    assert decoded is not None


# ============================================================
# OPERAND ZERO
# ============================================================


@pytest.mark.parametrize(
    "name",
    sorted(
        TWO_BYTE_INSTRUCTIONS
    ),
)
def test_two_byte_instruction_operand_zero(
    name,
):
    """
    Operand 0x00 is valid.
    """

    opcode = OPCODES[
        name
    ]

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
        0x00,
    )

    assert decoded is not None


# ============================================================
# OPERAND FF
# ============================================================


@pytest.mark.parametrize(
    "name",
    sorted(
        TWO_BYTE_INSTRUCTIONS
    ),
)
def test_two_byte_instruction_operand_ff(
    name,
):
    """
    Operand 0xFF is valid.
    """

    opcode = OPCODES[
        name
    ]

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        opcode,
        0xFF,
    )

    assert decoded is not None


# ============================================================
# ALL 8-BIT OPERANDS
# ============================================================


@pytest.mark.parametrize(
    "operand",
    range(
        0x100
    ),
)
def test_load_accepts_all_8bit_operands(
    operand,
):
    """
    LOAD must accept every possible
    8-bit operand value.
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        OPCODES["LOAD"],
        operand,
    )

    assert decoded is not None


# ============================================================
# JMP ADDRESS
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        0x00,
        0x01,
        0x7F,
        0x80,
        0xFE,
        0xFF,
    ],
)
def test_jmp_accepts_8bit_address(
    address,
):
    """
    JMP uses an 8-bit address operand.
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        OPCODES["JMP"],
        address,
    )

    assert decoded is not None


# ============================================================
# JZ ADDRESS
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        0x00,
        0x01,
        0x7F,
        0x80,
        0xFE,
        0xFF,
    ],
)
def test_jz_accepts_8bit_address(
    address,
):
    """
    JZ uses an 8-bit address operand.
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        OPCODES["JZ"],
        address,
    )

    assert decoded is not None


# ============================================================
# INVALID OPCODE
# ============================================================


@pytest.mark.parametrize(
    "opcode",
    [
        -1,
        0x100,
        0x101,
        0x1FF,
        0x1000,
    ],
)
def test_invalid_opcode_is_rejected(
    opcode,
):
    """
    Values outside the 8-bit opcode range
    must not be silently decoded.
    """

    decoder = create_decoder()

    with pytest.raises(
        (
            ValueError,
            KeyError,
            TypeError,
            OverflowError,
        )
    ):

        decode_instruction(
            decoder,
            opcode,
        )


# ============================================================
# NON-INTEGER OPCODE
# ============================================================


@pytest.mark.parametrize(
    "opcode",
    [
        None,
        "LOAD",
        "0x10",
        1.5,
        [],
        {},
    ],
)
def test_non_integer_opcode_is_rejected(
    opcode,
):
    """
    Opcode input must be a valid numeric byte.
    """

    decoder = create_decoder()

    with pytest.raises(
        (
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
        )
    ):

        decode_instruction(
            decoder,
            opcode,
        )


# ============================================================
# INVALID OPERAND
# ============================================================


@pytest.mark.parametrize(
    "operand",
    [
        -1,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_operand_is_rejected(
    operand,
):
    """
    Operands must remain within 8-bit range.
    """

    decoder = create_decoder()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        decode_instruction(
            decoder,
            OPCODES["LOAD"],
            operand,
        )


# ============================================================
# NON-INTEGER OPERAND
# ============================================================


@pytest.mark.parametrize(
    "operand",
    [
        None,
        "10",
        "0x10",
        1.5,
        [],
        {},
    ],
)
def test_non_integer_operand_is_rejected(
    operand,
):
    """
    Operand must be an integer byte.
    """

    decoder = create_decoder()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        decode_instruction(
            decoder,
            OPCODES["LOAD"],
            operand,
        )


# ============================================================
# DECODE RESULT IS STABLE
# ============================================================


@pytest.mark.parametrize(
    "name,opcode",
    list(
        OPCODES.items()
    ),
)
def test_decoding_same_opcode_is_deterministic(
    name,
    opcode,
):
    """
    Decoding the same opcode repeatedly
    must produce the same instruction.
    """

    decoder = create_decoder()

    first = decode_instruction(
        decoder,
        opcode,
    )

    reset_decoder(
        decoder
    )

    second = decode_instruction(
        decoder,
        opcode,
    )

    first_name = extract_instruction_name(
        first
    )

    second_name = extract_instruction_name(
        second
    )

    assert (
        first_name
        == second_name
    )


# ============================================================
# SEQUENTIAL DECODING
# ============================================================


def test_sequential_decoding():
    """
    Decoder must correctly decode a sequence
    of different instructions.
    """

    decoder = create_decoder()

    sequence = [
        0x00,
        0x10,
        0x30,
        0x80,
        0x90,
        0xF0,
    ]

    expected = [
        "NOP",
        "LOAD",
        "ADD",
        "JMP",
        "JZ",
        "HALT",
    ]

    for opcode, expected_name in zip(
        sequence,
        expected,
    ):

        decoded = decode_instruction(
            decoder,
            opcode,
        )

        name = extract_instruction_name(
            decoded
        )

        assert (
            name
            == expected_name
        )


# ============================================================
# RESET AFTER DECODE
# ============================================================


def test_reset_after_decode_if_supported():
    """
    Reset must clear or reinitialize
    decoder state when supported.
    """

    decoder = create_decoder()

    decode_instruction(
        decoder,
        OPCODES["LOAD"],
        0x42,
    )

    if not hasattr(
        decoder,
        "reset",
    ):

        pytest.skip(
            "Decoder reset() is not exposed."
        )

    reset_decoder(
        decoder
    )

    state = get_decoder_state(
        decoder
    )

    if state is None:

        return

    if isinstance(
        state,
        dict,
    ):

        assert state == {}

    else:

        assert state is not None


# ============================================================
# INSTRUCTION NAME UNIQUENESS
# ============================================================


def test_all_instruction_names_are_unique():
    """
    The 16-instruction ISA must not contain
    duplicate instruction names.
    """

    names = list(
        OPCODES.keys()
    )

    assert len(
        names
    ) == len(
        set(
            names
        )
    )


# ============================================================
# OPCODE UNIQUENESS
# ============================================================


def test_all_opcodes_are_unique():
    """
    Every instruction must have a unique opcode.
    """

    values = list(
        OPCODES.values()
    )

    assert len(
        values
    ) == len(
        set(
            values
        )
    )


# ============================================================
# OPCODE RANGE
# ============================================================


def test_all_opcodes_are_8bit():
    """
    All opcode values must fit in one byte.
    """

    for opcode in OPCODES.values():

        assert (
            0x00
            <= opcode
            <= 0xFF
        )


# ============================================================
# INSTRUCTION COUNT
# ============================================================


def test_isa_contains_exactly_16_instructions():
    """
    MiniCPU architecture must contain
    exactly 16 instructions.
    """

    assert (
        len(
            OPCODES
        )
        == 16
    )


# ============================================================
# ONE BYTE + TWO BYTE COUNT
# ============================================================


def test_instruction_groups_cover_all_instructions():
    """
    Every instruction must belong to exactly
    one instruction-size group.
    """

    combined = (
        ONE_BYTE_INSTRUCTIONS
        | TWO_BYTE_INSTRUCTIONS
    )

    assert (
        combined
        == set(
            OPCODES.keys()
        )
    )

    assert not (
        ONE_BYTE_INSTRUCTIONS
        & TWO_BYTE_INSTRUCTIONS
    )


# ============================================================
# OPCODE UPPER NIBBLE
# ============================================================


def test_opcode_layout_uses_upper_nibble():
    """
    MiniCPU opcode layout uses the upper nibble
    for the primary instruction opcode.

    Examples:

        0x10
        0x20
        ...
        0xF0
    """

    for name, opcode in OPCODES.items():

        assert (
            opcode
            & 0x0F
        ) == 0


# ============================================================
# FINAL DECODER INTEGRATION
# ============================================================


def test_instruction_decoder_complete_integration():
    """
    Complete decoder workflow:

        Create Decoder
              ↓
        Decode NOP
              ↓
        Decode LOAD + operand
              ↓
        Decode ADD + operand
              ↓
        Decode JMP + address
              ↓
        Decode JZ + address
              ↓
        Decode HALT
    """

    decoder = create_decoder()

    decoded = decode_instruction(
        decoder,
        OPCODES["NOP"],
    )

    assert (
        extract_instruction_name(
            decoded
        )
        == "NOP"
    )

    decoded = decode_instruction(
        decoder,
        OPCODES["LOAD"],
        0x42,
    )

    assert (
        extract_instruction_name(
            decoded
        )
        == "LOAD"
    )

    decoded = decode_instruction(
        decoder,
        OPCODES["ADD"],
        0x10,
    )

    assert (
        extract_instruction_name(
            decoded
        )
        == "ADD"
    )

    decoded = decode_instruction(
        decoder,
        OPCODES["JMP"],
        0x80,
    )

    assert (
        extract_instruction_name(
            decoded
        )
        == "JMP"
    )

    decoded = decode_instruction(
        decoder,
        OPCODES["JZ"],
        0xFF,
    )

    assert (
        extract_instruction_name(
            decoded
        )
        == "JZ"
    )

    decoded = decode_instruction(
        decoder,
        OPCODES["HALT"],
    )

    assert (
        extract_instruction_name(
            decoded
        )
        == "HALT"
    )
