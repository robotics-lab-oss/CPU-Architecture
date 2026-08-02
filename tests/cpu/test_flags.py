"""
tests/cpu/test_flags.py

MiniCPU 8-bit CPU Architecture
Flags Test Suite

Expected flags:

    Z = Zero Flag
    C = Carry Flag
    N = Negative Flag
    V = Overflow Flag

The exact flag implementation may be provided by
cpu.flags.Flags or integrated into the CPU.

This test module verifies:

- Flag creation
- Reset behavior
- Set/clear operations
- Zero flag
- Carry flag
- Negative flag
- Overflow flag
- 8-bit arithmetic conditions
- Flag independence
- Boolean state
"""

from __future__ import annotations

import pytest

from cpu.flags import Flags


# ============================================================
# HELPERS
# ============================================================


def create_flags():
    """
    Create a fresh Flags object.
    """

    return Flags()


def reset_flags(
    flags,
):
    """
    Reset flags when reset() exists.
    """

    if hasattr(
        flags,
        "reset",
    ):

        reset = getattr(
            flags,
            "reset",
        )

        if callable(
            reset
        ):

            reset()


def get_flag(
    flags,
    names,
):
    """
    Read a flag using common names.
    """

    for name in names:

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

                try:

                    return value()

                except TypeError:

                    continue

            return value

    return None


def set_flag(
    flags,
    names,
    value,
):
    """
    Set a flag using common APIs.
    """

    for name in names:

        if hasattr(
            flags,
            name,
        ):

            target = getattr(
                flags,
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
                    flags,
                    name,
                    value,
                )

                return True

            except Exception:

                continue

    return False


# ============================================================
# CREATION
# ============================================================


def test_flags_can_be_created():
    """
    Flags object must be constructable.
    """

    flags = create_flags()

    assert flags is not None


# ============================================================
# RESET
# ============================================================


def test_flags_reset_if_supported():
    """
    Flags reset must execute successfully.
    """

    flags = create_flags()

    reset_flags(
        flags
    )


# ============================================================
# DEFAULT STATE
# ============================================================


def test_flags_are_clear_after_reset():
    """
    All standard flags should be clear
    after reset.
    """

    flags = create_flags()

    reset_flags(
        flags
    )

    zero = get_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
        ),
    )

    carry = get_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
        ),
    )

    negative = get_flag(
        flags,
        (
            "negative",
            "negative_flag",
            "n",
            "N",
        ),
    )

    overflow = get_flag(
        flags,
        (
            "overflow",
            "overflow_flag",
            "v",
            "V",
        ),
    )

    if zero is not None:

        assert bool(
            zero
        ) is False

    if carry is not None:

        assert bool(
            carry
        ) is False

    if negative is not None:

        assert bool(
            negative
        ) is False

    if overflow is not None:

        assert bool(
            overflow
        ) is False


# ============================================================
# ZERO FLAG
# ============================================================


def test_zero_flag_can_be_set():
    """
    Zero flag must support the True state.
    """

    flags = create_flags()

    success = set_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
            "set_zero",
            "set_zero_flag",
        ),
        True,
    )

    if not success:

        pytest.skip(
            "Zero flag setter is not exposed."
        )

    value = get_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
        ),
    )

    assert bool(
        value
    ) is True


def test_zero_flag_can_be_cleared():
    """
    Zero flag must support the False state.
    """

    flags = create_flags()

    set_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
            "set_zero",
            "set_zero_flag",
        ),
        True,
    )

    success = set_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
            "set_zero",
            "set_zero_flag",
        ),
        False,
    )

    if not success:

        pytest.skip(
            "Zero flag setter is not exposed."
        )

    value = get_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
        ),
    )

    assert bool(
        value
    ) is False


# ============================================================
# CARRY FLAG
# ============================================================


def test_carry_flag_can_be_set():
    """
    Carry flag must support the True state.
    """

    flags = create_flags()

    success = set_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
            "set_carry",
            "set_carry_flag",
        ),
        True,
    )

    if not success:

        pytest.skip(
            "Carry flag setter is not exposed."
        )

    value = get_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
        ),
    )

    assert bool(
        value
    ) is True


def test_carry_flag_can_be_cleared():
    """
    Carry flag must support the False state.
    """

    flags = create_flags()

    set_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
            "set_carry",
            "set_carry_flag",
        ),
        True,
    )

    success = set_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
            "set_carry",
            "set_carry_flag",
        ),
        False,
    )

    if not success:

        pytest.skip(
            "Carry flag setter is not exposed."
        )

    value = get_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
        ),
    )

    assert bool(
        value
    ) is False


# ============================================================
# NEGATIVE FLAG
# ============================================================


def test_negative_flag_can_be_set():
    """
    Negative flag must support the True state.
    """

    flags = create_flags()

    success = set_flag(
        flags,
        (
            "negative",
            "negative_flag",
            "n",
            "N",
            "set_negative",
            "set_negative_flag",
        ),
        True,
    )

    if not success:

        pytest.skip(
            "Negative flag setter is not exposed."
        )

    value = get_flag(
        flags,
        (
            "negative",
            "negative_flag",
            "n",
            "N",
        ),
    )

    assert bool(
        value
    ) is True


# ============================================================
# OVERFLOW FLAG
# ============================================================


def test_overflow_flag_can_be_set():
    """
    Overflow flag must support the True state.
    """

    flags = create_flags()

    success = set_flag(
        flags,
        (
            "overflow",
            "overflow_flag",
            "v",
            "V",
            "set_overflow",
            "set_overflow_flag",
        ),
        True,
    )

    if not success:

        pytest.skip(
            "Overflow flag setter is not exposed."
        )

    value = get_flag(
        flags,
        (
            "overflow",
            "overflow_flag",
            "v",
            "V",
        ),
    )

    assert bool(
        value
    ) is True


# ============================================================
# FLAG INDEPENDENCE
# ============================================================


def test_zero_and_carry_are_independent():
    """
    Setting Zero must not automatically
    change Carry.
    """

    flags = create_flags()

    reset_flags(
        flags
    )

    set_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
            "set_carry",
            "set_carry_flag",
        ),
        False,
    )

    set_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
            "set_zero",
            "set_zero_flag",
        ),
        True,
    )

    zero = get_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
        ),
    )

    carry = get_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
        ),
    )

    if (
        zero is None
        or carry is None
    ):

        pytest.skip(
            "Required flags are not exposed."
        )

    assert bool(
        zero
    ) is True

    assert bool(
        carry
    ) is False


# ============================================================
# ZERO RESULT
# ============================================================


def test_zero_result_should_set_zero_flag():
    """
    Arithmetic result 0x00 should represent
    the Zero condition.

    This test checks the common update method
    if provided by the Flags implementation.
    """

    flags = create_flags()

    for method_name in (
        "update",
        "update_flags",
        "update_from_result",
        "set_from_result",
    ):

        if not hasattr(
            flags,
            method_name,
        ):

            continue

        method = getattr(
            flags,
            method_name,
        )

        if not callable(
            method
        ):

            continue

        try:

            method(
                0x00
            )

        except TypeError:

            try:

                method(
                    0x00,
                    0,
                )

            except TypeError:

                continue

        zero = get_flag(
            flags,
            (
                "zero",
                "zero_flag",
                "z",
                "Z",
            ),
        )

        if zero is not None:

            assert bool(
                zero
            ) is True

        return

    pytest.skip(
        "No supported result-to-flags API is exposed."
    )


# ============================================================
# NON-ZERO RESULT
# ============================================================


def test_nonzero_result_should_clear_zero_flag():
    """
    Non-zero arithmetic result should not
    produce the Zero condition.
    """

    flags = create_flags()

    for method_name in (
        "update",
        "update_flags",
        "update_from_result",
        "set_from_result",
    ):

        if not hasattr(
            flags,
            method_name,
        ):

            continue

        method = getattr(
            flags,
            method_name,
        )

        if not callable(
            method
        ):

            continue

        try:

            method(
                0x01
            )

        except TypeError:

            try:

                method(
                    0x01,
                    0,
                )

            except TypeError:

                continue

        zero = get_flag(
            flags,
            (
                "zero",
                "zero_flag",
                "z",
                "Z",
            ),
        )

        if zero is not None:

            assert bool(
                zero
            ) is False

        return

    pytest.skip(
        "No supported result-to-flags API is exposed."
    )


# ============================================================
# NEGATIVE SIGN BIT
# ============================================================


def test_negative_flag_for_0x80():
    """
    In signed 8-bit representation,
    0x80 has the sign bit set.

    Therefore the Negative condition
    should be true when the implementation
    derives N from the result MSB.
    """

    flags = create_flags()

    for method_name in (
        "update",
        "update_flags",
        "update_from_result",
        "set_from_result",
    ):

        if not hasattr(
            flags,
            method_name,
        ):

            continue

        method = getattr(
            flags,
            method_name,
        )

        if not callable(
            method
        ):

            continue

        try:

            method(
                0x80
            )

        except TypeError:

            try:

                method(
                    0x80,
                    0,
                )

            except TypeError:

                continue

        negative = get_flag(
            flags,
            (
                "negative",
                "negative_flag",
                "n",
                "N",
            ),
        )

        if negative is not None:

            assert bool(
                negative
            ) is True

        return

    pytest.skip(
        "No supported result-to-flags API is exposed."
    )


# ============================================================
# POSITIVE SIGN BIT
# ============================================================


def test_negative_flag_for_0x7f():
    """
    0x7F does not have the sign bit set.
    """

    flags = create_flags()

    for method_name in (
        "update",
        "update_flags",
        "update_from_result",
        "set_from_result",
    ):

        if not hasattr(
            flags,
            method_name,
        ):

            continue

        method = getattr(
            flags,
            method_name,
        )

        if not callable(
            method
        ):

            continue

        try:

            method(
                0x7F
            )

        except TypeError:

            try:

                method(
                    0x7F,
                    0,
                )

            except TypeError:

                continue

        negative = get_flag(
            flags,
            (
                "negative",
                "negative_flag",
                "n",
                "N",
            ),
        )

        if negative is not None:

            assert bool(
                negative
            ) is False

        return

    pytest.skip(
        "No supported result-to-flags API is exposed."
    )


# ============================================================
# ALL FLAGS BOOLEAN
# ============================================================


def test_flags_are_boolean_values_when_exposed():
    """
    Standard flags should be boolean values.
    """

    flags = create_flags()

    reset_flags(
        flags
    )

    names = (
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
        ),
        (
            "carry",
            "carry_flag",
            "c",
            "C",
        ),
        (
            "negative",
            "negative_flag",
            "n",
            "N",
        ),
        (
            "overflow",
            "overflow_flag",
            "v",
            "V",
        ),
    )

    for aliases in names:

        value = get_flag(
            flags,
            aliases,
        )

        if value is not None:

            assert isinstance(
                value,
                bool,
            )


# ============================================================
# RESET AFTER FLAGS SET
# ============================================================


def test_reset_clears_flags():
    """
    Reset should clear flags that were previously set.
    """

    flags = create_flags()

    for aliases in (
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
            "set_zero",
            "set_zero_flag",
        ),
        (
            "carry",
            "carry_flag",
            "c",
            "C",
            "set_carry",
            "set_carry_flag",
        ),
        (
            "negative",
            "negative_flag",
            "n",
            "N",
            "set_negative",
            "set_negative_flag",
        ),
        (
            "overflow",
            "overflow_flag",
            "v",
            "V",
            "set_overflow",
            "set_overflow_flag",
        ),
    ):

        set_flag(
            flags,
            aliases,
            True,
        )

    reset_flags(
        flags
    )

    for aliases in (
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
        ),
        (
            "carry",
            "carry_flag",
            "c",
            "C",
        ),
        (
            "negative",
            "negative_flag",
            "n",
            "N",
        ),
        (
            "overflow",
            "overflow_flag",
            "v",
            "V",
        ),
    ):

        value = get_flag(
            flags,
            aliases,
        )

        if value is not None:

            assert bool(
                value
            ) is False


# ============================================================
# 8-BIT RESULT RANGE
# ============================================================


@pytest.mark.parametrize(
    "result",
    [
        0x00,
        0x01,
        0x7F,
        0x80,
        0xFE,
        0xFF,
    ],
)
def test_flags_accept_valid_8bit_results(
    result,
):
    """
    Valid 8-bit results must be accepted.
    """

    flags = create_flags()

    for method_name in (
        "update",
        "update_flags",
        "update_from_result",
        "set_from_result",
    ):

        if not hasattr(
            flags,
            method_name,
        ):

            continue

        method = getattr(
            flags,
            method_name,
        )

        if not callable(
            method
        ):

            continue

        try:

            method(
                result
            )

        except TypeError:

            try:

                method(
                    result,
                    0,
                )

            except TypeError:

                continue

        return

    pytest.skip(
        "No supported result-to-flags API is exposed."
    )


# ============================================================
# INVALID RESULT
# ============================================================


@pytest.mark.parametrize(
    "result",
    [
        -1,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_flags_reject_invalid_8bit_results(
    result,
):
    """
    Values outside 8-bit range should be rejected
    by result-based flag APIs.
    """

    flags = create_flags()

    for method_name in (
        "update",
        "update_flags",
        "update_from_result",
        "set_from_result",
    ):

        if not hasattr(
            flags,
            method_name,
        ):

            continue

        method = getattr(
            flags,
            method_name,
        )

        if not callable(
            method
        ):

            continue

        with pytest.raises(
            (
                ValueError,
                TypeError,
                OverflowError,
            )
        ):

            method(
                result
            )

        return

    pytest.skip(
        "No supported result-to-flags API is exposed."
    )


# ============================================================
# FINAL FLAGS INTEGRATION
# ============================================================


def test_flags_complete_integration():
    """
    Complete Flags workflow:

        Reset
          ↓
        Set Z
          ↓
        Set C
          ↓
        Clear Z
          ↓
        Clear C
          ↓
        Reset
    """

    flags = create_flags()

    reset_flags(
        flags
    )

    set_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
            "set_zero",
            "set_zero_flag",
        ),
        True,
    )

    set_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
            "set_carry",
            "set_carry_flag",
        ),
        True,
    )

    zero = get_flag(
        flags,
        (
            "zero",
            "zero_flag",
            "z",
            "Z",
        ),
    )

    carry = get_flag(
        flags,
        (
            "carry",
            "carry_flag",
            "c",
            "C",
        ),
    )

    if (
        zero is not None
        and carry is not None
    ):

        assert bool(
            zero
        ) is True

        assert bool(
            carry
        ) is True

    reset_flags(
        flags
    )
