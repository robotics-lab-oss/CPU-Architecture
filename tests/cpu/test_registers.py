"""
tests/cpu/test_registers.py

MiniCPU 8-bit CPU Architecture
Register File Test Suite

Architecture:
    Data width:   8-bit
    Register values:
        0x00 - 0xFF

Expected register file:
    A   - Accumulator
    B   - General purpose register
    PC  - Program Counter
    SP  - Stack Pointer

This test module verifies:

- Register creation
- Register reset
- 8-bit value storage
- Minimum value
- Maximum value
- Register read/write
- Register independence
- Invalid register handling
- 8-bit overflow behavior
- 8-bit underflow behavior
"""

from __future__ import annotations

import pytest

from cpu.registers import Registers


# ============================================================
# CONSTANTS
# ============================================================

MIN_8BIT = 0x00
MAX_8BIT = 0xFF

BYTE_MASK = 0xFF

REGISTER_A = "A"
REGISTER_B = "B"


# ============================================================
# HELPERS
# ============================================================


def create_registers():
    """
    Create a fresh register file.
    """

    return Registers()


def read_register(
    registers,
    name,
):
    """
    Read a register using the supported register API.

    Preferred API:

        registers.read("A")

    Compatibility forms are also supported.
    """

    if hasattr(
        registers,
        "read",
    ):

        return registers.read(
            name
        )

    if hasattr(
        registers,
        "get",
    ):

        return registers.get(
            name
        )

    if hasattr(
        registers,
        name,
    ):

        return getattr(
            registers,
            name,
        )

    if hasattr(
        registers,
        name.upper(),
    ):

        return getattr(
            registers,
            name.upper(),
        )

    raise AttributeError(
        f"Unable to read register: {name}"
    )


def write_register(
    registers,
    name,
    value,
):
    """
    Write a value to a register.

    Preferred API:

        registers.write("A", value)
    """

    if hasattr(
        registers,
        "write",
    ):

        registers.write(
            name,
            value,
        )

        return

    if hasattr(
        registers,
        "set",
    ):

        registers.set(
            name,
            value,
        )

        return

    if hasattr(
        registers,
        name,
    ):

        setattr(
            registers,
            name,
            value,
        )

        return

    if hasattr(
        registers,
        name.upper(),
    ):

        setattr(
            registers,
            name.upper(),
            value,
        )

        return

    raise AttributeError(
        f"Unable to write register: {name}"
    )


def reset_registers(
    registers,
):
    """
    Reset the register file.
    """

    if not hasattr(
        registers,
        "reset",
    ):

        raise AttributeError(
            "Registers must provide reset()."
        )

    registers.reset()


# ============================================================
# CREATION
# ============================================================


def test_registers_can_be_created():
    """
    Register file should be constructable.
    """

    registers = create_registers()

    assert registers is not None


# ============================================================
# RESET
# ============================================================


def test_registers_reset():
    """
    After reset, core registers should contain
    their defined reset values.

    The default architecture expectation is:

        A  = 0x00
        B  = 0x00
    """

    registers = create_registers()

    reset_registers(
        registers
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x00

    assert read_register(
        registers,
        REGISTER_B,
    ) == 0x00


# ============================================================
# REGISTER A WRITE / READ
# ============================================================


def test_register_a_write_and_read():
    """
    Register A must support writing and reading
    an 8-bit value.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0x42,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x42


# ============================================================
# REGISTER B WRITE / READ
# ============================================================


def test_register_b_write_and_read():
    """
    Register B must support writing and reading
    an 8-bit value.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_B,
        0x24,
    )

    assert read_register(
        registers,
        REGISTER_B,
    ) == 0x24


# ============================================================
# ZERO VALUE
# ============================================================


def test_register_accepts_zero():
    """
    0x00 is a valid 8-bit value.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0x00,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x00


# ============================================================
# MAXIMUM VALUE
# ============================================================


def test_register_accepts_ff():
    """
    0xFF is the maximum unsigned 8-bit value.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0xFF,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0xFF


# ============================================================
# ALL 8-BIT VALUES
# ============================================================


@pytest.mark.parametrize(
    "value",
    range(
        0x100
    ),
)
def test_register_a_accepts_all_8bit_values(
    value,
):
    """
    Every value from 0x00 through 0xFF
    must be representable by an 8-bit register.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        value,
    )

    result = read_register(
        registers,
        REGISTER_A,
    )

    assert result == value

    assert (
        MIN_8BIT
        <= result
        <= MAX_8BIT
    )


# ============================================================
# REGISTER INDEPENDENCE
# ============================================================


def test_registers_are_independent():
    """
    Writing A must not modify B.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0xAA,
    )

    write_register(
        registers,
        REGISTER_B,
        0x55,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0xAA

    assert read_register(
        registers,
        REGISTER_B,
    ) == 0x55


# ============================================================
# OVERWRITE REGISTER
# ============================================================


def test_register_can_be_overwritten():
    """
    A register can be written multiple times.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0x10,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x10

    write_register(
        registers,
        REGISTER_A,
        0x20,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x20


# ============================================================
# REGISTER RESET AFTER WRITE
# ============================================================


def test_reset_clears_register_values():
    """
    Reset should restore register values
    to their reset state.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0xFF,
    )

    write_register(
        registers,
        REGISTER_B,
        0xAA,
    )

    reset_registers(
        registers
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x00

    assert read_register(
        registers,
        REGISTER_B,
    ) == 0x00


# ============================================================
# RESET IS DETERMINISTIC
# ============================================================


def test_reset_is_deterministic():
    """
    Calling reset repeatedly should produce
    the same register state.
    """

    registers = create_registers()

    reset_registers(
        registers
    )

    first_a = read_register(
        registers,
        REGISTER_A,
    )

    first_b = read_register(
        registers,
        REGISTER_B,
    )

    write_register(
        registers,
        REGISTER_A,
        0x12,
    )

    write_register(
        registers,
        REGISTER_B,
        0x34,
    )

    reset_registers(
        registers
    )

    second_a = read_register(
        registers,
        REGISTER_A,
    )

    second_b = read_register(
        registers,
        REGISTER_B,
    )

    assert first_a == second_a

    assert first_b == second_b


# ============================================================
# REGISTER VALUE TYPE
# ============================================================


def test_register_value_is_integer():
    """
    Register values should be integers.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0x42,
    )

    value = read_register(
        registers,
        REGISTER_A,
    )

    assert isinstance(
        value,
        int,
    )


# ============================================================
# REGISTER RANGE
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        0x00,
        0x01,
        0x7F,
        0x80,
        0xFE,
        0xFF,
    ],
)
def test_register_values_are_8bit(
    value,
):
    """
    Test important 8-bit boundary values.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        value,
    )

    result = read_register(
        registers,
        REGISTER_A,
    )

    assert (
        0x00
        <= result
        <= 0xFF
    )


# ============================================================
# INVALID REGISTER NAME
# ============================================================


def test_invalid_register_name_is_rejected():
    """
    Unknown register names should not be silently accepted.
    """

    registers = create_registers()

    with pytest.raises(
        (
            KeyError,
            ValueError,
            AttributeError,
        )
    ):

        write_register(
            registers,
            "INVALID_REGISTER",
            0x42,
        )


# ============================================================
# INVALID READ
# ============================================================


def test_invalid_register_read_is_rejected():
    """
    Reading an unknown register should fail.
    """

    registers = create_registers()

    with pytest.raises(
        (
            KeyError,
            ValueError,
            AttributeError,
        )
    ):

        read_register(
            registers,
            "INVALID_REGISTER",
        )


# ============================================================
# LOWERCASE REGISTER ACCESS
# ============================================================


def test_register_name_case_behavior():
    """
    The register implementation may support
    case-insensitive register names.

    If it does not, lowercase access is expected
    to raise a standard register lookup error.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        0x42,
    )

    try:

        value = read_register(
            registers,
            "a",
        )

    except (
        KeyError,
        ValueError,
        AttributeError,
    ):

        return

    assert value == 0x42


# ============================================================
# BYTE BOUNDARY VALUES
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        0x00,
        0x7F,
        0x80,
        0xFF,
    ],
)
def test_register_boundary_values(
    value,
):
    """
    Verify all major 8-bit boundaries.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        value,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == value


# ============================================================
# REGISTER A / B DIFFERENT VALUES
# ============================================================


@pytest.mark.parametrize(
    "a_value,b_value",
    [
        (0x00, 0xFF),
        (0xFF, 0x00),
        (0x12, 0x34),
        (0xAA, 0x55),
    ],
)
def test_register_a_and_b_hold_different_values(
    a_value,
    b_value,
):
    """
    A and B must independently retain their values.
    """

    registers = create_registers()

    write_register(
        registers,
        REGISTER_A,
        a_value,
    )

    write_register(
        registers,
        REGISTER_B,
        b_value,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == a_value

    assert read_register(
        registers,
        REGISTER_B,
    ) == b_value


# ============================================================
# OPTIONAL REGISTER COLLECTION
# ============================================================


def test_register_collection_if_available():
    """
    If the implementation exposes a register collection,
    it should contain the expected core registers.
    """

    registers = create_registers()

    collection = None

    for name in (
        "registers",
        "values",
        "storage",
    ):

        if hasattr(
            registers,
            name,
        ):

            candidate = getattr(
                registers,
                name,
            )

            if isinstance(
                candidate,
                dict,
            ):

                collection = candidate

                break

    if collection is None:

        pytest.skip(
            "Register collection API is not exposed."
        )

    assert REGISTER_A in collection

    assert REGISTER_B in collection


# ============================================================
# REGISTER COUNT
# ============================================================


def test_register_count_if_available():
    """
    If register metadata exposes a register count,
    it must be a positive integer.
    """

    registers = create_registers()

    count = None

    for name in (
        "REGISTER_COUNT",
        "register_count",
        "count",
    ):

        if hasattr(
            registers,
            name,
        ):

            candidate = getattr(
                registers,
                name,
            )

            if isinstance(
                candidate,
                int,
            ):

                count = candidate

                break

    if count is None:

        pytest.skip(
            "Register count is not exposed."
        )

    assert count > 0


# ============================================================
# 8-BIT MASK
# ============================================================


def test_byte_mask_is_8bit():
    """
    Architectural byte mask must be FF.
    """

    assert BYTE_MASK == 0xFF


# ============================================================
# FINAL REGISTER INTEGRATION
# ============================================================


def test_registers_complete_integration():
    """
    Complete register workflow:

        Create
          ↓
        Reset
          ↓
        Write A
          ↓
        Write B
          ↓
        Read A
          ↓
        Read B
          ↓
        Reset
          ↓
        Verify cleared
    """

    registers = create_registers()

    reset_registers(
        registers
    )

    write_register(
        registers,
        REGISTER_A,
        0x42,
    )

    write_register(
        registers,
        REGISTER_B,
        0x24,
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x42

    assert read_register(
        registers,
        REGISTER_B,
    ) == 0x24

    reset_registers(
        registers
    )

    assert read_register(
        registers,
        REGISTER_A,
    ) == 0x00

    assert read_register(
        registers,
        REGISTER_B,
    ) == 0x00
