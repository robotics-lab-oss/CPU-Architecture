"""
tests/cpu/test_bus.py

MiniCPU 8-bit CPU Architecture
Bus Test Suite

The system bus connects CPU components such as:

    CPU
    Memory
    Registers
    ALU
    Control Unit

This test module verifies:

- Bus creation
- 8-bit data transfer
- Read operations
- Write operations
- Address transfer
- Data transfer
- 8-bit value range
- Address range
- Bus reset
- Bus isolation
- Repeated transfers
- Boundary values
"""

from __future__ import annotations

import pytest

from cpu.bus import Bus


# ============================================================
# CONSTANTS
# ============================================================

ADDRESS_MIN = 0x00
ADDRESS_MAX = 0xFF

DATA_MIN = 0x00
DATA_MAX = 0xFF

ADDRESS_BITS = 8
DATA_BITS = 8


# ============================================================
# HELPERS
# ============================================================


def create_bus():
    """
    Create a fresh Bus object.

    Supported constructor styles:

        Bus()

    or:

        Bus(address_width=8, data_width=8)
    """

    try:

        return Bus()

    except TypeError:

        try:

            return Bus(
                address_width=ADDRESS_BITS,
                data_width=DATA_BITS,
            )

        except TypeError:

            return Bus(
                ADDRESS_BITS,
                DATA_BITS,
            )


def reset_bus(
    bus,
):
    """
    Reset bus when reset() is available.
    """

    if hasattr(
        bus,
        "reset",
    ):

        reset = getattr(
            bus,
            "reset",
        )

        if callable(
            reset
        ):

            reset()


def get_value(
    obj,
    names,
):
    """
    Read a value from an object using
    common attribute names.
    """

    for name in names:

        if not hasattr(
            obj,
            name,
        ):

            continue

        value = getattr(
            obj,
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


def set_value(
    obj,
    names,
    value,
):
    """
    Set a value using common attribute names
    or setter methods.
    """

    for name in names:

        if not hasattr(
            obj,
            name,
        ):

            continue

        target = getattr(
            obj,
            name,
        )

        if callable(
            target
        ):

            try:

                target(
                    value
                )

                return True

            except TypeError:

                continue

        try:

            setattr(
                obj,
                name,
                value,
            )

            return True

        except Exception:

            continue

    return False


def write_data(
    bus,
    value,
):
    """
    Write data onto the bus.

    Supported APIs:

        write_data(value)
        set_data(value)
        drive_data(value)
    """

    for name in (
        "write_data",
        "set_data",
        "drive_data",
        "write",
        "set",
    ):

        if not hasattr(
            bus,
            name,
        ):

            continue

        method = getattr(
            bus,
            name,
        )

        if callable(
            method
        ):

            try:

                return method(
                    value
                )

            except TypeError:

                continue

    success = set_value(
        bus,
        (
            "data",
            "data_bus",
            "value",
        ),
        value,
    )

    if success:

        return None

    raise AttributeError(
        "Bus does not expose "
        "a supported data write API."
    )


def read_data(
    bus,
):
    """
    Read data from the bus.
    """

    for name in (
        "read_data",
        "get_data",
        "read",
        "get",
    ):

        if not hasattr(
            bus,
            name,
        ):

            continue

        method = getattr(
            bus,
            name,
        )

        if callable(
            method
        ):

            try:

                return method()

            except TypeError:

                continue

    value = get_value(
        bus,
        (
            "data",
            "data_bus",
            "value",
        ),
    )

    if value is not None:

        return value

    raise AttributeError(
        "Bus does not expose "
        "a supported data read API."
    )


def write_address(
    bus,
    address,
):
    """
    Write an address onto the bus.
    """

    for name in (
        "write_address",
        "set_address",
        "drive_address",
    ):

        if not hasattr(
            bus,
            name,
        ):

            continue

        method = getattr(
            bus,
            name,
        )

        if callable(
            method
        ):

            try:

                return method(
                    address
                )

            except TypeError:

                continue

    success = set_value(
        bus,
        (
            "address",
            "address_bus",
            "addr",
        ),
        address,
    )

    if success:

        return None

    raise AttributeError(
        "Bus does not expose "
        "a supported address write API."
    )


def read_address(
    bus,
):
    """
    Read address from the bus.
    """

    for name in (
        "read_address",
        "get_address",
    ):

        if not hasattr(
            bus,
            name,
        ):

            continue

        method = getattr(
            bus,
            name,
        )

        if callable(
            method
        ):

            try:

                return method()

            except TypeError:

                continue

    value = get_value(
        bus,
        (
            "address",
            "address_bus",
            "addr",
        ),
    )

    if value is not None:

        return value

    raise AttributeError(
        "Bus does not expose "
        "a supported address read API."
    )


# ============================================================
# CREATION
# ============================================================


def test_bus_can_be_created():
    """
    Bus must be constructable.
    """

    bus = create_bus()

    assert bus is not None


# ============================================================
# DATA BUS
# ============================================================


def test_data_bus_write_and_read():
    """
    A value written to the data bus must
    be readable from the data bus.
    """

    bus = create_bus()

    write_data(
        bus,
        0x42,
    )

    assert (
        read_data(
            bus
        )
        == 0x42
    )


# ============================================================
# ADDRESS BUS
# ============================================================


def test_address_bus_write_and_read():
    """
    An address written to the address bus
    must be readable from the address bus.
    """

    bus = create_bus()

    write_address(
        bus,
        0x80,
    )

    assert (
        read_address(
            bus
        )
        == 0x80
    )


# ============================================================
# DATA BOUNDARIES
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
def test_data_bus_accepts_8bit_values(
    value,
):
    """
    Data bus must support all important 8-bit
    boundary values.
    """

    bus = create_bus()

    write_data(
        bus,
        value,
    )

    assert (
        read_data(
            bus
        )
        == value
    )


# ============================================================
# ADDRESS BOUNDARIES
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
def test_address_bus_accepts_8bit_addresses(
    address,
):
    """
    Address bus must support the complete
    8-bit address range boundaries.
    """

    bus = create_bus()

    write_address(
        bus,
        address,
    )

    assert (
        read_address(
            bus
        )
        == address
    )


# ============================================================
# ALL DATA VALUES
# ============================================================


def test_data_bus_supports_all_256_values():
    """
    Every possible 8-bit data value must
    be transferable.
    """

    bus = create_bus()

    for value in range(
        256
    ):

        write_data(
            bus,
            value,
        )

        assert (
            read_data(
                bus
            )
            == value
        )


# ============================================================
# ALL ADDRESSES
# ============================================================


def test_address_bus_supports_all_256_addresses():
    """
    Every possible 8-bit address must
    be transferable.
    """

    bus = create_bus()

    for address in range(
        256
    ):

        write_address(
            bus,
            address,
        )

        assert (
            read_address(
                bus
            )
            == address
        )


# ============================================================
# DATA OVERWRITE
# ============================================================


def test_data_bus_can_be_overwritten():
    """
    Data bus value can change between transfers.
    """

    bus = create_bus()

    write_data(
        bus,
        0x11,
    )

    assert (
        read_data(
            bus
        )
        == 0x11
    )

    write_data(
        bus,
        0x22,
    )

    assert (
        read_data(
            bus
        )
        == 0x22
    )

    write_data(
        bus,
        0xFF,
    )

    assert (
        read_data(
            bus
        )
        == 0xFF
    )


# ============================================================
# ADDRESS OVERWRITE
# ============================================================


def test_address_bus_can_be_overwritten():
    """
    Address bus value can change between transfers.
    """

    bus = create_bus()

    write_address(
        bus,
        0x10,
    )

    assert (
        read_address(
            bus
        )
        == 0x10
    )

    write_address(
        bus,
        0x20,
    )

    assert (
        read_address(
            bus
        )
        == 0x20
    )

    write_address(
        bus,
        0xFF,
    )

    assert (
        read_address(
            bus
        )
        == 0xFF
    )


# ============================================================
# DATA AND ADDRESS INDEPENDENCE
# ============================================================


def test_data_and_address_are_independent():
    """
    Changing the address bus must not change
    the data bus, and vice versa.
    """

    bus = create_bus()

    write_data(
        bus,
        0xAA,
    )

    write_address(
        bus,
        0x55,
    )

    assert (
        read_data(
            bus
        )
        == 0xAA
    )

    assert (
        read_address(
            bus
        )
        == 0x55
    )

    write_data(
        bus,
        0x11,
    )

    assert (
        read_data(
            bus
        )
        == 0x11
    )

    assert (
        read_address(
            bus
        )
        == 0x55
    )


# ============================================================
# RESET
# ============================================================


def test_bus_reset_if_supported():
    """
    Bus reset must execute successfully.
    """

    bus = create_bus()

    reset_bus(
        bus
    )


# ============================================================
# RESET STATE
# ============================================================


def test_bus_reset_clears_bus_values():
    """
    If reset() is implemented as a complete bus reset,
    data and address should return to zero.
    """

    bus = create_bus()

    write_data(
        bus,
        0xAA,
    )

    write_address(
        bus,
        0x55,
    )

    if not hasattr(
        bus,
        "reset",
    ):

        pytest.skip(
            "Bus reset() is not exposed."
        )

    reset_bus(
        bus
    )

    data = read_data(
        bus
    )

    address = read_address(
        bus
    )

    assert (
        data
        == 0x00
    )

    assert (
        address
        == 0x00
    )


# ============================================================
# INVALID DATA
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        -1,
        -2,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_data_is_rejected(
    value,
):
    """
    Data bus must reject values outside
    the 8-bit range.
    """

    bus = create_bus()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        write_data(
            bus,
            value,
        )


# ============================================================
# INVALID ADDRESS
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        -1,
        -2,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_address_is_rejected(
    address,
):
    """
    Address bus must reject values outside
    the 8-bit range.
    """

    bus = create_bus()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        write_address(
            bus,
            address,
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
    Data bus must reject non-integer values.
    """

    bus = create_bus()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        write_data(
            bus,
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
    Address bus must reject non-integer values.
    """

    bus = create_bus()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        write_address(
            bus,
            address,
        )


# ============================================================
# TRANSFER SEQUENCE
# ============================================================


def test_bus_transfer_sequence():
    """
    Verify a sequence of address/data transfers.

    Example:

        Address 0x10 -> Data 0xAA
        Address 0x20 -> Data 0x55
        Address 0x30 -> Data 0xFF
    """

    bus = create_bus()

    transfers = [
        (
            0x10,
            0xAA,
        ),
        (
            0x20,
            0x55,
        ),
        (
            0x30,
            0xFF,
        ),
    ]

    for address, value in transfers:

        write_address(
            bus,
            address,
        )

        write_data(
            bus,
            value,
        )

        assert (
            read_address(
                bus
            )
            == address
        )

        assert (
            read_data(
                bus
            )
            == value
        )


# ============================================================
# ALTERNATING TRANSFERS
# ============================================================


def test_bus_alternating_transfers():
    """
    Repeatedly alternate address and data
    values to ensure no stale state is introduced.
    """

    bus = create_bus()

    for index in range(
        32
    ):

        address = (
            index
            & 0xFF
        )

        value = (
            0xFF
            - index
        ) & 0xFF

        write_address(
            bus,
            address,
        )

        write_data(
            bus,
            value,
        )

        assert (
            read_address(
                bus
            )
            == address
        )

        assert (
            read_data(
                bus
            )
            == value
        )


# ============================================================
# BUS WIDTH
# ============================================================


def test_bus_is_8bit_data_bus():
    """
    MiniCPU data bus width is 8 bits.
    """

    bus = create_bus()

    width = get_value(
        bus,
        (
            "data_width",
            "DATA_WIDTH",
        ),
    )

    if width is None:

        pytest.skip(
            "Data bus width is not exposed."
        )

    assert (
        width
        == DATA_BITS
    )


def test_bus_is_8bit_address_bus():
    """
    MiniCPU address bus width is 8 bits.
    """

    bus = create_bus()

    width = get_value(
        bus,
        (
            "address_width",
            "ADDRESS_WIDTH",
        ),
    )

    if width is None:

        pytest.skip(
            "Address bus width is not exposed."
        )

    assert (
        width
        == ADDRESS_BITS
    )


# ============================================================
# COMPLETE BUS INTEGRATION
# ============================================================


def test_bus_complete_integration():
    """
    Complete MiniCPU bus test.

    The 8-bit CPU has:

        Data Bus:
            0x00 - 0xFF

        Address Bus:
            0x00 - 0xFF
    """

    bus = create_bus()

    test_vectors = [
        (
            0x00,
            0x00,
        ),
        (
            0x01,
            0xFF,
        ),
        (
            0x7F,
            0x80,
        ),
        (
            0x80,
            0x7F,
        ),
        (
            0xFE,
            0xAA,
        ),
        (
            0xFF,
            0x55,
        ),
    ]

    for address, data in test_vectors:

        write_address(
            bus,
            address,
        )

        write_data(
            bus,
            data,
        )

        assert (
            read_address(
                bus
            )
            == address
        )

        assert (
            read_data(
                bus
            )
            == data
        )


# ============================================================
# FINAL ARCHITECTURE VALIDATION
# ============================================================


def test_bus_matches_8bit_cpu_architecture():
    """
    Final architecture validation.

    MiniCPU:

        Address width = 8 bits
        Data width    = 8 bits

    Therefore:

        Address range = 0x00 - 0xFF
        Data range    = 0x00 - 0xFF
    """

    assert (
        2 ** ADDRESS_BITS
        == 256
    )

    assert (
        ADDRESS_MAX
        == 0xFF
    )

    assert (
        DATA_MAX
        == 0xFF
    )

    bus = create_bus()

    write_address(
        bus,
        ADDRESS_MAX,
    )

    write_data(
        bus,
        DATA_MAX,
    )

    assert (
        read_address(
            bus
        )
        == ADDRESS_MAX
    )

    assert (
        read_data(
            bus
        )
        == DATA_MAX
    )
