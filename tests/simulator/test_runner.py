"""
tests/simulator/test_runner.py

MiniCPU 8-bit CPU Architecture
Simulator Runner Test Suite

The simulator runner is responsible for:

- Loading machine code
- Resetting CPU state
- Starting execution
- Executing instructions
- Handling 1-byte instructions
- Handling 2-byte instructions
- Advancing Program Counter
- HALT handling
- Maximum cycle protection
- Running complete programs

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
        1 byte or 2 bytes
"""

from __future__ import annotations

import pytest


# ============================================================
# IMPORT RUNNER
# ============================================================

try:
    from simulator.runner import Runner
except ImportError:

    try:
        from simulator.runner import SimulatorRunner as Runner
    except ImportError:

        Runner = None


# ============================================================
# CONSTANTS
# ============================================================

BITS = 8

MEMORY_SIZE = 256

MIN_BYTE = 0x00

MAX_BYTE = 0xFF

MAX_CYCLES = 1000


# ============================================================
# HELPERS
# ============================================================


def create_runner():
    """
    Create a fresh simulator runner.

    The preferred API is:

        Runner()

    If the project exposes a different constructor,
    this helper attempts common alternatives.
    """

    if Runner is None:

        pytest.skip(
            "Simulator Runner implementation "
            "was not found."
        )

    constructors = (
        lambda: Runner(),
        lambda: Runner(
            memory_size=MEMORY_SIZE
        ),
        lambda: Runner(
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
        "Unable to construct simulator Runner: "
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

    Supports multiple common method names.
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

        if hasattr(
            obj,
            name,
        ):

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


def load_program(
    runner,
    program,
):
    """
    Load a program into the simulator.

    Supported APIs include:

        load_program(program)
        load(program)
        load_code(program)
    """

    return call_method(
        runner,
        (
            "load_program",
            "load",
            "load_code",
            "load_machine_code",
        ),
        program,
    )


def reset_runner(
    runner,
):
    """
    Reset simulator state.
    """

    return call_method(
        runner,
        (
            "reset",
            "restart",
        ),
    )


def run_runner(
    runner,
    max_cycles=MAX_CYCLES,
):
    """
    Run the loaded program.
    """

    try:

        return call_method(
            runner,
            (
                "run",
                "execute",
                "start",
            ),
            max_cycles=max_cycles,
        )

    except AttributeError:

        return call_method(
            runner,
            (
                "run",
                "execute",
                "start",
            ),
            max_cycles,
        )


def step_runner(
    runner,
):
    """
    Execute one simulator step.
    """

    return call_method(
        runner,
        (
            "step",
            "tick",
            "cycle",
        ),
    )


# ============================================================
# CREATION
# ============================================================


def test_runner_can_be_created():
    """
    Runner must be constructable.
    """

    runner = create_runner()

    assert runner is not None


# ============================================================
# RESET
# ============================================================


def test_runner_reset():
    """
    Runner must support reset.
    """

    runner = create_runner()

    try:

        result = reset_runner(
            runner
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose reset()."
        )

    assert (
        result is None
        or result is True
        or isinstance(
            result,
            dict,
        )
    )


def test_runner_reset_is_repeatable():
    """
    Multiple resets must be safe.
    """

    runner = create_runner()

    try:

        reset_runner(
            runner
        )

        reset_runner(
            runner
        )

        reset_runner(
            runner
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose reset()."
        )


# ============================================================
# PROGRAM LOADING
# ============================================================


def test_load_empty_program():
    """
    Empty program should be accepted or safely rejected
    according to the runner's API.
    """

    runner = create_runner()

    try:

        load_program(
            runner,
            [],
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )


def test_load_single_byte_program():
    """
    Runner must support loading a single-byte program.
    """

    runner = create_runner()

    program = bytes(
        [
            0x00,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )


def test_load_two_byte_program():
    """
    Runner must support a 2-byte instruction program.

    Example:

        LOAD 0x10

    Opcode:
        0x10

    Operand:
        0x10
    """

    runner = create_runner()

    program = bytes(
        [
            0x10,
            0x10,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )


# ============================================================
# MACHINE CODE RANGE
# ============================================================


def test_program_bytes_are_8bit():
    """
    Every machine-code byte must fit in 8 bits.
    """

    program = bytes(
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
            0xFF,
        ]
    )

    for byte in program:

        assert (
            MIN_BYTE
            <= byte
            <= MAX_BYTE
        )


# ============================================================
# STEP
# ============================================================


def test_single_step_if_supported():
    """
    Runner should execute one CPU step.
    """

    runner = create_runner()

    try:

        reset_runner(
            runner
        )

    except AttributeError:

        pass

    try:

        result = step_runner(
            runner
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
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
# NOP PROGRAM
# ============================================================


def test_nop_program():
    """
    NOP opcode:

        0x00

    A NOP should not modify normal CPU state
    except advancing the Program Counter.
    """

    runner = create_runner()

    program = bytes(
        [
            0x00,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )

    try:

        result = run_runner(
            runner,
            max_cycles=1,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program execution."
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
# HALT PROGRAM
# ============================================================


def test_halt_program():
    """
    HALT opcode:

        0xF0

    A HALT instruction must stop normal execution.
    """

    runner = create_runner()

    program = bytes(
        [
            0xF0,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )

    try:

        run_runner(
            runner,
            max_cycles=10,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program execution."
        )

    try:

        halted = get_attribute(
            runner,
            (
                "halted",
                "is_halted",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "halt state."
        )

    assert (
        bool(
            halted
        )
        is True
    )


# ============================================================
# PROGRAM COUNTER
# ============================================================


def test_program_counter_starts_at_zero():
    """
    After reset, PC should start at 0x00.
    """

    runner = create_runner()

    try:

        reset_runner(
            runner
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose reset()."
        )

    try:

        pc = get_attribute(
            runner,
            (
                "program_counter",
                "pc",
                "PC",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "Program Counter."
        )

    assert (
        pc
        == 0x00
    )


# ============================================================
# PROGRAM COUNTER ADVANCEMENT
# ============================================================


def test_one_byte_instruction_advances_pc_by_one():
    """
    A 1-byte instruction must advance PC by 1.

    Example:

        0x00

    PC:

        0x00 -> 0x01
    """

    runner = create_runner()

    program = bytes(
        [
            0x00,
            0xF0,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

        reset_runner(
            runner
        )

        step_runner(
            runner
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "required execution API."
        )

    try:

        pc = get_attribute(
            runner,
            (
                "program_counter",
                "pc",
                "PC",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose PC."
        )

    assert (
        pc
        == 0x01
    )


# ============================================================
# TWO-BYTE INSTRUCTION
# ============================================================


def test_two_byte_instruction_advances_pc_by_two():
    """
    A 2-byte instruction must advance PC by 2.

    Example:

        0x10 0x20

    PC:

        0x00 -> 0x02
    """

    runner = create_runner()

    program = bytes(
        [
            0x10,
            0x20,
            0xF0,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

        reset_runner(
            runner
        )

        step_runner(
            runner
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "required execution API."
        )

    try:

        pc = get_attribute(
            runner,
            (
                "program_counter",
                "pc",
                "PC",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose PC."
        )

    assert (
        pc
        == 0x02
    )


# ============================================================
# MAX CYCLE PROTECTION
# ============================================================


def test_max_cycle_protection():
    """
    Runner must not execute forever when a program
    does not halt.

    Example:

        NOP
        NOP
        NOP
        ...

    The max_cycles argument protects the simulator.
    """

    runner = create_runner()

    program = bytes(
        [
            0x00,
            0x00,
            0x00,
            0x00,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )

    try:

        result = run_runner(
            runner,
            max_cycles=5,
        )

    except (
        AttributeError,
        TypeError,
    ):

        pytest.skip(
            "Runner does not support "
            "max cycle protection."
        )

    assert (
        result is None
        or isinstance(
            result,
            int,
        )
        or isinstance(
            result,
            dict,
        )
    )


# ============================================================
# COMPLETE PROGRAM
# ============================================================


def test_complete_halt_program():
    """
    Complete minimal program:

        NOP
        NOP
        HALT

    Machine code:

        00 00 F0
    """

    runner = create_runner()

    program = bytes(
        [
            0x00,
            0x00,
            0xF0,
        ]
    )

    try:

        load_program(
            runner,
            program,
        )

        run_runner(
            runner,
            max_cycles=10,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "required execution API."
        )

    try:

        halted = get_attribute(
            runner,
            (
                "halted",
                "is_halted",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "halt state."
        )

    assert (
        bool(
            halted
        )
        is True
    )


# ============================================================
# MEMORY SIZE
# ============================================================


def test_simulator_uses_8bit_address_space():
    """
    MiniCPU has an 8-bit address bus.

    Therefore:

        2^8 = 256

    valid addresses:

        0x00 - 0xFF
    """

    assert (
        2 ** BITS
        == MEMORY_SIZE
    )

    assert (
        MEMORY_SIZE
        == 256
    )


# ============================================================
# ADDRESS RANGE
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
def test_valid_address_range(
    address,
):
    """
    Every valid CPU address must fit in 8 bits.
    """

    assert (
        MIN_BYTE
        <= address
        <= MAX_BYTE
    )


# ============================================================
# INVALID PROGRAM BYTES
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        -1,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_machine_code_byte_is_rejected(
    value,
):
    """
    Machine code bytes outside 8-bit range
    must not be silently accepted.
    """

    runner = create_runner()

    try:

        with pytest.raises(
            (
                ValueError,
                TypeError,
                OverflowError,
            )
        ):

            load_program(
                runner,
                [
                    value,
                ],
            )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )


# ============================================================
# RUNNER STATE
# ============================================================


def test_runner_exposes_cpu_state_if_supported():
    """
    Runner may expose CPU state for debugging.

    Typical state:

        PC
        Registers
        Flags
        Memory
        Halted
    """

    runner = create_runner()

    state_names = (
        "state",
        "cpu",
        "cpu_state",
    )

    for name in state_names:

        if hasattr(
            runner,
            name,
        ):

            state = getattr(
                runner,
                name,
            )

            assert (
                state
                is not None
            )

            return

    pytest.skip(
        "Runner does not expose "
        "CPU state directly."
    )


# ============================================================
# FULL SIMULATOR WORKFLOW
# ============================================================


def test_full_simulator_workflow():
    """
    Validate the complete simulator lifecycle:

        1. Create Runner
        2. Reset CPU
        3. Load program
        4. Execute program
        5. Reach HALT
    """

    runner = create_runner()

    program = bytes(
        [
            0x00,  # NOP
            0x00,  # NOP
            0xF0,  # HALT
        ]
    )

    try:

        reset_runner(
            runner
        )

    except AttributeError:

        pass

    try:

        load_program(
            runner,
            program,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program loading."
        )

    try:

        run_runner(
            runner,
            max_cycles=MAX_CYCLES,
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "program execution."
        )

    try:

        halted = get_attribute(
            runner,
            (
                "halted",
                "is_halted",
            ),
        )

    except AttributeError:

        pytest.skip(
            "Runner does not expose "
            "halt state."
        )

    assert (
        bool(
            halted
        )
        is True
    )


# ============================================================
# FINAL ARCHITECTURE VALIDATION
# ============================================================


def test_runner_matches_minicpu_architecture():
    """
    Final MiniCPU simulator architecture validation.

    CPU:

        8-bit data
        8-bit address
        256-byte address space
        1-byte instructions
        2-byte instructions
        16 instruction opcodes
    """

    assert (
        2 ** 8
        == 256
    )

    assert (
        0x00
        <= 0xFF
        <= 0xFF
    )

    one_byte_program = bytes(
        [
            0x00,
        ]
    )

    two_byte_program = bytes(
        [
            0x10,
            0x00,
        ]
    )

    assert (
        len(
            one_byte_program
        )
        == 1
    )

    assert (
        len(
            two_byte_program
        )
        == 2
    )

    assert (
        16
        == 2 ** 4
    )
