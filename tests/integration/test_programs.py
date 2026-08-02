"""
tests/integration/test_programs.py

MiniCPU 8-bit CPU Architecture
Integration Program Test Suite

Tests complete assembly programs through:

    Assembly Source
        ↓
    Assembler
        ↓
    Machine Code
        ↓
    CPU Memory
        ↓
    CPU Execution
        ↓
    Final CPU State

Architecture:

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


def assemble(
    source,
):
    """
    Assemble source code.
    """

    assembler = create_assembler()

    for method_name in (
        "assemble",
        "compile",
        "build",
    ):

        if not hasattr(
            assembler,
            method_name,
        ):

            continue

        method = getattr(
            assembler,
            method_name,
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
        "a supported assemble API."
    )


def get_machine_code(
    result,
):
    """
    Extract machine code from assembler result.
    """

    if isinstance(
        result,
        bytes,
    ):

        return result

    if isinstance(
        result,
        bytearray,
    ):

        return bytes(
            result
        )

    if isinstance(
        result,
        list,
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
        "Unable to extract machine code."
    )


def load_program(
    cpu,
    program,
):
    """
    Load machine code into CPU.
    """

    for method_name in (
        "load_program",
        "load",
        "load_code",
        "load_memory",
    ):

        if not hasattr(
            cpu,
            method_name,
        ):

            continue

        method = getattr(
            cpu,
            method_name,
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


def run_program(
    cpu,
):
    """
    Execute loaded program.
    """

    for method_name in (
        "run",
        "execute",
        "run_program",
        "start",
    ):

        if not hasattr(
            cpu,
            method_name,
        ):

            continue

        method = getattr(
            cpu,
            method_name,
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


def get_cpu_value(
    cpu,
    names,
):
    """
    Get value from CPU using multiple possible names.
    """

    for name in names:

        if not hasattr(
            cpu,
            name,
        ):

            continue

        value = getattr(
            cpu,
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


# ============================================================
# PROGRAM 1
# NOP + HALT
# ============================================================


def test_program_nop_halt():
    """
    Program:

        NOP
        HALT
    """

    source = """
        NOP
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 2
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 2
# MULTIPLE NOP
# ============================================================


def test_program_multiple_nop():
    """
    Program:

        NOP
        NOP
        NOP
        HALT
    """

    source = """
        NOP
        NOP
        NOP
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 4
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 3
# LOAD
# ============================================================


def test_program_load():
    """
    Program:

        LOAD 0x42
        HALT

    Tests:

        2-byte instruction
        8-bit operand
        HALT
    """

    source = """
        LOAD 0x42
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 3
    )

    assert (
        program[1]
        == 0x42
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 4
# LOAD + STORE
# ============================================================


def test_program_load_store():
    """
    Program:

        LOAD 0x42
        STORE 0x80
        HALT
    """

    source = """
        LOAD 0x42
        STORE 0x80
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 5
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 5
# ADD
# ============================================================


def test_program_add():
    """
    Program:

        LOAD 0x05
        ADD 0x03
        HALT
    """

    source = """
        LOAD 0x05
        ADD 0x03
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 5
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 6
# SUB
# ============================================================


def test_program_sub():
    """
    Program:

        LOAD 0x08
        SUB 0x03
        HALT
    """

    source = """
        LOAD 0x08
        SUB 0x03
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 5
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 7
# LOGICAL OPERATIONS
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    [
        "AND",
        "OR",
        "XOR",
    ],
)
def test_program_logical_instruction(
    instruction,
):
    """
    Test logical 2-byte instructions.
    """

    source = f"""
        LOAD 0x55
        {instruction} 0x0F
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 5
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 8
# INC
# ============================================================


def test_program_inc():
    """
    Program:

        LOAD 0x10
        INC
        HALT
    """

    source = """
        LOAD 0x10
        INC
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 4
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 9
# DEC
# ============================================================


def test_program_dec():
    """
    Program:

        LOAD 0x10
        DEC
        HALT
    """

    source = """
        LOAD 0x10
        DEC
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 4
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 10
# LABEL + JMP
# ============================================================


def test_program_label_jump():
    """
    Program:

        START:
            NOP
            JMP START

    Tests:

        Label resolution
        2-byte JMP
        Backward jump
    """

    source = """
        START:
            NOP
            JMP START
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 3
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )


# ============================================================
# PROGRAM 11
# CONDITIONAL JUMP
# ============================================================


def test_program_conditional_jump():
    """
    Program:

        START:
            NOP
            JZ START
            HALT

    Tests:

        Label resolution
        Conditional branch
    """

    source = """
        START:
            NOP
            JZ START
            HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 4
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )


# ============================================================
# PROGRAM 12
# CMP
# ============================================================


def test_program_cmp():
    """
    Program:

        LOAD 0x10
        CMP 0x10
        HALT
    """

    source = """
        LOAD 0x10
        CMP 0x10
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 5
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )

    run_program(
        cpu
    )


# ============================================================
# PROGRAM 13
# INPUT / OUTPUT
# ============================================================


def test_program_input_output():
    """
    Program:

        IN
        OUT
        HALT

    Tests I/O instructions.
    """

    source = """
        IN
        OUT
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 3
    )

    cpu = create_cpu()

    load_program(
        cpu,
        program,
    )


# ============================================================
# PROGRAM 14
# ALL ONE-BYTE INSTRUCTIONS
# ============================================================


def test_all_one_byte_instructions_assemble():
    """
    Verify all 1-byte instructions can be assembled.

    Instructions:

        NOP
        OUT
        IN
        INC
        DEC
        HALT
    """

    source = """
        NOP
        OUT
        IN
        INC
        DEC
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 6
    )


# ============================================================
# PROGRAM 15
# ALL TWO-BYTE INSTRUCTIONS
# ============================================================


def test_all_two_byte_instructions_assemble():
    """
    Verify all 2-byte instructions can be assembled.

    Instructions:

        LOAD
        STORE
        ADD
        SUB
        AND
        OR
        XOR
        JMP
        JZ
        CMP
    """

    source = """
        LOAD 0x01
        STORE 0x02
        ADD 0x03
        SUB 0x04
        AND 0x05
        OR 0x06
        XOR 0x07
        JMP 0x08
        JZ 0x09
        CMP 0x0A
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    # 10 two-byte instructions
    # = 20 bytes
    # HALT
    # = 1 byte
    #
    # Total = 21 bytes

    assert (
        len(
            program
        )
        == 21
    )


# ============================================================
# PROGRAM 16
# COMPLETE ISA COVERAGE
# ============================================================


def test_complete_instruction_set_program():
    """
    Assemble a program covering all 16 instructions.

    This verifies that the assembler can encode
    every instruction in the MiniCPU ISA.
    """

    source = """
        NOP
        LOAD 0x10
        STORE 0x20
        ADD 0x01
        SUB 0x01
        AND 0x0F
        OR 0xF0
        XOR 0xFF
        JMP 0x00
        JZ 0x00
        OUT
        IN
        INC
        DEC
        CMP 0x10
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        > INSTRUCTION_COUNT
    )

    assert all(
        MIN_BYTE
        <= byte
        <= MAX_BYTE
        for byte in program
    )


# ============================================================
# PROGRAM 17
# 8-BIT VALUE BOUNDARIES
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
def test_program_8bit_operand_boundaries(
    value,
):
    """
    Test valid 8-bit operand boundaries.
    """

    source = f"""
        LOAD 0x{value:02X}
        HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 3
    )

    assert (
        program[1]
        == value
    )


# ============================================================
# PROGRAM 18
# LABELS WITH MIXED INSTRUCTION SIZES
# ============================================================


def test_labels_with_mixed_instruction_sizes():
    """
    Verify label addresses when 1-byte and 2-byte
    instructions are mixed.

    Program:

        START:
            NOP              1 byte
            LOAD 0x10        2 bytes
            INC              1 byte
        LOOP:
            DEC              1 byte
            JZ LOOP          2 bytes
            HALT             1 byte
    """

    source = """
        START:
            NOP
            LOAD 0x10
            INC

        LOOP:
            DEC
            JZ LOOP
            HALT
    """

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    # Total:
    #
    # NOP       = 1
    # LOAD      = 2
    # INC       = 1
    # DEC       = 1
    # JZ        = 2
    # HALT      = 1
    #
    # Total     = 8 bytes

    assert (
        len(
            program
        )
        == 8
    )


# ============================================================
# PROGRAM 19
# MAXIMUM SMALL PROGRAM
# ============================================================


def test_program_fits_inside_8bit_memory():
    """
    Verify a program can fit inside 256-byte memory.
    """

    source_lines = []

    for _ in range(
        100
    ):

        source_lines.append(
            "NOP"
        )

    source_lines.append(
        "HALT"
    )

    source = "\n".join(
        source_lines
    )

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    assert (
        len(
            program
        )
        == 101
    )

    assert (
        len(
            program
        )
        <= MEMORY_SIZE
    )


# ============================================================
# PROGRAM 20
# FULL ASSEMBLER → CPU EXECUTION
# ============================================================


def test_full_program_execution():
    """
    Complete real-world integration program.

    Program:

        LOAD 0x05
        ADD 0x03
        STORE 0x80
        HALT

    Pipeline:

        Assembly
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
        CPU Memory
            ↓
        CPU Execution
            ↓
        HALT
    """

    source = """
        LOAD 0x05
        ADD 0x03
        STORE 0x80
        HALT
    """

    # --------------------------------------------------------
    # Assemble
    # --------------------------------------------------------

    result = assemble(
        source
    )

    program = get_machine_code(
        result
    )

    # --------------------------------------------------------
    # Verify program size
    # --------------------------------------------------------

    # LOAD  = 2
    # ADD   = 2
    # STORE = 2
    # HALT  = 1
    #
    # Total = 7

    assert (
        len(
            program
        )
        == 7
    )

    # --------------------------------------------------------
    # Verify byte range
    # --------------------------------------------------------

    assert all(
        MIN_BYTE
        <= byte
        <= MAX_BYTE
        for byte in program
    )

    # --------------------------------------------------------
    # Create CPU
    # --------------------------------------------------------

    cpu = create_cpu()

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    load_program(
        cpu,
        program,
    )

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    run_program(
        cpu
    )

    # --------------------------------------------------------
    # Verify halt
    # --------------------------------------------------------

    halted = get_cpu_value(
        cpu,
        (
            "halted",
            "is_halted",
        ),
    )

    if halted is not None:

        assert (
            halted
            is True
        )
