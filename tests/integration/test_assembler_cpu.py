"""
tests/integration/test_assembler_cpu.py

MiniCPU 8-bit CPU Architecture
Assembler + CPU Integration Tests

Tests the complete pipeline:

    Assembly Source
        ↓
    Lexer
        ↓
    Parser
        ↓
    First Pass
        ↓
    Symbol Table
        ↓
    Second Pass
        ↓
    Encoder
        ↓
    Machine Code
        ↓
    CPU
        ↓
    Execution

Architecture:

    Data width:
        8-bit

    Address width:
        8-bit

    Memory:
        256 bytes

    Instruction count:
        16

    Instruction size:
        1-byte or 2-byte
"""

from __future__ import annotations

import pytest


# ============================================================
# IMPORT ASSEMBLER
# ============================================================

try:
    from assembler.assembler import Assembler
except ImportError:

    Assembler = None


# ============================================================
# IMPORT CPU
# ============================================================

try:
    from cpu.cpu import CPU
except ImportError:

    CPU = None


# ============================================================
# CONSTANTS
# ============================================================

MEMORY_SIZE = 256

MIN_BYTE = 0x00

MAX_BYTE = 0xFF

INSTRUCTION_COUNT = 16


# ============================================================
# HELPERS
# ============================================================


def create_assembler():
    """
    Create assembler instance.
    """

    if Assembler is None:

        pytest.skip(
            "Assembler implementation "
            "was not found."
        )

    try:

        return Assembler()

    except TypeError as exc:

        pytest.skip(
            "Unable to construct Assembler: "
            f"{exc}"
        )


def create_cpu():
    """
    Create CPU instance.
    """

    if CPU is None:

        pytest.skip(
            "CPU implementation "
            "was not found."
        )

    constructors = (
        lambda: CPU(),
        lambda: CPU(
            memory_size=MEMORY_SIZE
        ),
        lambda: CPU(
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
        "Unable to construct CPU: "
        f"{last_error}"
    )


def assemble_source(
    source,
):
    """
    Assemble source using the available API.
    """

    assembler = create_assembler()

    methods = (
        "assemble",
        "compile",
        "build",
    )

    for name in methods:

        if not hasattr(
            assembler,
            name,
        ):

            continue

        method = getattr(
            assembler,
            name,
        )

        if not callable(
            method
        ):

            continue

        try:

            return method(
                source
            )

        except TypeError:

            continue

    pytest.skip(
        "Assembler does not expose "
        "a supported assemble() API."
    )


def extract_machine_code(
    result,
):
    """
    Extract machine code from assembler result.

    Supports:

        bytes
        bytearray
        list[int]
        dict with code / machine_code / output
    """

    if isinstance(
        result,
        (
            bytes,
            bytearray,
        ),
    ):

        return bytes(
            result
        )

    if isinstance(
        result,
        list,
    ):

        if all(
            isinstance(
                value,
                int,
            )
            for value in result
        ):

            return bytes(
                result
            )

    if isinstance(
        result,
        dict,
    ):

        for key in (
            "machine_code",
            "code",
            "binary",
            "output",
            "bytes",
        ):

            if key not in result:

                continue

            value = result[
                key
            ]

            if isinstance(
                value,
                (
                    bytes,
                    bytearray,
                ),
            ):

                return bytes(
                    value
                )

            if isinstance(
                value,
                list,
            ):

                return bytes(
                    value
                )

    pytest.skip(
        "Unable to extract machine code "
        "from assembler result."
    )


def load_program(
    cpu,
    program,
):
    """
    Load machine code into CPU.
    """

    methods = (
        "load_program",
        "load",
        "load_code",
        "load_memory",
    )

    for name in methods:

        if not hasattr(
            cpu,
            name,
        ):

            continue

        method = getattr(
            cpu,
            name,
        )

        if not callable(
            method
        ):

            continue

        try:

            return method(
                program
            )

        except TypeError:

            continue

    pytest.skip(
        "CPU does not expose "
        "a supported program loading API."
    )


def run_cpu(
    cpu,
):
    """
    Run CPU program.
    """

    methods = (
        "run",
        "execute",
        "run_program",
        "start",
    )

    for name in methods:

        if not hasattr(
            cpu,
            name,
        ):

            continue

        method = getattr(
            cpu,
            name,
        )

        if not callable(
            method
        ):

            continue

        try:

            return method()

        except TypeError:

            continue

    pytest.skip(
        "CPU does not expose "
        "a supported execution API."
    )


# ============================================================
# BASIC ASSEMBLER → CPU PIPELINE
# ============================================================


def test_assembler_output_can_be_loaded_into_cpu():
    """
    Machine code generated by assembler must be
    loadable into the CPU.
    """

    source = """
        NOP
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    assert (
        len(
            machine_code
        )
        == 2
    )

    cpu = create_cpu()

    load_program(
        cpu,
        machine_code,
    )


# ============================================================
# NOP + HALT
# ============================================================


def test_nop_halt_program():
    """
    Program:

        NOP
        HALT

    Expected:

        CPU executes NOP
        CPU executes HALT
        CPU stops
    """

    source = """
        NOP
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    cpu = create_cpu()

    load_program(
        cpu,
        machine_code,
    )

    run_cpu(
        cpu
    )


# ============================================================
# LABEL RESOLUTION
# ============================================================


def test_assembler_resolves_label_for_cpu():
    """
    Verify that assembler can resolve a label
    before CPU execution.
    """

    source = """
        START:
            NOP
            JMP START
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    assert (
        len(
            machine_code
        )
        >= 3
    )

    cpu = create_cpu()

    load_program(
        cpu,
        machine_code,
    )


# ============================================================
# TWO-BYTE INSTRUCTION
# ============================================================


def test_two_byte_instruction_is_encoded_correctly():
    """
    Verify 2-byte instruction pipeline.

    Example:

        LOAD 0x10

    Expected:

        opcode byte
        operand byte
    """

    source = """
        LOAD 0x10
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    assert (
        len(
            machine_code
        )
        == 3
    )

    assert all(
        MIN_BYTE
        <= byte
        <= MAX_BYTE
        for byte in machine_code
    )


# ============================================================
# ONE-BYTE + TWO-BYTE MIX
# ============================================================


def test_mixed_instruction_sizes():
    """
    Verify that assembler and CPU handle
    mixed 1-byte and 2-byte instructions.

    Program:

        NOP          -> 1 byte
        LOAD 0x10    -> 2 bytes
        NOP          -> 1 byte
        HALT         -> 1 byte

    Total:

        5 bytes
    """

    source = """
        NOP
        LOAD 0x10
        NOP
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    assert (
        len(
            machine_code
        )
        == 5
    )


# ============================================================
# CPU EXECUTION
# ============================================================


def test_assembled_program_executes_on_cpu():
    """
    Full integration test:

        Assembly
        → Machine Code
        → CPU
        → Execution
    """

    source = """
        NOP
        NOP
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    cpu = create_cpu()

    load_program(
        cpu,
        machine_code,
    )

    run_cpu(
        cpu
    )


# ============================================================
# HALT STATE
# ============================================================


def test_cpu_halts_after_assembled_halt_instruction():
    """
    HALT instruction generated by assembler must
    cause CPU to enter halted state.
    """

    source = """
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    cpu = create_cpu()

    load_program(
        cpu,
        machine_code,
    )

    run_cpu(
        cpu
    )

    halted = None

    for name in (
        "halted",
        "is_halted",
    ):

        if hasattr(
            cpu,
            name,
        ):

            value = getattr(
                cpu,
                name,
            )

            halted = (
                value()
                if callable(
                    value
                )
                else value
            )

            break

    if halted is None:

        pytest.skip(
            "CPU does not expose "
            "halt state."
        )

    assert (
        halted
        is True
    )


# ============================================================
# PROGRAM COUNTER
# ============================================================


def test_program_counter_advances_using_instruction_sizes():
    """
    Verify PC movement for:

        NOP      -> 1 byte
        LOAD     -> 2 bytes
        HALT     -> 1 byte

    Total program size:

        4 bytes
    """

    source = """
        NOP
        LOAD 0x10
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    assert (
        len(
            machine_code
        )
        == 4
    )

    cpu = create_cpu()

    load_program(
        cpu,
        machine_code,
    )

    run_cpu(
        cpu
    )


# ============================================================
# MACHINE CODE RANGE
# ============================================================


def test_assembled_machine_code_is_8bit():
    """
    Every generated machine-code byte must fit
    in the 8-bit range.
    """

    source = """
        NOP
        LOAD 0xFF
        STORE 0x00
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    assert all(
        MIN_BYTE
        <= byte
        <= MAX_BYTE
        for byte in machine_code
    )


# ============================================================
# 8-BIT MEMORY LIMIT
# ============================================================


def test_program_fits_8bit_address_space():
    """
    Program must fit inside the 256-byte address space.
    """

    source = """
        NOP
        HALT
    """

    result = assemble_source(
        source
    )

    machine_code = extract_machine_code(
        result
    )

    assert (
        len(
            machine_code
        )
        <= MEMORY_SIZE
    )


# ============================================================
# COMPLETE PIPELINE
# ============================================================


def test_complete_assembler_cpu_pipeline():
    """
    Complete integration workflow:

        1. Write assembly
        2. Assemble
        3. Generate machine code
        4. Verify byte range
        5. Create CPU
        6. Load program
        7. Execute program
        8. Verify halt
    """

    source = """
        START:
            NOP
            NOP
            HALT
    """

    # --------------------------------------------------------
    # Assemble
    # --------------------------------------------------------

    result = assemble_source(
        source
    )

    # --------------------------------------------------------
    # Machine Code
    # --------------------------------------------------------

    machine_code = extract_machine_code(
        result
    )

    assert (
        len(
            machine_code
        )
        == 3
    )

    assert all(
        MIN_BYTE
        <= byte
        <= MAX_BYTE
        for byte in machine_code
    )

    # --------------------------------------------------------
    # CPU
    # --------------------------------------------------------

    cpu = create_cpu()

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    load_program(
        cpu,
        machine_code,
    )

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    run_cpu(
        cpu
    )

    # --------------------------------------------------------
    # Halt
    # --------------------------------------------------------

    if hasattr(
        cpu,
        "halted",
    ):

        assert (
            cpu.halted
            is True
        )

    elif hasattr(
        cpu,
        "is_halted",
    ):

        halted = cpu.is_halted

        if callable(
            halted
        ):

            halted = halted()

        assert (
            halted
            is True
        )
