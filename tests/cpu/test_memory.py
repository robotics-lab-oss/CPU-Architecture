"""
tests/cpu/test_memory.py

MiniCPU 8-bit CPU Architecture
Memory Test Suite

Memory model:

    Address width : 8-bit
    Address range : 0x00 - 0xFF
    Capacity      : 256 bytes
    Data width    : 8-bit

This test module verifies:

- Memory creation
- Default size
- Reset behavior
- Read operation
- Write operation
- All 256 addresses
- 8-bit data values
- Address boundary behavior
- Invalid addresses
- Invalid data
- Memory isolation
- Sequential read/write
"""

from __future__ import annotations

import pytest

from cpu.memory import Memory


# ============================================================
# CONSTANTS
# ============================================================

ADDRESS_MIN = 0x00
ADDRESS_MAX = 0xFF

DATA_MIN = 0x00
DATA_MAX = 0xFF

MEMORY_SIZE = 256


# ============================================================
# HELPERS
# ============================================================


def create_memory():
    """
    Create a fresh Memory object.

    The implementation may expose either:

        Memory()

    or:

        Memory(size)
    """

    try:

        return Memory()

    except TypeError:

        return Memory(
            MEMORY_SIZE
        )


def reset_memory(
    memory,
):
    """
    Reset memory when reset() is available.
    """

    if hasattr(
        memory,
        "reset",
    ):

        reset = getattr(
            memory,
            "reset",
        )

        if callable(
            reset
        ):

            reset()


def write_memory(
    memory,
    address,
    value,
):
    """
    Write a byte to memory.

    Supported APIs:

        write(address, value)
        store(address, value)
        set(address, value)
        memory[address] = value
    """

    for name in (
        "write",
        "store",
        "set",
    ):

        if hasattr(
            memory,
            name,
        ):

            method = getattr(
                memory,
                name,
            )

            if callable(
                method
            ):

                return method(
                    address,
                    value,
                )

    try:

        memory[
            address
        ] = value

        return None

    except (
        TypeError,
        KeyError,
        IndexError,
    ):

        raise AttributeError(
            "Memory does not expose "
            "a supported write API."
        )


def read_memory(
    memory,
    address,
):
    """
    Read a byte from memory.

    Supported APIs:

        read(address)
        load(address)
        get(address)
        memory[address]
    """

    for name in (
        "read",
        "load",
        "get",
    ):

        if hasattr(
            memory,
            name,
        ):

            method = getattr(
                memory,
                name,
            )

            if callable(
                method
            ):

                return method(
                    address
                )

    try:

        return memory[
            address
        ]

    except (
        TypeError,
        KeyError,
        IndexError,
    ):

        raise AttributeError(
            "Memory does not expose "
            "a supported read API."
        )


def get_memory_size(
    memory,
):
    """
    Return memory size when exposed.
    """

    for name in (
        "size",
        "capacity",
        "length",
    ):

        if hasattr(
            memory,
            name,
        ):

            value = getattr(
                memory,
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

    for name in (
        "data",
        "memory",
        "ram",
    ):

        if hasattr(
            memory,
            name,
        ):

            value = getattr(
                memory,
                name,
            )

            try:

                return len(
                    value
                )

            except TypeError:

                continue

    try:

        return len(
            memory
        )

    except TypeError:

        return None


# ============================================================
# CREATION
# ============================================================


def test_memory_can_be_created():
    """
    Memory must be constructable.
    """

    memory = create_memory()

    assert memory is not None


# ============================================================
# SIZE
# ============================================================


def test_memory_has_256_bytes():
    """
    8-bit address space requires:

        2^8 = 256

    addressable memory locations.
    """

    memory = create_memory()

    size = get_memory_size(
        memory
    )

    if size is None:

        pytest.skip(
            "Memory size is not exposed."
        )

    assert (
        size
        == MEMORY_SIZE
    )


# ============================================================
# RESET
# ============================================================


def test_memory_reset_if_supported():
    """
    Memory reset must execute successfully.
    """

    memory = create_memory()

    reset_memory(
        memory
    )


# ============================================================
# INITIAL STATE
# ============================================================


def test_memory_is_zero_initialized():
    """
    Newly initialized memory should normally
    contain zero bytes.
    """

    memory = create_memory()

    reset_memory(
        memory
    )

    for address in (
        0x00,
        0x01,
        0x7F,
        0x80,
        0xFE,
        0xFF,
    ):

        value = read_memory(
            memory,
            address,
        )

        assert (
            value
            == 0x00
        )


# ============================================================
# WRITE / READ
# ============================================================


def test_memory_write_and_read():
    """
    A value written to an address must be
    readable from the same address.
    """

    memory = create_memory()

    write_memory(
        memory,
        0x10,
        0x42,
    )

    value = read_memory(
        memory,
        0x10,
    )

    assert (
        value
        == 0x42
    )


# ============================================================
# ADDRESS 00
# ============================================================


def test_first_memory_address():
    """
    Address 0x00 must be valid.
    """

    memory = create_memory()

    write_memory(
        memory,
        ADDRESS_MIN,
        0xAA,
    )

    assert (
        read_memory(
            memory,
            ADDRESS_MIN,
        )
        == 0xAA
    )


# ============================================================
# ADDRESS FF
# ============================================================


def test_last_memory_address():
    """
    Address 0xFF must be valid.
    """

    memory = create_memory()

    write_memory(
        memory,
        ADDRESS_MAX,
        0x55,
    )

    assert (
        read_memory(
            memory,
            ADDRESS_MAX,
        )
        == 0x55
    )


# ============================================================
# ALL ADDRESSES
# ============================================================


def test_all_256_addresses_are_accessible():
    """
    Every address from 0x00 through 0xFF
    must be independently accessible.
    """

    memory = create_memory()

    for address in range(
        MEMORY_SIZE
    ):

        value = (
            address
            & 0xFF
        )

        write_memory(
            memory,
            address,
            value,
        )

    for address in range(
        MEMORY_SIZE
    ):

        value = read_memory(
            memory,
            address,
        )

        assert (
            value
            == (
                address
                & 0xFF
            )
        )


# ============================================================
# ALL 8-BIT DATA VALUES
# ============================================================


@pytest.mark.parametrize(
    "value",
    range(
        256
    ),
)
def test_all_8bit_values_can_be_stored(
    value,
):
    """
    Every possible 8-bit value must be storable.
    """

    memory = create_memory()

    write_memory(
        memory,
        0x00,
        value,
    )

    result = read_memory(
        memory,
        0x00,
    )

    assert (
        result
        == value
    )


# ============================================================
# ADDRESS INDEPENDENCE
# ============================================================


def test_memory_addresses_are_independent():
    """
    Writing one address must not modify
    another address.
    """

    memory = create_memory()

    write_memory(
        memory,
        0x10,
        0xAA,
    )

    write_memory(
        memory,
        0x11,
        0x55,
    )

    assert (
        read_memory(
            memory,
            0x10,
        )
        == 0xAA
    )

    assert (
        read_memory(
            memory,
            0x11,
        )
        == 0x55
    )


# ============================================================
# OVERWRITE
# ============================================================


def test_memory_value_can_be_overwritten():
    """
    A memory location can be written multiple times.
    """

    memory = create_memory()

    write_memory(
        memory,
        0x20,
        0x11,
    )

    assert (
        read_memory(
            memory,
            0x20,
        )
        == 0x11
    )

    write_memory(
        memory,
        0x20,
        0x22,
    )

    assert (
        read_memory(
            memory,
            0x20,
        )
        == 0x22
    )

    write_memory(
        memory,
        0x20,
        0xFF,
    )

    assert (
        read_memory(
            memory,
            0x20,
        )
        == 0xFF
    )


# ============================================================
# MEMORY PATTERN
# ============================================================


def test_memory_pattern():
    """
    Write a repeating byte pattern to memory
    and verify every location.
    """

    memory = create_memory()

    pattern = [
        0x00,
        0xFF,
        0xAA,
        0x55,
    ]

    for address in range(
        MEMORY_SIZE
    ):

        value = pattern[
            address
            % len(
                pattern
            )
        ]

        write_memory(
            memory,
            address,
            value,
        )

    for address in range(
        MEMORY_SIZE
    ):

        expected = pattern[
            address
            % len(
                pattern
            )
        ]

        actual = read_memory(
            memory,
            address,
        )

        assert (
            actual
            == expected
        )


# ============================================================
# INVALID ADDRESS - NEGATIVE
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        -1,
        -2,
        -128,
        -256,
    ],
)
def test_negative_address_is_rejected(
    address,
):
    """
    Negative addresses are outside the
    8-bit address space.

    Note:
    Python lists normally accept negative indexes,
    therefore the Memory implementation must explicitly
    validate addresses if this test is enabled.
    """

    memory = create_memory()

    with pytest.raises(
        (
            ValueError,
            IndexError,
            TypeError,
            OverflowError,
        )
    ):

        write_memory(
            memory,
            address,
            0x00,
        )


# ============================================================
# INVALID ADDRESS - ABOVE FF
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        0x100,
        0x101,
        0x1FF,
        0x1000,
    ],
)
def test_address_above_ff_is_rejected(
    address,
):
    """
    Addresses above 0xFF must be rejected.
    """

    memory = create_memory()

    with pytest.raises(
        (
            ValueError,
            IndexError,
            TypeError,
            OverflowError,
        )
    ):

        write_memory(
            memory,
            address,
            0x00,
        )


# ============================================================
# INVALID DATA - NEGATIVE
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        -1,
        -2,
        -128,
        -256,
    ],
)
def test_negative_data_is_rejected(
    value,
):
    """
    Data values below 0x00 must be rejected.
    """

    memory = create_memory()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        write_memory(
            memory,
            0x00,
            value,
        )


# ============================================================
# INVALID DATA - ABOVE FF
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        0x100,
        0x101,
        0x1FF,
        0x1000,
    ],
)
def test_data_above_ff_is_rejected(
    value,
):
    """
    Data values above 0xFF must be rejected.
    """

    memory = create_memory()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        write_memory(
            memory,
            0x00,
            value,
        )


# ============================================================
# NON-INTEGER ADDRESS
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        None,
        "0x10",
        "10",
        1.5,
        [],
        {},
    ],
)
def test_non_integer_address_is_rejected(
    address,
):
    """
    Memory addresses must be integers.
    """

    memory = create_memory()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            IndexError,
        )
    ):

        write_memory(
            memory,
            address,
            0x00,
        )


# ============================================================
# NON-INTEGER DATA
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        None,
        "0x10",
        "10",
        1.5,
        [],
        {},
    ],
)
def test_non_integer_data_is_rejected(
    value,
):
    """
    Memory data must be integers.
    """

    memory = create_memory()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        write_memory(
            memory,
            0x00,
            value,
        )


# ============================================================
# SEQUENTIAL WRITE
# ============================================================


def test_sequential_write_and_read():
    """
    Sequential memory operations must preserve
    all written bytes.
    """

    memory = create_memory()

    values = [
        0x10,
        0x20,
        0x30,
        0x40,
        0x50,
        0x60,
        0x70,
        0x80,
    ]

    start_address = 0x20

    for offset, value in enumerate(
        values
    ):

        write_memory(
            memory,
            start_address
            + offset,
            value,
        )

    for offset, expected in enumerate(
        values
    ):

        actual = read_memory(
            memory,
            start_address
            + offset,
        )

        assert (
            actual
            == expected
        )


# ============================================================
# RESET CLEARS MEMORY
# ============================================================


def test_reset_clears_written_memory():
    """
    If reset() is implemented as a full memory reset,
    previously written locations should return to zero.
    """

    memory = create_memory()

    write_memory(
        memory,
        0x00,
        0xAA,
    )

    write_memory(
        memory,
        0x7F,
        0x55,
    )

    write_memory(
        memory,
        0xFF,
        0xFF,
    )

    if not hasattr(
        memory,
        "reset",
    ):

        pytest.skip(
            "Memory reset() is not exposed."
        )

    reset_memory(
        memory
    )

    assert (
        read_memory(
            memory,
            0x00,
        )
        == 0x00
    )

    assert (
        read_memory(
            memory,
            0x7F,
        )
        == 0x00
    )

    assert (
        read_memory(
            memory,
            0xFF,
        )
        == 0x00
    )


# ============================================================
# MEMORY SIZE REMAINS CONSTANT
# ============================================================


def test_memory_size_does_not_change_after_write():
    """
    Writing data must never change memory capacity.
    """

    memory = create_memory()

    size_before = get_memory_size(
        memory
    )

    if size_before is None:

        pytest.skip(
            "Memory size is not exposed."
        )

    write_memory(
        memory,
        0x00,
        0xAA,
    )

    write_memory(
        memory,
        0xFF,
        0x55,
    )

    size_after = get_memory_size(
        memory
    )

    assert (
        size_before
        == size_after
    )

    assert (
        size_after
        == MEMORY_SIZE
    )


# ============================================================
# COMPLETE MEMORY INTEGRATION
# ============================================================


def test_memory_complete_integration():
    """
    Complete MiniCPU memory workflow:

        Address 0x00 -> 0x00
        Address 0x01 -> 0x01
        Address 0x7F -> 0x7F
        Address 0x80 -> 0x80
        Address 0xFE -> 0xFE
        Address 0xFF -> 0xFF

    Verifies the complete 8-bit address range.
    """

    memory = create_memory()

    test_addresses = [
        0x00,
        0x01,
        0x7F,
        0x80,
        0xFE,
        0xFF,
    ]

    for address in test_addresses:

        write_memory(
            memory,
            address,
            address,
        )

    for address in test_addresses:

        assert (
            read_memory(
                memory,
                address,
            )
            == address
        )


# ============================================================
# FINAL ARCHITECTURE CHECK
# ============================================================


def test_memory_matches_8bit_cpu_architecture():
    """
    MiniCPU uses an 8-bit address bus.

    Therefore:

        2^8 = 256 addresses

    Valid range:

        0x00 - 0xFF
    """

    memory = create_memory()

    size = get_memory_size(
        memory
    )

    if size is None:

        pytest.skip(
            "Memory size is not exposed."
        )

    assert (
        size
        == 2 ** 8
    )

    assert (
        ADDRESS_MIN
        == 0x00
    )

    assert (
        ADDRESS_MAX
        == 0xFF
    )
