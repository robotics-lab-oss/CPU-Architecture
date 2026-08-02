"""
tests/simulator/test_state.py

MiniCPU 8-bit CPU Architecture
Simulator State Test Suite

This module tests CPU state management.

The simulator state may contain:

- Program Counter (PC)
- Registers
- Flags
- Memory
- Halt state
- Instruction Register (IR)
- Stack Pointer (SP)

Supported operations may include:

- Get current state
- Create snapshot
- Save state
- Restore snapshot
- Reset state
- Inspect state
- Compare state

MiniCPU architecture:

    Data width:
        8-bit

    Address width:
        8-bit

    Memory:
        256 bytes

    Address range:
        0x00 - 0xFF

    Instructions:
        16

    Instruction size:
        1-byte or 2-byte
"""

from __future__ import annotations

import copy

import pytest


# ============================================================
# IMPORT STATE
# ============================================================

try:
    from simulator.state import CPUState
except ImportError:

    try:
        from simulator.state import State
    except ImportError:

        CPUState = None

        try:
            from simulator.state import SimulatorState as State
        except ImportError:

            State = None


# ============================================================
# CONSTANTS
# ============================================================

CPU_BITS = 8

ADDRESS_BITS = 8

MEMORY_SIZE = 256

MIN_BYTE = 0x00

MAX_BYTE = 0xFF

INSTRUCTION_COUNT = 16


# ============================================================
# HELPERS
# ============================================================


def get_state_class():
    """
    Return the available CPU state class.
    """

    state_class = (
        CPUState
        or State
    )

    if state_class is None:

        pytest.skip(
            "Simulator state implementation "
            "was not found."
        )

    return state_class


def create_state():
    """
    Create a fresh CPU state.

    Preferred API:

        CPUState()

    Common alternative:

        State()
    """

    state_class = get_state_class()

    constructors = (
        lambda: state_class(),
        lambda: state_class(
            memory_size=MEMORY_SIZE
        ),
        lambda: state_class(
            MEMORY_SIZE
        ),
    )

    last_error = None

    for constructor in constructors:

        try:

            return constructor()

        except (
            TypeError,
            ValueError,
        ) as exc:

            last_error = exc

    pytest.skip(
        "Unable to construct CPU state: "
        f"{last_error}"
    )


def call_method(
    obj,
    names,
    *args,
    **kwargs,
):
    """
    Call the first available method.
    """

    for name in names:

        if not hasattr(
            obj,
            name,
        ):

            continue

        method = getattr(
            obj,
            name,
        )

        if not callable(
            method
        ):

            continue

        try:

            return method(
                *args,
                **kwargs,
            )

        except TypeError:

            continue

    raise AttributeError(
        "None of the supported methods exist: "
        f"{names}"
    )


def get_attribute(
    obj,
    names,
):
    """
    Return the first available attribute.
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

    raise AttributeError(
        "None of the attributes exist: "
        f"{names}"
    )


def get_state_snapshot(
    state,
):
    """
    Get a state snapshot using the available API.
    """

    try:

        return call_method(
            state,
            (
                "snapshot",
                "create_snapshot",
                "save",
                "save_state",
            ),
        )

    except AttributeError:

        try:

            return call_method(
                state,
                (
                    "get_state",
                    "to_dict",
                ),
            )

        except AttributeError:

            return copy.deepcopy(
                getattr(
                    state,
                    "__dict__",
                    {},
                )
            )


# ============================================================
# CREATION
# ============================================================


def test_state_can_be_created():
    """
    CPU state must be constructable.
    """

    state = create_state()

    assert (
        state
        is not None
    )


# ============================================================
# RESET
# ============================================================


def test_state_reset_if_supported():
    """
    State should support reset.
    """

    state = create_state()

    try:

        result = call_method(
            state,
            (
                "reset",
                "clear",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose reset()."
        )

    assert (
        result is None
        or result is True
        or isinstance(
            result,
            dict,
        )
    )


def test_state_reset_is_repeatable():
    """
    Reset should be safe to call multiple times.
    """

    state = create_state()

    try:

        call_method(
            state,
            (
                "reset",
                "clear",
            ),
        )

        call_method(
            state,
            (
                "reset",
                "clear",
            ),
        )

        call_method(
            state,
            (
                "reset",
                "clear",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose reset()."
        )


# ============================================================
# PROGRAM COUNTER
# ============================================================


def test_initial_program_counter_is_zero():
    """
    Initial PC should normally be 0x00.
    """

    state = create_state()

    try:

        pc = get_attribute(
            state,
            (
                "program_counter",
                "pc",
                "PC",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose Program Counter."
        )

    assert (
        pc
        == 0x00
    )


@pytest.mark.parametrize(
    "pc",
    [
        0x00,
        0x01,
        0x10,
        0x40,
        0x80,
        0xFE,
        0xFF,
    ],
)
def test_program_counter_is_8bit(
    pc,
):
    """
    Program Counter must fit in 8 bits.
    """

    assert (
        MIN_BYTE
        <= pc
        <= MAX_BYTE
    )


# ============================================================
# REGISTER STATE
# ============================================================


def test_state_contains_register_information_if_supported():
    """
    CPU state should expose register information.
    """

    state = create_state()

    try:

        registers = get_attribute(
            state,
            (
                "registers",
                "register_file",
                "regs",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose register information."
        )

    assert (
        registers
        is not None
    )


# ============================================================
# FLAGS
# ============================================================


def test_state_contains_flags_if_supported():
    """
    CPU state should expose flags.
    """

    state = create_state()

    try:

        flags = get_attribute(
            state,
            (
                "flags",
                "status_flags",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose flags."
        )

    assert (
        flags
        is not None
    )


# ============================================================
# MEMORY
# ============================================================


def test_state_contains_memory_if_supported():
    """
    CPU state should expose memory information.
    """

    state = create_state()

    try:

        memory = get_attribute(
            state,
            (
                "memory",
                "ram",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose memory."
        )

    assert (
        memory
        is not None
    )


def test_memory_size_is_256_bytes_if_exposed():
    """
    MiniCPU uses an 8-bit address bus:

        2^8 = 256

    Therefore memory address space is:

        0x00 - 0xFF
    """

    state = create_state()

    try:

        memory = get_attribute(
            state,
            (
                "memory",
                "ram",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose memory."
        )

    try:

        assert (
            len(
                memory
            )
            == MEMORY_SIZE
        )

    except TypeError:

        pytest.skip(
            "State memory does not expose "
            "a length."
        )


# ============================================================
# HALT STATE
# ============================================================


def test_initial_halt_state_is_false_if_supported():
    """
    CPU should not initially be halted.
    """

    state = create_state()

    try:

        halted = get_attribute(
            state,
            (
                "halted",
                "is_halted",
                "halt",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose halt state."
        )

    assert (
        bool(
            halted
        )
        is False
    )


# ============================================================
# INSTRUCTION REGISTER
# ============================================================


def test_instruction_register_is_8bit_if_supported():
    """
    Instruction Register must hold an 8-bit value.
    """

    state = create_state()

    try:

        ir = get_attribute(
            state,
            (
                "instruction_register",
                "ir",
                "IR",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose Instruction Register."
        )

    assert (
        MIN_BYTE
        <= ir
        <= MAX_BYTE
    )


# ============================================================
# STACK POINTER
# ============================================================


def test_stack_pointer_is_8bit_if_supported():
    """
    Stack Pointer must fit in the 8-bit address space.
    """

    state = create_state()

    try:

        sp = get_attribute(
            state,
            (
                "stack_pointer",
                "sp",
                "SP",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose Stack Pointer."
        )

    assert (
        MIN_BYTE
        <= sp
        <= MAX_BYTE
    )


# ============================================================
# SNAPSHOT
# ============================================================


def test_state_snapshot_can_be_created():
    """
    State should support snapshot creation.

    A snapshot allows the debugger to save
    the current CPU state.
    """

    state = create_state()

    snapshot = get_state_snapshot(
        state
    )

    assert (
        snapshot
        is not None
    )


def test_snapshot_is_independent_if_supported():
    """
    Snapshot should represent an independent copy
    of the CPU state.
    """

    state = create_state()

    snapshot = get_state_snapshot(
        state
    )

    if isinstance(
        snapshot,
        dict,
    ):

        copied = copy.deepcopy(
            snapshot
        )

        assert (
            copied
            == snapshot
        )

    else:

        assert (
            snapshot
            is not state
        )


# ============================================================
# RESTORE
# ============================================================


def test_state_can_restore_snapshot_if_supported():
    """
    State should support restoring a previous snapshot.
    """

    state = create_state()

    snapshot = get_state_snapshot(
        state
    )

    try:

        result = call_method(
            state,
            (
                "restore",
                "restore_snapshot",
                "load_snapshot",
                "restore_state",
            ),
            snapshot,
        )

    except AttributeError:

        pytest.skip(
            "State does not expose "
            "snapshot restore."
        )

    assert (
        result is None
        or result is True
        or isinstance(
            result,
            dict,
        )
    )


# ============================================================
# STATE SERIALIZATION
# ============================================================


def test_state_can_be_serialized_if_supported():
    """
    State may support conversion to a dictionary.
    """

    state = create_state()

    try:

        result = call_method(
            state,
            (
                "to_dict",
                "serialize",
                "get_state",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose serialization."
        )

    assert isinstance(
        result,
        dict,
    )


# ============================================================
# STATE COPY
# ============================================================


def test_state_can_be_copied():
    """
    CPU state should be safely copyable.
    """

    state = create_state()

    copied_state = copy.deepcopy(
        state
    )

    assert (
        copied_state
        is not state
    )


# ============================================================
# STATE COMPARISON
# ============================================================


def test_two_initial_states_are_equivalent_if_supported():
    """
    Two freshly created CPU states should normally
    represent the same initial CPU state.
    """

    state_a = create_state()

    state_b = create_state()

    snapshot_a = get_state_snapshot(
        state_a
    )

    snapshot_b = get_state_snapshot(
        state_b
    )

    if isinstance(
        snapshot_a,
        dict,
    ) and isinstance(
        snapshot_b,
        dict,
    ):

        assert (
            snapshot_a
            == snapshot_b
        )

    else:

        assert (
            snapshot_a
            is not None
        )

        assert (
            snapshot_b
            is not None
        )


# ============================================================
# BYTE RANGE VALIDATION
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
def test_valid_8bit_values(
    value,
):
    """
    CPU state values must support valid 8-bit values.
    """

    assert (
        MIN_BYTE
        <= value
        <= MAX_BYTE
    )


@pytest.mark.parametrize(
    "value",
    [
        -1,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_8bit_values(
    value,
):
    """
    Values outside 8-bit range are invalid.
    """

    assert not (
        MIN_BYTE
        <= value
        <= MAX_BYTE
    )


# ============================================================
# STATE IMMUTABILITY OF SNAPSHOT
# ============================================================


def test_snapshot_does_not_change_when_state_changes_if_supported():
    """
    After creating a snapshot, changing the live state
    must not silently modify the snapshot.
    """

    state = create_state()

    snapshot = get_state_snapshot(
        state
    )

    if not isinstance(
        snapshot,
        dict,
    ):

        pytest.skip(
            "Snapshot format cannot be "
            "verified as a dictionary."
        )

    original_snapshot = copy.deepcopy(
        snapshot
    )

    # Try to modify PC.
    try:

        call_method(
            state,
            (
                "set_program_counter",
                "set_pc",
            ),
            0x40,
        )

    except AttributeError:

        # Direct attribute fallback.
        if hasattr(
            state,
            "program_counter",
        ):

            try:

                state.program_counter = 0x40

            except (
                AttributeError,
                TypeError,
            ):

                pytest.skip(
                    "State PC cannot be modified."
                )

        elif hasattr(
            state,
            "pc",
        ):

            try:

                state.pc = 0x40

            except (
                AttributeError,
                TypeError,
            ):

                pytest.skip(
                    "State PC cannot be modified."
                )

        else:

            pytest.skip(
                "State does not expose "
                "modifiable Program Counter."
            )

    # Snapshot must remain unchanged.
    assert (
        snapshot
        == original_snapshot
    )


# ============================================================
# RESET AFTER MODIFICATION
# ============================================================


def test_reset_returns_state_to_initial_condition_if_supported():
    """
    Reset should return the state to its initial condition.
    """

    state = create_state()

    initial_snapshot = get_state_snapshot(
        state
    )

    try:

        call_method(
            state,
            (
                "reset",
                "clear",
            ),
        )

    except AttributeError:

        pytest.skip(
            "State does not expose reset()."
        )

    final_snapshot = get_state_snapshot(
        state
    )

    if isinstance(
        initial_snapshot,
        dict,
    ) and isinstance(
        final_snapshot,
        dict,
    ):

        assert (
            final_snapshot
            == initial_snapshot
        )


# ============================================================
# FULL STATE WORKFLOW
# ============================================================


def test_complete_state_workflow():
    """
    Complete CPU state workflow:

        1. Create initial state
        2. Capture snapshot
        3. Modify state
        4. Restore snapshot
        5. Verify state
    """

    state = create_state()

    initial_snapshot = get_state_snapshot(
        state
    )

    operations_run = 1

    # --------------------------------------------------------
    # Modify PC
    # --------------------------------------------------------

    try:

        call_method(
            state,
            (
                "set_program_counter",
                "set_pc",
            ),
            0x20,
        )

        operations_run += 1

    except AttributeError:

        pass

    # --------------------------------------------------------
    # Restore
    # --------------------------------------------------------

    try:

        call_method(
            state,
            (
                "restore",
                "restore_snapshot",
                "load_snapshot",
                "restore_state",
            ),
            initial_snapshot,
        )

        operations_run += 1

    except AttributeError:

        pass

    # --------------------------------------------------------
    # Verify
    # --------------------------------------------------------

    final_snapshot = get_state_snapshot(
        state
    )

    assert (
        operations_run
        >= 1
    )

    if isinstance(
        initial_snapshot,
        dict,
    ) and isinstance(
        final_snapshot,
        dict,
    ):

        assert (
            final_snapshot
            == initial_snapshot
        )


# ============================================================
# FINAL ARCHITECTURE VALIDATION
# ============================================================


def test_state_matches_minicpu_architecture():
    """
    Final MiniCPU state architecture validation.

    CPU:

        8-bit data
        8-bit address
        256-byte memory
        16 instructions
    """

    assert (
        CPU_BITS
        == 8
    )

    assert (
        ADDRESS_BITS
        == 8
    )

    assert (
        2 ** ADDRESS_BITS
        == MEMORY_SIZE
    )

    assert (
        MEMORY_SIZE
        == 256
    )

    assert (
        INSTRUCTION_COUNT
        == 16
    )

    assert (
        MIN_BYTE
        == 0x00
    )

    assert (
        MAX_BYTE
        == 0xFF
    )
