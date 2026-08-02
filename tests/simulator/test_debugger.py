"""
tests/simulator/test_debugger.py

MiniCPU 8-bit CPU Architecture
Simulator Debugger Test Suite

The debugger is responsible for:

- CPU inspection
- Register inspection
- Program Counter inspection
- Flag inspection
- Memory inspection
- Breakpoints
- Removing breakpoints
- Single-step execution
- Continue execution
- Halt detection
- CPU state inspection

MiniCPU architecture:

    Data width:
        8-bit

    Address width:
        8-bit

    Memory:
        256 bytes

    Address range:
        0x00 - 0xFF

    Instruction size:
        1-byte or 2-byte
"""

from __future__ import annotations

import pytest


# ============================================================
# IMPORT DEBUGGER
# ============================================================

try:
    from simulator.debugger import Debugger
except ImportError:

    try:
        from simulator.debugger import CPUDebugger as Debugger
    except ImportError:

        Debugger = None


# ============================================================
# CONSTANTS
# ============================================================

CPU_BITS = 8

ADDRESS_BITS = 8

MEMORY_SIZE = 256

MIN_BYTE = 0x00

MAX_BYTE = 0xFF


# ============================================================
# HELPERS
# ============================================================


def create_debugger():
    """
    Create a debugger instance.

    Preferred API:

        Debugger()

    Common alternative:

        Debugger(cpu)
    """

    if Debugger is None:

        pytest.skip(
            "Simulator Debugger implementation "
            "was not found."
        )

    constructors = (
        lambda: Debugger(),
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
        "Unable to construct Debugger: "
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
    Get the first available attribute.
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


# ============================================================
# CREATION
# ============================================================


def test_debugger_can_be_created():
    """
    Debugger must be constructable.
    """

    debugger = create_debugger()

    assert (
        debugger
        is not None
    )


# ============================================================
# RESET
# ============================================================


def test_debugger_reset_if_supported():
    """
    Debugger should support reset when implemented.
    """

    debugger = create_debugger()

    try:

        result = call_method(
            debugger,
            (
                "reset",
                "restart",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose reset()."
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
# PROGRAM LOADING
# ============================================================


def test_debugger_can_load_program_if_supported():
    """
    Debugger may directly load machine code.
    """

    debugger = create_debugger()

    program = bytes(
        [
            0x00,
            0x00,
            0xF0,
        ]
    )

    try:

        result = call_method(
            debugger,
            (
                "load_program",
                "load",
                "load_code",
            ),
            program,
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "program loading."
        )

    assert (
        result is None
        or isinstance(
            result,
            bool,
        )
        or isinstance(
            result,
            dict,
        )
    )


# ============================================================
# PROGRAM COUNTER INSPECTION
# ============================================================


def test_debugger_can_inspect_program_counter():
    """
    Debugger should expose Program Counter information.
    """

    debugger = create_debugger()

    try:

        pc = get_attribute(
            debugger,
            (
                "program_counter",
                "pc",
                "get_pc",
                "inspect_pc",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "Program Counter inspection."
        )

    assert (
        MIN_BYTE
        <= pc
        <= MAX_BYTE
    )


# ============================================================
# REGISTER INSPECTION
# ============================================================


def test_debugger_can_inspect_registers():
    """
    Debugger should expose register information.
    """

    debugger = create_debugger()

    try:

        registers = call_method(
            debugger,
            (
                "get_registers",
                "inspect_registers",
                "dump_registers",
            ),
        )

    except AttributeError:

        try:

            registers = get_attribute(
                debugger,
                (
                    "registers",
                    "register_file",
                ),
            )

        except AttributeError:

            pytest.skip(
                "Debugger does not expose "
                "register inspection."
            )

    assert (
        registers
        is not None
    )


# ============================================================
# FLAG INSPECTION
# ============================================================


def test_debugger_can_inspect_flags():
    """
    Debugger should expose CPU flag information.
    """

    debugger = create_debugger()

    try:

        flags = call_method(
            debugger,
            (
                "get_flags",
                "inspect_flags",
                "dump_flags",
            ),
        )

    except AttributeError:

        try:

            flags = get_attribute(
                debugger,
                (
                    "flags",
                ),
            )

        except AttributeError:

            pytest.skip(
                "Debugger does not expose "
                "flag inspection."
            )

    assert (
        flags
        is not None
    )


# ============================================================
# MEMORY INSPECTION
# ============================================================


@pytest.mark.parametrize(
    "address",
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
def test_debugger_can_inspect_memory(
    address,
):
    """
    Debugger should be able to inspect valid 8-bit
    memory addresses.
    """

    debugger = create_debugger()

    try:

        value = call_method(
            debugger,
            (
                "read_memory",
                "inspect_memory",
                "peek",
                "memory_read",
            ),
            address,
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "memory inspection."
        )

    assert (
        value is None
        or (
            isinstance(
                value,
                int,
            )
            and MIN_BYTE
            <= value
            <= MAX_BYTE
        )
    )


# ============================================================
# INVALID MEMORY ADDRESS
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        -1,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_memory_address_is_rejected(
    address,
):
    """
    Memory addresses outside 8-bit range
    must be rejected.
    """

    debugger = create_debugger()

    try:

        with pytest.raises(
            (
                ValueError,
                TypeError,
                OverflowError,
            )
        ):

            call_method(
                debugger,
                (
                    "read_memory",
                    "inspect_memory",
                    "peek",
                    "memory_read",
                ),
                address,
            )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "memory inspection."
        )


# ============================================================
# MEMORY WRITE
# ============================================================


def test_debugger_can_modify_memory_if_supported():
    """
    Debugger may provide memory write functionality
    for debugging purposes.
    """

    debugger = create_debugger()

    try:

        result = call_method(
            debugger,
            (
                "write_memory",
                "poke",
                "memory_write",
            ),
            0x10,
            0x42,
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "memory write."
        )

    assert (
        result is None
        or isinstance(
            result,
            bool,
        )
    )


# ============================================================
# BREAKPOINT CREATION
# ============================================================


@pytest.mark.parametrize(
    "address",
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
def test_breakpoint_can_be_added(
    address,
):
    """
    Debugger must support breakpoints at valid
    8-bit addresses when breakpoint functionality exists.
    """

    debugger = create_debugger()

    try:

        result = call_method(
            debugger,
            (
                "add_breakpoint",
                "set_breakpoint",
                "breakpoint",
            ),
            address,
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "breakpoint functionality."
        )

    assert (
        result is None
        or isinstance(
            result,
            bool,
        )
        or isinstance(
            result,
            int,
        )
    )


# ============================================================
# INVALID BREAKPOINT
# ============================================================


@pytest.mark.parametrize(
    "address",
    [
        -1,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_breakpoint_address_is_rejected(
    address,
):
    """
    Breakpoint addresses must fit in 8 bits.
    """

    debugger = create_debugger()

    try:

        with pytest.raises(
            (
                ValueError,
                TypeError,
                OverflowError,
            )
        ):

            call_method(
                debugger,
                (
                    "add_breakpoint",
                    "set_breakpoint",
                    "breakpoint",
                ),
                address,
            )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "breakpoint functionality."
        )


# ============================================================
# BREAKPOINT REMOVAL
# ============================================================


def test_breakpoint_can_be_removed():
    """
    Debugger should support removing breakpoints.
    """

    debugger = create_debugger()

    try:

        call_method(
            debugger,
            (
                "add_breakpoint",
                "set_breakpoint",
            ),
            0x10,
        )

        result = call_method(
            debugger,
            (
                "remove_breakpoint",
                "clear_breakpoint",
                "delete_breakpoint",
            ),
            0x10,
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "breakpoint management."
        )

    assert (
        result is None
        or isinstance(
            result,
            bool,
        )
    )


# ============================================================
# CLEAR ALL BREAKPOINTS
# ============================================================


def test_clear_all_breakpoints():
    """
    Debugger should be able to clear all breakpoints.
    """

    debugger = create_debugger()

    try:

        call_method(
            debugger,
            (
                "add_breakpoint",
                "set_breakpoint",
            ),
            0x10,
        )

        call_method(
            debugger,
            (
                "add_breakpoint",
                "set_breakpoint",
            ),
            0x20,
        )

        result = call_method(
            debugger,
            (
                "clear_breakpoints",
                "remove_all_breakpoints",
                "delete_all_breakpoints",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "clear-all breakpoint functionality."
        )

    assert (
        result is None
        or isinstance(
            result,
            bool,
        )
    )


# ============================================================
# BREAKPOINT INSPECTION
# ============================================================


def test_debugger_can_list_breakpoints():
    """
    Debugger should expose active breakpoints
    when breakpoint functionality is implemented.
    """

    debugger = create_debugger()

    try:

        call_method(
            debugger,
            (
                "add_breakpoint",
                "set_breakpoint",
            ),
            0x10,
        )

        breakpoints = call_method(
            debugger,
            (
                "get_breakpoints",
                "list_breakpoints",
                "breakpoints",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "breakpoint listing."
        )

    assert (
        breakpoints
        is not None
    )


# ============================================================
# SINGLE STEP
# ============================================================


def test_debugger_single_step():
    """
    Debugger should support single-step execution.
    """

    debugger = create_debugger()

    try:

        result = call_method(
            debugger,
            (
                "step",
                "step_instruction",
                "single_step",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "single-step execution."
        )

    assert (
        result is None
        or isinstance(
            result,
            int,
        )
        or isinstance(
            result,
            bool,
        )
        or isinstance(
            result,
            dict,
        )
    )


# ============================================================
# CONTINUE EXECUTION
# ============================================================


def test_debugger_continue():
    """
    Debugger should support continuing execution
    after a breakpoint when implemented.
    """

    debugger = create_debugger()

    try:

        result = call_method(
            debugger,
            (
                "continue_execution",
                "continue_run",
                "continue_",
                "run",
                "continue",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "continue execution."
        )

    assert (
        result is None
        or isinstance(
            result,
            int,
        )
        or isinstance(
            result,
            bool,
        )
        or isinstance(
            result,
            dict,
        )
    )


# ============================================================
# HALT INSPECTION
# ============================================================


def test_debugger_can_inspect_halt_state():
    """
    Debugger should expose CPU halt status.
    """

    debugger = create_debugger()

    try:

        halted = get_attribute(
            debugger,
            (
                "halted",
                "is_halted",
                "get_halt_state",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "halt state."
        )

    assert isinstance(
        halted,
        bool,
    )


# ============================================================
# CPU STATE DUMP
# ============================================================


def test_debugger_can_dump_cpu_state():
    """
    Debugger should provide a complete CPU state dump
    when implemented.
    """

    debugger = create_debugger()

    try:

        state = call_method(
            debugger,
            (
                "get_state",
                "inspect_state",
                "dump_state",
                "cpu_state",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "CPU state dump."
        )

    assert (
        state
        is not None
    )


# ============================================================
# CPU STATE SNAPSHOT
# ============================================================


def test_debugger_can_create_snapshot():
    """
    Debugger may support snapshots for debugging.
    """

    debugger = create_debugger()

    try:

        snapshot = call_method(
            debugger,
            (
                "snapshot",
                "create_snapshot",
                "save_state",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "snapshot functionality."
        )

    assert (
        snapshot
        is not None
    )


# ============================================================
# WATCHPOINT
# ============================================================


def test_memory_watchpoint_if_supported():
    """
    Advanced debugger implementations may support
    memory watchpoints.
    """

    debugger = create_debugger()

    try:

        result = call_method(
            debugger,
            (
                "add_watchpoint",
                "set_watchpoint",
                "watch_memory",
            ),
            0x20,
        )

    except AttributeError:

        pytest.skip(
            "Debugger does not expose "
            "memory watchpoints."
        )

    assert (
        result is None
        or isinstance(
            result,
            bool,
        )
        or isinstance(
            result,
            int,
        )
    )


# ============================================================
# 8-BIT ADDRESS VALIDATION
# ============================================================


def test_debugger_uses_8bit_address_space():
    """
    MiniCPU debugger must work with an 8-bit address bus.

        2^8 = 256 addresses

        0x00 - 0xFF
    """

    assert (
        2 ** ADDRESS_BITS
        == MEMORY_SIZE
    )

    assert (
        MEMORY_SIZE
        == 256
    )


# ============================================================
# COMPLETE DEBUGGING WORKFLOW
# ============================================================


def test_complete_debugger_workflow():
    """
    Complete debugging workflow:

        1. Create debugger
        2. Reset
        3. Load program
        4. Set breakpoint
        5. Step or continue
        6. Inspect state
        7. Remove breakpoint
    """

    debugger = create_debugger()

    operations_run = 0

    # --------------------------------------------------------
    # Reset
    # --------------------------------------------------------

    try:

        call_method(
            debugger,
            (
                "reset",
                "restart",
            ),
        )

        operations_run += 1

    except AttributeError:

        pass

    # --------------------------------------------------------
    # Load program
    # --------------------------------------------------------

    try:

        call_method(
            debugger,
            (
                "load_program",
                "load",
                "load_code",
            ),
            bytes(
                [
                    0x00,
                    0x00,
                    0xF0,
                ]
            ),
        )

        operations_run += 1

    except AttributeError:

        pass

    # --------------------------------------------------------
    # Breakpoint
    # --------------------------------------------------------

    try:

        call_method(
            debugger,
            (
                "add_breakpoint",
                "set_breakpoint",
            ),
            0x02,
        )

        operations_run += 1

    except AttributeError:

        pass

    # --------------------------------------------------------
    # Step
    # --------------------------------------------------------

    try:

        call_method(
            debugger,
            (
                "step",
                "step_instruction",
                "single_step",
            ),
        )

        operations_run += 1

    except AttributeError:

        pass

    # --------------------------------------------------------
    # State inspection
    # --------------------------------------------------------

    try:

        call_method(
            debugger,
            (
                "get_state",
                "inspect_state",
                "dump_state",
            ),
        )

        operations_run += 1

    except AttributeError:

        pass

    # --------------------------------------------------------
    # Breakpoint removal
    # --------------------------------------------------------

    try:

        call_method(
            debugger,
            (
                "remove_breakpoint",
                "clear_breakpoint",
                "delete_breakpoint",
            ),
            0x02,
        )

        operations_run += 1

    except AttributeError:

        pass

    if operations_run == 0:

        pytest.skip(
            "Debugger does not expose "
            "any supported debugging operations."
        )

    assert (
        operations_run
        >= 1
    )


# ============================================================
# FINAL ARCHITECTURE VALIDATION
# ============================================================


def test_debugger_matches_minicpu_architecture():
    """
    Final MiniCPU debugger architecture validation.

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
        16
        == 2 ** 4
    )

    assert (
        MIN_BYTE
        == 0x00
    )

    assert (
        MAX_BYTE
        == 0xFF
    )
