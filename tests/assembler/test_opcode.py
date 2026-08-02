"""
test_opcode.py

MiniCPU 8-bit CPU Architecture
16-Instruction Opcode Tests

Tests:
    - Exactly 16 instructions
    - Opcode uniqueness
    - 8-bit opcode range
    - One-byte instructions
    - Two-byte instructions
    - Instruction sizes
    - Operand requirements
    - Opcode lookup
    - Instruction normalization
    - Instruction metadata
    - ISA validation
"""

from __future__ import annotations

import pytest

from assembler.opcode import (
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
    validate_opcodes,
)


# ============================================================
# EXPECTED 16-INSTRUCTION ISA
# ============================================================

EXPECTED_OPCODES = {
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


EXPECTED_ONE_BYTE = {
    "NOP",
    "OUT",
    "IN",
    "INC",
    "DEC",
    "HALT",
}


EXPECTED_TWO_BYTE = {
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
# INSTRUCTION COUNT
# ============================================================


def test_instruction_count():
    """
    MiniCPU must contain exactly 16 instructions.
    """

    assert INSTRUCTION_COUNT == 16

    assert len(
        OPCODES
    ) == 16


# ============================================================
# OPCODE TABLE
# ============================================================


def test_expected_opcodes():
    """
    Verify complete opcode mapping.
    """

    assert OPCODES == EXPECTED_OPCODES


# ============================================================
# OPCODE UNIQUENESS
# ============================================================


def test_opcodes_are_unique():
    """
    Every instruction must have a unique opcode.
    """

    values = list(
        OPCODES.values()
    )

    assert len(
        values
    ) == len(
        set(values)
    )


# ============================================================
# OPCODE RANGE
# ============================================================


def test_opcodes_are_8bit():
    """
    Every opcode must fit in one byte.
    """

    for name, opcode in OPCODES.items():

        assert isinstance(
            opcode,
            int,
        )

        assert 0x00 <= opcode <= 0xFF


# ============================================================
# ONE-BYTE INSTRUCTIONS
# ============================================================


def test_one_byte_instruction_set():
    """
    Verify all one-byte instructions.
    """

    assert (
        ONE_BYTE_INSTRUCTIONS
        == EXPECTED_ONE_BYTE
    )


def test_one_byte_instruction_sizes():
    """
    One-byte instructions must have size 1.
    """

    for instruction in EXPECTED_ONE_BYTE:

        assert (
            get_instruction_size(
                instruction
            )
            == 1
        )


# ============================================================
# TWO-BYTE INSTRUCTIONS
# ============================================================


def test_two_byte_instruction_set():
    """
    Verify all two-byte instructions.
    """

    assert (
        TWO_BYTE_INSTRUCTIONS
        == EXPECTED_TWO_BYTE
    )


def test_two_byte_instruction_sizes():
    """
    Two-byte instructions must have size 2.
    """

    for instruction in EXPECTED_TWO_BYTE:

        assert (
            get_instruction_size(
                instruction
            )
            == 2
        )


# ============================================================
# INSTRUCTION GROUPS
# ============================================================


def test_instruction_groups_are_complete():
    """
    Every instruction must belong to exactly
    one instruction-size group.
    """

    combined = (
        ONE_BYTE_INSTRUCTIONS
        | TWO_BYTE_INSTRUCTIONS
    )

    assert combined == set(
        OPCODES.keys()
    )


def test_instruction_groups_do_not_overlap():
    """
    An instruction cannot be both one-byte
    and two-byte.
    """

    assert not (
        ONE_BYTE_INSTRUCTIONS
        & TWO_BYTE_INSTRUCTIONS
    )


# ============================================================
# OPERAND INSTRUCTIONS
# ============================================================


def test_operand_instructions_match_two_byte():
    """
    Operand instructions must match the
    two-byte instruction set.
    """

    assert (
        OPERAND_INSTRUCTIONS
        == TWO_BYTE_INSTRUCTIONS
    )


def test_one_byte_instructions_do_not_require_operand():
    """
    One-byte instructions do not require
    a second byte.
    """

    for instruction in EXPECTED_ONE_BYTE:

        assert (
            requires_operand(
                instruction
            )
            is False
        )


def test_two_byte_instructions_require_operand():
    """
    Two-byte instructions require
    a second operand byte.
    """

    for instruction in EXPECTED_TWO_BYTE:

        assert (
            requires_operand(
                instruction
            )
            is True
        )


# ============================================================
# INSTRUCTION SIZES
# ============================================================


def test_instruction_sizes_complete():
    """
    Every instruction must have a size entry.
    """

    assert set(
        INSTRUCTION_SIZES.keys()
    ) == set(
        OPCODES.keys()
    )


def test_instruction_sizes_are_valid():
    """
    Instruction sizes can only be 1 or 2.
    """

    for size in (
        INSTRUCTION_SIZES.values()
    ):

        assert size in {
            1,
            2,
        }


# ============================================================
# NORMALIZATION
# ============================================================


@pytest.mark.parametrize(
    "source, expected",
    [
        ("NOP", "NOP"),
        ("nop", "NOP"),
        ("Nop", "NOP"),
        (" nOp ", "NOP"),
        ("LOAD", "LOAD"),
        ("load", "LOAD"),
        ("LoAd", "LOAD"),
        (" halt ", "HALT"),
    ],
)
def test_normalize_instruction(
    source: str,
    expected: str,
):
    """
    Instruction names should normalize
    to uppercase.
    """

    assert (
        normalize_instruction(
            source
        )
        == expected
    )


def test_normalize_instruction_non_string():
    """
    Non-string instruction names should
    raise TypeError.
    """

    with pytest.raises(
        TypeError
    ):
        normalize_instruction(
            123
        )


# ============================================================
# VALID INSTRUCTION
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
def test_valid_instructions(
    instruction: str,
):
    """
    All 16 instructions must be valid.
    """

    assert (
        is_valid_instruction(
            instruction
        )
        is True
    )


def test_invalid_instruction():
    """
    Unknown instruction must be invalid.
    """

    assert (
        is_valid_instruction(
            "UNKNOWN"
        )
        is False
    )


def test_invalid_instruction_empty():
    """
    Empty instruction must be invalid.
    """

    assert (
        is_valid_instruction(
            ""
        )
        is False
    )


def test_valid_instruction_case_insensitive():
    """
    Instruction validation should support
    case-insensitive names.
    """

    assert is_valid_instruction(
        "nop"
    )

    assert is_valid_instruction(
        "Load"
    )

    assert is_valid_instruction(
        "hAlT"
    )


# ============================================================
# OPCODE LOOKUP
# ============================================================


@pytest.mark.parametrize(
    "instruction, expected_opcode",
    EXPECTED_OPCODES.items(),
)
def test_get_opcode(
    instruction: str,
    expected_opcode: int,
):
    """
    Verify opcode lookup for every instruction.
    """

    assert (
        get_opcode(
            instruction
        )
        == expected_opcode
    )


def test_get_opcode_case_insensitive():
    """
    Opcode lookup should be case-insensitive.
    """

    assert (
        get_opcode(
            "load"
        )
        == 0x10
    )

    assert (
        get_opcode(
            "LoAd"
        )
        == 0x10
    )


def test_get_opcode_unknown_instruction():
    """
    Unknown instruction must raise ValueError.
    """

    with pytest.raises(
        ValueError
    ):
        get_opcode(
            "UNKNOWN"
        )


# ============================================================
# INSTRUCTION SIZE LOOKUP
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    EXPECTED_ONE_BYTE,
)
def test_get_size_one_byte(
    instruction: str,
):
    """
    Verify one-byte instruction sizes.
    """

    assert (
        get_instruction_size(
            instruction
        )
        == 1
    )


@pytest.mark.parametrize(
    "instruction",
    EXPECTED_TWO_BYTE,
)
def test_get_size_two_byte(
    instruction: str,
):
    """
    Verify two-byte instruction sizes.
    """

    assert (
        get_instruction_size(
            instruction
        )
        == 2
    )


def test_get_instruction_size_unknown():
    """
    Unknown instruction size lookup
    must raise ValueError.
    """

    with pytest.raises(
        ValueError
    ):
        get_instruction_size(
            "UNKNOWN"
        )


# ============================================================
# OPERAND REQUIREMENT
# ============================================================


def test_requires_operand_for_all_instructions():
    """
    Verify operand requirement for the
    complete ISA.
    """

    for instruction in OPCODES:

        expected = (
            instruction
            in EXPECTED_TWO_BYTE
        )

        assert (
            requires_operand(
                instruction
            )
            == expected
        )


def test_requires_operand_unknown():
    """
    Unknown instructions do not silently
    become valid operand instructions.
    """

    assert (
        requires_operand(
            "UNKNOWN"
        )
        is False
    )


# ============================================================
# INSTRUCTION INFO
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    OPCODES.keys(),
)
def test_instruction_info(
    instruction: str,
):
    """
    Every instruction must return complete
    metadata.
    """

    info = get_instruction_info(
        instruction
    )

    assert isinstance(
        info,
        dict,
    )

    assert (
        info["name"]
        == instruction
    )

    assert (
        info["opcode"]
        == OPCODES[instruction]
    )

    assert (
        info["size"]
        == INSTRUCTION_SIZES[
            instruction
        ]
    )

    assert (
        info["requires_operand"]
        == (
            instruction
            in OPERAND_INSTRUCTIONS
        )
    )


def test_instruction_info_load():
    """
    Verify LOAD metadata.
    """

    info = get_instruction_info(
        "LOAD"
    )

    assert info == {
        "name": "LOAD",
        "opcode": 0x10,
        "size": 2,
        "requires_operand": True,
    }


def test_instruction_info_nop():
    """
    Verify NOP metadata.
    """

    info = get_instruction_info(
        "NOP"
    )

    assert info == {
        "name": "NOP",
        "opcode": 0x00,
        "size": 1,
        "requires_operand": False,
    }


def test_instruction_info_unknown():
    """
    Unknown instruction metadata lookup
    must raise ValueError.
    """

    with pytest.raises(
        ValueError
    ):
        get_instruction_info(
            "UNKNOWN"
        )


# ============================================================
# ISA OPCODE PATTERN
# ============================================================


def test_opcode_upper_nibble_layout():
    """
    Current ISA uses the upper nibble
    as the instruction group.

    Expected:

        NOP   = 0x00
        LOAD  = 0x10
        STORE = 0x20
        ...
        HALT  = 0xF0
    """

    for instruction, opcode in (
        EXPECTED_OPCODES.items()
    ):

        expected_group = (
            list(
                EXPECTED_OPCODES
            ).index(
                instruction
            )
        )

        assert (
            opcode
            == (
                expected_group
                << 4
            )
        )


# ============================================================
# OPCODE LOWER NIBBLE
# ============================================================


def test_opcode_lower_nibble_reserved():
    """
    Current ISA definition uses the lower
    nibble as reserved.

    Therefore all current opcodes should
    have lower nibble 0.
    """

    for opcode in OPCODES.values():

        assert (
            opcode & 0x0F
        ) == 0


# ============================================================
# VALIDATE OPCODES
# ============================================================


def test_validate_opcodes():
    """
    Complete ISA validation should pass.
    """

    result = validate_opcodes()

    assert result is None


# ============================================================
# IMMUTABILITY / CONSISTENCY CHECK
# ============================================================


def test_opcode_count_matches_groups():
    """
    One-byte + two-byte instructions must
    equal total instruction count.
    """

    assert (
        len(
            ONE_BYTE_INSTRUCTIONS
        )
        + len(
            TWO_BYTE_INSTRUCTIONS
        )
        == INSTRUCTION_COUNT
    )


def test_operand_count():
    """
    There should be 10 operand instructions
    in the current ISA.
    """

    assert (
        len(
            OPERAND_INSTRUCTIONS
        )
        == 10
    )


def test_one_byte_count():
    """
    There should be 6 one-byte instructions.
    """

    assert (
        len(
            ONE_BYTE_INSTRUCTIONS
        )
        == 6
    )


def test_two_byte_count():
    """
    There should be 10 two-byte instructions.
    """

    assert (
        len(
            TWO_BYTE_INSTRUCTIONS
        )
        == 10
    )
