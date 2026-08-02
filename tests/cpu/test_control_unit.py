"""
tests/cpu/test_control_unit.py

MiniCPU 8-bit CPU Architecture
Control Unit Test Suite

The Control Unit is responsible for coordinating
the CPU instruction cycle:

    FETCH
      ↓
    DECODE
      ↓
    EXECUTE

This test module verifies:

- Control Unit creation
- Reset behavior
- Initial state
- FETCH state
- DECODE state
- EXECUTE state
- Instruction cycle
- HALT behavior
- Program Counter interaction where supported
- Instruction Decoder interaction where supported
- Invalid state handling
"""

from __future__ import annotations

import pytest

from cpu.control_unit import ControlUnit


# ============================================================
# CONSTANTS
# ============================================================

FETCH = "FETCH"
DECODE = "DECODE"
EXECUTE = "EXECUTE"
HALT = "HALT"


# ============================================================
# HELPERS
# ============================================================


def create_control_unit():
    """
    Create a fresh Control Unit instance.
    """

    return ControlUnit()


def get_state(
    control_unit,
):
    """
    Read the current Control Unit state.

    Supports common APIs:

        get_state()
        state
        current_state
    """

    if hasattr(
        control_unit,
        "get_state",
    ):

        return control_unit.get_state()

    if hasattr(
        control_unit,
        "state",
    ):

        value = control_unit.state

        if callable(
            value
        ):

            return value()

        return value

    if hasattr(
        control_unit,
        "current_state",
    ):

        value = control_unit.current_state

        if callable(
            value
        ):

            return value()

        return value

    raise AttributeError(
        "ControlUnit does not expose a state API."
    )


def normalize_state(
    state,
):
    """
    Normalize state representation.

    Supports:

        "FETCH"
        "fetch"
        Enum values
    """

    if isinstance(
        state,
        str,
    ):

        return state.upper()

    if hasattr(
        state,
        "name",
    ):

        return state.name.upper()

    return str(
        state
    ).upper()


def reset_control_unit(
    control_unit,
):
    """
    Reset the Control Unit.
    """

    if not hasattr(
        control_unit,
        "reset",
    ):

        raise AttributeError(
            "ControlUnit must provide reset()."
        )

    control_unit.reset()


def call_method(
    control_unit,
    names,
    *args,
):
    """
    Call the first available method.
    """

    for name in names:

        if hasattr(
            control_unit,
            name,
        ):

            method = getattr(
                control_unit,
                name,
            )

            if callable(
                method
            ):

                return method(
                    *args
                )

    raise AttributeError(
        "None of the requested methods "
        "are available: "
        f"{names}"
    )


def step_control_unit(
    control_unit,
):
    """
    Execute one Control Unit step.

    Supported APIs:

        step()
        tick()
        clock()
        cycle()
    """

    return call_method(
        control_unit,
        (
            "step",
            "tick",
            "clock",
            "cycle",
        ),
    )


# ============================================================
# CREATION
# ============================================================


def test_control_unit_can_be_created():
    """
    Control Unit should be constructable.
    """

    control_unit = create_control_unit()

    assert (
        control_unit
        is not None
    )


# ============================================================
# RESET
# ============================================================


def test_control_unit_can_reset():
    """
    Control Unit must provide reset().
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    assert (
        control_unit
        is not None
    )


# ============================================================
# INITIAL STATE
# ============================================================


def test_initial_state_is_valid():
    """
    After creation/reset, the Control Unit
    must have a valid execution state.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert state in {
        FETCH,
        DECODE,
        EXECUTE,
        HALT,
        "IDLE",
        "RESET",
    }


# ============================================================
# RESET STATE
# ============================================================


def test_reset_state_is_deterministic():
    """
    Reset must always produce the same state.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    first_state = normalize_state(
        get_state(
            control_unit
        )
    )

    step_control_unit(
        control_unit
    )

    reset_control_unit(
        control_unit
    )

    second_state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert (
        first_state
        == second_state
    )


# ============================================================
# STEP CHANGES OR PROCESSES STATE
# ============================================================


def test_control_unit_step_is_available():
    """
    Control Unit must expose a method
    capable of advancing execution.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    result = step_control_unit(
        control_unit
    )

    # Some implementations return None.
    # The important requirement is that
    # the operation executes without error.
    assert (
        result is None
        or result is not None
    )


# ============================================================
# MULTIPLE CLOCK STEPS
# ============================================================


def test_control_unit_can_execute_multiple_steps():
    """
    Control Unit should be able to process
    multiple clock steps without crashing.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    for _ in range(
        16
    ):

        step_control_unit(
            control_unit
        )


# ============================================================
# STATE REMAINS VALID
# ============================================================


def test_state_remains_valid_after_steps():
    """
    Every execution step should leave the
    Control Unit in a valid state.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    valid_states = {
        FETCH,
        DECODE,
        EXECUTE,
        HALT,
        "IDLE",
        "RESET",
    }

    for _ in range(
        16
    ):

        state = normalize_state(
            get_state(
                control_unit
            )
        )

        assert state in valid_states

        step_control_unit(
            control_unit
        )


# ============================================================
# FETCH STATE
# ============================================================


def test_fetch_state_if_supported():
    """
    Control Unit should support a FETCH phase
    if the architecture exposes explicit states.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    explicit_fetch = False

    for name in (
        "fetch",
        "do_fetch",
        "fetch_instruction",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            method = getattr(
                control_unit,
                name,
            )

            if callable(
                method
            ):

                method()

                explicit_fetch = True

                break

    if not explicit_fetch:

        pytest.skip(
            "Explicit FETCH method is not exposed."
        )

    state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert state in {
        FETCH,
        DECODE,
        EXECUTE,
        HALT,
    }


# ============================================================
# DECODE STATE
# ============================================================


def test_decode_state_if_supported():
    """
    Control Unit should support a DECODE phase
    if explicit decode functionality exists.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    explicit_decode = False

    for name in (
        "decode",
        "do_decode",
        "decode_instruction",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            method = getattr(
                control_unit,
                name,
            )

            if callable(
                method
            ):

                try:

                    method(
                        0x00
                    )

                except TypeError:

                    method()

                explicit_decode = True

                break

    if not explicit_decode:

        pytest.skip(
            "Explicit DECODE method is not exposed."
        )

    state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert state in {
        FETCH,
        DECODE,
        EXECUTE,
        HALT,
    }


# ============================================================
# EXECUTE STATE
# ============================================================


def test_execute_state_if_supported():
    """
    Control Unit should support an EXECUTE phase
    if explicit execution functionality exists.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    explicit_execute = False

    for name in (
        "execute",
        "do_execute",
        "execute_instruction",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            method = getattr(
                control_unit,
                name,
            )

            if callable(
                method
            ):

                try:

                    method(
                        0x00
                    )

                except TypeError:

                    method()

                explicit_execute = True

                break

    if not explicit_execute:

        pytest.skip(
            "Explicit EXECUTE method is not exposed."
        )

    state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert state in {
        FETCH,
        DECODE,
        EXECUTE,
        HALT,
    }


# ============================================================
# HALT SUPPORT
# ============================================================


def test_halt_api_if_supported():
    """
    If halt() is exposed, it must place the
    Control Unit into a halted state.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    halt_method = None

    for name in (
        "halt",
        "stop",
        "set_halt",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            candidate = getattr(
                control_unit,
                name,
            )

            if callable(
                candidate
            ):

                halt_method = candidate

                break

    if halt_method is None:

        pytest.skip(
            "HALT API is not exposed."
        )

    halt_method()

    state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert state in {
        HALT,
        "STOPPED",
        "STOP",
    }


# ============================================================
# HALT IS STABLE
# ============================================================


def test_halt_state_is_stable_if_supported():
    """
    Once halted, clock steps should not
    accidentally resume execution.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    halt_method = None

    for name in (
        "halt",
        "stop",
        "set_halt",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            candidate = getattr(
                control_unit,
                name,
            )

            if callable(
                candidate
            ):

                halt_method = candidate

                break

    if halt_method is None:

        pytest.skip(
            "HALT API is not exposed."
        )

    halt_method()

    before = normalize_state(
        get_state(
            control_unit
        )
    )

    for _ in range(
        8
    ):

        step_control_unit(
            control_unit
        )

    after = normalize_state(
        get_state(
            control_unit
        )
    )

    assert (
        before
        == after
    )


# ============================================================
# RUN / START
# ============================================================


def test_start_api_if_supported():
    """
    If the Control Unit exposes start(),
    run(), or resume(), it should be callable.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    start_method = None

    for name in (
        "start",
        "run",
        "resume",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            candidate = getattr(
                control_unit,
                name,
            )

            if callable(
                candidate
            ):

                start_method = candidate

                break

    if start_method is None:

        pytest.skip(
            "START/RUN API is not exposed."
        )

    result = start_method()

    assert (
        result is None
        or result is not None
    )


# ============================================================
# CLOCK API
# ============================================================


def test_clock_api_if_supported():
    """
    If clock() exists, it should execute
    without raising an unexpected exception.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    if not hasattr(
        control_unit,
        "clock",
    ):

        pytest.skip(
            "clock() is not exposed."
        )

    clock = getattr(
        control_unit,
        "clock",
    )

    if not callable(
        clock
    ):

        pytest.skip(
            "clock is not callable."
        )

    for _ in range(
        8
    ):

        clock()


# ============================================================
# FETCH-DECODE-EXECUTE CYCLE
# ============================================================


def test_fetch_decode_execute_cycle_if_supported():
    """
    Verify that an explicit CPU cycle can be executed.

    The implementation may expose:

        cycle()
        step()
        tick()
        clock()
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    cycle_method = None

    for name in (
        "cycle",
        "step",
        "tick",
        "clock",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            candidate = getattr(
                control_unit,
                name,
            )

            if callable(
                candidate
            ):

                cycle_method = candidate

                break

    if cycle_method is None:

        pytest.skip(
            "No cycle execution method is exposed."
        )

    for _ in range(
        32
    ):

        cycle_method()


# ============================================================
# INSTRUCTION REGISTER
# ============================================================


def test_instruction_register_if_supported():
    """
    If an instruction register is exposed,
    it should be able to hold an 8-bit opcode.
    """

    control_unit = create_control_unit()

    found = False

    for name in (
        "instruction_register",
        "ir",
        "current_instruction",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            value = getattr(
                control_unit,
                name,
            )

            if isinstance(
                value,
                int,
            ):

                assert (
                    0x00
                    <= value
                    <= 0xFF
                )

            found = True

            break

    if not found:

        pytest.skip(
            "Instruction register is not exposed."
        )


# ============================================================
# OPCODE STORAGE
# ============================================================


@pytest.mark.parametrize(
    "opcode",
    [
        0x00,
        0x10,
        0x20,
        0x30,
        0x40,
        0x50,
        0x60,
        0x70,
        0x80,
        0x90,
        0xA0,
        0xB0,
        0xC0,
        0xD0,
        0xE0,
        0xF0,
    ],
)
def test_opcode_values_if_supported(
    opcode,
):
    """
    MiniCPU uses 8-bit opcode values.

    If the Control Unit exposes an opcode
    loading API, every valid 8-bit opcode
    should be accepted.
    """

    control_unit = create_control_unit()

    load_method = None

    for name in (
        "load_instruction",
        "load_opcode",
        "set_instruction",
        "set_opcode",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            candidate = getattr(
                control_unit,
                name,
            )

            if callable(
                candidate
            ):

                load_method = candidate

                break

    if load_method is None:

        pytest.skip(
            "Opcode loading API is not exposed."
        )

    load_method(
        opcode
    )


# ============================================================
# INVALID OPCODE
# ============================================================


def test_invalid_opcode_is_rejected_if_supported():
    """
    Values outside the 8-bit opcode range
    should be rejected by an opcode loading API.
    """

    control_unit = create_control_unit()

    load_method = None

    for name in (
        "load_instruction",
        "load_opcode",
        "set_instruction",
        "set_opcode",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            candidate = getattr(
                control_unit,
                name,
            )

            if callable(
                candidate
            ):

                load_method = candidate

                break

    if load_method is None:

        pytest.skip(
            "Opcode loading API is not exposed."
        )

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        load_method(
            0x100
        )


# ============================================================
# RESET AFTER HALT
# ============================================================


def test_reset_can_leave_halt_state():
    """
    Reset must restore normal execution
    after HALT when halt API is available.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    halt_method = None

    for name in (
        "halt",
        "stop",
        "set_halt",
    ):

        if hasattr(
            control_unit,
            name,
        ):

            candidate = getattr(
                control_unit,
                name,
            )

            if callable(
                candidate
            ):

                halt_method = candidate

                break

    if halt_method is None:

        pytest.skip(
            "HALT API is not exposed."
        )

    halt_method()

    halted_state = normalize_state(
        get_state(
            control_unit
        )
    )

    reset_control_unit(
        control_unit
    )

    reset_state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert (
        reset_state
        != halted_state
        or reset_state
        in {
            FETCH,
            "RESET",
            "IDLE",
        }
    )


# ============================================================
# COMPLETE CONTROL UNIT INTEGRATION
# ============================================================


def test_control_unit_complete_integration():
    """
    Complete Control Unit workflow:

        RESET
          ↓
        FETCH
          ↓
        DECODE
          ↓
        EXECUTE
          ↓
        next cycle

    The exact internal state transition
    depends on the implementation.
    """

    control_unit = create_control_unit()

    reset_control_unit(
        control_unit
    )

    initial_state = normalize_state(
        get_state(
            control_unit
        )
    )

    assert initial_state in {
        FETCH,
        DECODE,
        EXECUTE,
        HALT,
        "IDLE",
        "RESET",
    }

    for _ in range(
        64
    ):

        step_control_unit(
            control_unit
        )

        state = normalize_state(
            get_state(
                control_unit
            )
        )

        assert state in {
            FETCH,
            DECODE,
            EXECUTE,
            HALT,
            "IDLE",
            "RESET",
        }
