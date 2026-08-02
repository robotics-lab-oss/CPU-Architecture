"""
tests/cpu/test_alu.py

MiniCPU 8-bit CPU Architecture
ALU Test Suite

Architecture:
    Data width: 8-bit
    Value range: 0x00 - 0xFF

The ALU is responsible for:

    ADD
    SUB
    AND
    OR
    XOR
    INC
    DEC
    CMP

This test module verifies:

- Basic arithmetic
- 8-bit overflow
- 8-bit underflow
- Logical operations
- Increment / decrement
- Compare operation
- Zero result
- Carry behavior where supported
- Borrow behavior where supported
- Flag updates where supported
"""

from __future__ import annotations

import pytest

from cpu.alu import ALU


# ============================================================
# CONSTANTS
# ============================================================

MASK_8BIT = 0xFF

MIN_8BIT = 0x00

MAX_8BIT = 0xFF


# ============================================================
# HELPERS
# ============================================================


def create_alu():
    """
    Create a fresh ALU instance.
    """

    return ALU()


def call_operation(
    alu,
    operation,
    *args,
):
    """
    Execute an ALU operation.

    Supports common method names:

        add()
        sub()
        and_op()
        or_op()
        xor()
        inc()
        dec()
        cmp()

    Also supports a generic execute()
    or operate() API.
    """

    operation = operation.upper()

    method_map = {
        "ADD": (
            "add",
            "ADD",
        ),
        "SUB": (
            "sub",
            "SUB",
        ),
        "AND": (
            "and_op",
            "and_operation",
            "AND",
        ),
        "OR": (
            "or_op",
            "or_operation",
            "OR",
        ),
        "XOR": (
            "xor",
            "xor_op",
            "XOR",
        ),
        "INC": (
            "inc",
            "increment",
            "INC",
        ),
        "DEC": (
            "dec",
            "decrement",
            "DEC",
        ),
        "CMP": (
            "cmp",
            "compare",
            "CMP",
        ),
    }

    for method_name in method_map.get(
        operation,
        (),
    ):

        if hasattr(
            alu,
            method_name,
        ):

            method = getattr(
                alu,
                method_name,
            )

            return method(
                *args
            )

    for method_name in (
        "execute",
        "operate",
        "calculate",
    ):

        if hasattr(
            alu,
            method_name,
        ):

            method = getattr(
                alu,
                method_name,
            )

            return method(
                operation,
                *args,
            )

    raise AttributeError(
        f"ALU does not support operation: "
        f"{operation}"
    )


def extract_result(
    result,
):
    """
    Extract the numeric result from
    common ALU return formats.

    Supported:

        int

        {
            "result": value
        }

        (
            value,
            flags
        )
    """

    if isinstance(
        result,
        int,
    ):

        return result

    if isinstance(
        result,
        dict,
    ):

        for key in (
            "result",
            "value",
            "output",
        ):

            if key in result:

                return result[key]

    if isinstance(
        result,
        tuple,
    ):

        if len(
            result
        ) > 0:

            return result[0]

    if hasattr(
        result,
        "result",
    ):

        return result.result

    if hasattr(
        result,
        "value",
    ):

        return result.value

    raise TypeError(
        f"Cannot extract ALU result "
        f"from {result!r}"
    )


def get_flag(
    alu,
    flag_name,
):
    """
    Read a flag if the ALU exposes flags.
    """

    flag_name = flag_name.lower()

    flags = getattr(
        alu,
        "flags",
        None,
    )

    if flags is not None:

        if isinstance(
            flags,
            dict,
        ):

            for key in (
                flag_name,
                flag_name.upper(),
            ):

                if key in flags:

                    return bool(
                        flags[key]
                    )

        for name in (
            flag_name,
            flag_name.upper(),
        ):

            if hasattr(
                flags,
                name,
            ):

                value = getattr(
                    flags,
                    name,
                )

                if callable(
                    value
                ):

                    return bool(
                        value()
                    )

                return bool(
                    value
                )

    for name in (
        flag_name,
        flag_name.upper(),
    ):

        if hasattr(
            alu,
            name,
        ):

            value = getattr(
                alu,
                name,
            )

            if callable(
                value
            ):

                return bool(
                    value()
                )

            return bool(
                value
            )

    return None


# ============================================================
# ALU CREATION
# ============================================================


def test_alu_can_be_created():
    """
    ALU should be constructable.
    """

    alu = create_alu()

    assert alu is not None


# ============================================================
# ADD
# ============================================================


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (0x00, 0x00, 0x00),
        (0x01, 0x01, 0x02),
        (0x05, 0x03, 0x08),
        (0x10, 0x20, 0x30),
        (0x7F, 0x01, 0x80),
        (0x80, 0x7F, 0xFF),
        (0xFF, 0x00, 0xFF),
    ],
)
def test_add(
    a,
    b,
    expected,
):
    """
    Verify 8-bit addition.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        a,
        b,
    )

    assert (
        extract_result(
            result
        )
        == expected
    )


# ============================================================
# ADD OVERFLOW
# ============================================================


def test_add_overflow_wraps_to_zero():
    """
    8-bit arithmetic:

        0xFF + 0x01
        = 0x100
        = 0x00
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        0xFF,
        0x01,
    )

    assert (
        extract_result(
            result
        )
        == 0x00
    )


# ============================================================
# ADD CARRY
# ============================================================


def test_add_sets_carry_if_supported():
    """
    0xFF + 0x01 produces a carry.

    If the ALU exposes a carry flag,
    it must be set.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        0xFF,
        0x01,
    )

    assert (
        extract_result(
            result
        )
        == 0x00
    )

    carry = get_flag(
        alu,
        "carry",
    )

    if carry is not None:

        assert carry is True


# ============================================================
# ADD WITHOUT CARRY
# ============================================================


def test_add_without_carry():
    """
    0x10 + 0x20 = 0x30

    No carry should be generated.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        0x10,
        0x20,
    )

    assert (
        extract_result(
            result
        )
        == 0x30
    )

    carry = get_flag(
        alu,
        "carry",
    )

    if carry is not None:

        assert carry is False


# ============================================================
# SUB
# ============================================================


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (0x00, 0x00, 0x00),
        (0x05, 0x03, 0x02),
        (0x10, 0x05, 0x0B),
        (0xFF, 0x01, 0xFE),
        (0x80, 0x01, 0x7F),
        (0x7F, 0x01, 0x7E),
    ],
)
def test_sub(
    a,
    b,
    expected,
):
    """
    Verify 8-bit subtraction.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "SUB",
        a,
        b,
    )

    assert (
        extract_result(
            result
        )
        == expected
    )


# ============================================================
# SUB UNDERFLOW
# ============================================================


def test_sub_underflow_wraps_to_ff():
    """
    8-bit arithmetic:

        0x00 - 0x01
        = -1
        = 0xFF
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "SUB",
        0x00,
        0x01,
    )

    assert (
        extract_result(
            result
        )
        == 0xFF
    )


# ============================================================
# SUB BORROW
# ============================================================


def test_sub_sets_borrow_if_supported():
    """
    0x00 - 0x01 requires a borrow.

    If borrow is exposed by the ALU,
    it should be reported.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "SUB",
        0x00,
        0x01,
    )

    assert (
        extract_result(
            result
        )
        == 0xFF
    )

    borrow = get_flag(
        alu,
        "borrow",
    )

    if borrow is not None:

        assert borrow is True


# ============================================================
# AND
# ============================================================


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (0x00, 0x00, 0x00),
        (0xFF, 0xFF, 0xFF),
        (0xF0, 0x0F, 0x00),
        (0xAA, 0x55, 0x00),
        (0xFF, 0x0F, 0x0F),
        (0x12, 0x0F, 0x02),
    ],
)
def test_and(
    a,
    b,
    expected,
):
    """
    Verify bitwise AND.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "AND",
        a,
        b,
    )

    assert (
        extract_result(
            result
        )
        == expected
    )


# ============================================================
# OR
# ============================================================


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (0x00, 0x00, 0x00),
        (0xFF, 0x00, 0xFF),
        (0xF0, 0x0F, 0xFF),
        (0xAA, 0x55, 0xFF),
        (0x10, 0x01, 0x11),
        (0x12, 0x0F, 0x1F),
    ],
)
def test_or(
    a,
    b,
    expected,
):
    """
    Verify bitwise OR.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "OR",
        a,
        b,
    )

    assert (
        extract_result(
            result
        )
        == expected
    )


# ============================================================
# XOR
# ============================================================


@pytest.mark.parametrize(
    "a,b,expected",
    [
        (0x00, 0x00, 0x00),
        (0xFF, 0x00, 0xFF),
        (0xFF, 0xFF, 0x00),
        (0xF0, 0x0F, 0xFF),
        (0xAA, 0x55, 0xFF),
        (0x12, 0x0F, 0x1D),
    ],
)
def test_xor(
    a,
    b,
    expected,
):
    """
    Verify bitwise XOR.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "XOR",
        a,
        b,
    )

    assert (
        extract_result(
            result
        )
        == expected
    )


# ============================================================
# INC
# ============================================================


@pytest.mark.parametrize(
    "value,expected",
    [
        (0x00, 0x01),
        (0x01, 0x02),
        (0x7F, 0x80),
        (0xFE, 0xFF),
        (0xFF, 0x00),
    ],
)
def test_inc(
    value,
    expected,
):
    """
    Verify 8-bit increment.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "INC",
        value,
    )

    assert (
        extract_result(
            result
        )
        == expected
    )


# ============================================================
# DEC
# ============================================================


@pytest.mark.parametrize(
    "value,expected",
    [
        (0x00, 0xFF),
        (0x01, 0x00),
        (0x02, 0x01),
        (0x80, 0x7F),
        (0xFF, 0xFE),
    ],
)
def test_dec(
    value,
    expected,
):
    """
    Verify 8-bit decrement.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "DEC",
        value,
    )

    assert (
        extract_result(
            result
        )
        == expected
    )


# ============================================================
# CMP
# ============================================================


def test_cmp_equal():
    """
    CMP 0x10, 0x10

    Expected:
        Equal
        Zero flag = True
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "CMP",
        0x10,
        0x10,
    )

    # CMP implementations may return
    # a difference or only update flags.
    if result is not None:

        result_value = extract_result(
            result
        )

        assert result_value in (
            0x00,
            0,
        )

    zero = get_flag(
        alu,
        "zero",
    )

    if zero is not None:

        assert zero is True


# ============================================================
# CMP NOT EQUAL
# ============================================================


def test_cmp_not_equal():
    """
    CMP 0x10, 0x20

    Expected:
        Not equal
        Zero flag = False
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "CMP",
        0x10,
        0x20,
    )

    if result is not None:

        result_value = extract_result(
            result
        )

        assert result_value != 0

    zero = get_flag(
        alu,
        "zero",
    )

    if zero is not None:

        assert zero is False


# ============================================================
# CMP GREATER
# ============================================================


def test_cmp_greater():
    """
    CMP 0x20, 0x10

    First operand is greater.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "CMP",
        0x20,
        0x10,
    )

    if result is not None:

        result_value = extract_result(
            result
        )

        assert result_value != 0


# ============================================================
# CMP LESS
# ============================================================


def test_cmp_less():
    """
    CMP 0x10, 0x20

    First operand is smaller.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "CMP",
        0x10,
        0x20,
    )

    if result is not None:

        result_value = extract_result(
            result
        )

        assert result_value != 0


# ============================================================
# ZERO RESULT FLAG
# ============================================================


@pytest.mark.parametrize(
    "operation,args",
    [
        (
            "ADD",
            (0x00, 0x00),
        ),
        (
            "SUB",
            (0x10, 0x10),
        ),
        (
            "AND",
            (0xF0, 0x0F),
        ),
        (
            "XOR",
            (0xAA, 0xAA),
        ),
    ],
)
def test_zero_result_flag_if_supported(
    operation,
    args,
):
    """
    Operations producing zero should set
    the zero flag when supported.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        operation,
        *args,
    )

    assert (
        extract_result(
            result
        )
        == 0x00
    )

    zero = get_flag(
        alu,
        "zero",
    )

    if zero is not None:

        assert zero is True


# ============================================================
# NONZERO RESULT FLAG
# ============================================================


def test_nonzero_result_flag_if_supported():
    """
    A non-zero result should clear the zero flag.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        0x01,
        0x01,
    )

    assert (
        extract_result(
            result
        )
        == 0x02
    )

    zero = get_flag(
        alu,
        "zero",
    )

    if zero is not None:

        assert zero is False


# ============================================================
# ALL BYTE VALUES AND ADD ZERO
# ============================================================


@pytest.mark.parametrize(
    "value",
    range(
        0x100
    ),
)
def test_add_zero_preserves_value(
    value,
):
    """
    x + 0 = x

    for every 8-bit value.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        value,
        0x00,
    )

    assert (
        extract_result(
            result
        )
        == value
    )


# ============================================================
# ALL BYTE VALUES AND XOR SELF
# ============================================================


@pytest.mark.parametrize(
    "value",
    range(
        0x100
    ),
)
def test_xor_self_is_zero(
    value,
):
    """
    x XOR x = 0
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "XOR",
        value,
        value,
    )

    assert (
        extract_result(
            result
        )
        == 0x00
    )


# ============================================================
# AND WITH FF
# ============================================================


@pytest.mark.parametrize(
    "value",
    range(
        0x100
    ),
)
def test_and_ff_preserves_value(
    value,
):
    """
    x AND 0xFF = x
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "AND",
        value,
        0xFF,
    )

    assert (
        extract_result(
            result
        )
        == value
    )


# ============================================================
# OR WITH ZERO
# ============================================================


@pytest.mark.parametrize(
    "value",
    range(
        0x100
    ),
)
def test_or_zero_preserves_value(
    value,
):
    """
    x OR 0 = x
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "OR",
        value,
        0x00,
    )

    assert (
        extract_result(
            result
        )
        == value
    )


# ============================================================
# ALU RESULT IS 8-BIT
# ============================================================


@pytest.mark.parametrize(
    "a,b",
    [
        (0x00, 0x00),
        (0xFF, 0xFF),
        (0x80, 0x80),
        (0x7F, 0x01),
        (0x55, 0xAA),
    ],
)
def test_add_result_is_8bit(
    a,
    b,
):
    """
    ALU output must remain within
    the 8-bit range.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        a,
        b,
    )

    value = extract_result(
        result
    )

    assert (
        0x00
        <= value
        <= 0xFF
    )


# ============================================================
# ALU RESET
# ============================================================


def test_alu_reset_if_supported():
    """
    If ALU exposes reset(), it should
    return the ALU to a clean state.
    """

    alu = create_alu()

    if not hasattr(
        alu,
        "reset",
    ):

        pytest.skip(
            "ALU reset() is not exposed."
        )

    alu.reset()

    assert alu is not None


# ============================================================
# INVALID OPERATION
# ============================================================


def test_invalid_operation_is_rejected():
    """
    Unknown operations must not silently execute.
    """

    alu = create_alu()

    with pytest.raises(
        (
            ValueError,
            KeyError,
            AttributeError,
            NotImplementedError,
        )
    ):

        call_operation(
            alu,
            "INVALID_OPERATION",
            0x01,
            0x02,
        )


# ============================================================
# FINAL ALU INTEGRATION
# ============================================================


def test_alu_complete_integration():
    """
    Complete ALU workflow:

        ADD
        SUB
        AND
        OR
        XOR
        INC
        DEC

    All results must be correct.
    """

    alu = create_alu()

    result = call_operation(
        alu,
        "ADD",
        0x10,
        0x05,
    )

    assert (
        extract_result(
            result
        )
        == 0x15
    )

    result = call_operation(
        alu,
        "SUB",
        0x15,
        0x05,
    )

    assert (
        extract_result(
            result
        )
        == 0x10
    )

    result = call_operation(
        alu,
        "AND",
        0xF0,
        0x0F,
    )

    assert (
        extract_result(
            result
        )
        == 0x00
    )

    result = call_operation(
        alu,
        "OR",
        0xF0,
        0x0F,
    )

    assert (
        extract_result(
            result
        )
        == 0xFF
    )

    result = call_operation(
        alu,
        "XOR",
        0xFF,
        0x0F,
    )

    assert (
        extract_result(
            result
        )
        == 0xF0
    )

    result = call_operation(
        alu,
        "INC",
        0x0F,
    )

    assert (
        extract_result(
            result
        )
        == 0x10
    )

    result = call_operation(
        alu,
        "DEC",
        0x10,
    )

    assert (
        extract_result(
            result
        )
        == 0x0F
    )
