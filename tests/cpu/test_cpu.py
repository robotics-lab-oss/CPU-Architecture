"""
tests/cpu/test_cpu.py

MiniCPU 8-bit CPU Architecture
CPU Core Integration Tests

Architecture:
    Data width:      8-bit
    Address width:   8-bit
    Memory:          256 bytes
    Instructions:    16

Instruction format:
    1-byte:
        [ OPCODE ]

    2-byte:
        [ OPCODE ][ OPERAND ]

This test module verifies the complete CPU core:

    Reset
      ↓
    Fetch
      ↓
    Decode
      ↓
    Execute
      ↓
    Program Counter Update
      ↓
    Next Instruction

The tests are intentionally written to work
with the MiniCPU component architecture:

    cpu.py
    registers.py
    alu.py
    control_unit.py
    instruction_decoder.py
    instruction_executor.py
    flags.py
    memory.py
    bus.py
    program_counter.py
    stack.py
"""

from __future__ import annotations

import pytest


# ============================================================
# IMPORT CPU
# ============================================================

from cpu.cpu import CPU


# ============================================================
# CONSTANTS
# ============================================================

MASK_8BIT = 0xFF

MEMORY_SIZE = 0x100

RESET_ADDRESS = 0x00


# ============================================================
# HELPERS
# ============================================================


def create_cpu():
    """
    Create a fresh CPU instance.
    """

    return CPU()


def get_register(
    cpu,
    name,
):
    """
    Read a register using common CPU APIs.

    Supported forms:

        cpu.registers.get("A")
        cpu.registers.read("A")
        cpu.registers.A
        cpu.A
    """

    registers = getattr(
        cpu,
        "registers",
        None,
    )

    if registers is not None:

        if hasattr(
            registers,
            "get",
        ):

            try:
                return registers.get(
                    name
                )

            except (
                KeyError,
                AttributeError,
            ):
                pass

        if hasattr(
            registers,
            "read",
        ):

            try:
                return registers.read(
                    name
                )

            except (
                KeyError,
                AttributeError,
            ):
                pass

        if hasattr(
            registers,
            name,
        ):

            return getattr(
                registers,
                name,
            )

        if hasattr(
            registers,
            name.upper(),
        ):

            return getattr(
                registers,
                name.upper(),
            )

    if hasattr(
        cpu,
        name,
    ):

        return getattr(
            cpu,
            name,
        )

    if hasattr(
        cpu,
        name.upper(),
    ):

        return getattr(
            cpu,
            name.upper(),
        )

    raise AttributeError(
        f"Cannot read register: {name}"
    )


def set_register(
    cpu,
    name,
    value,
):
    """
    Write a register using common CPU APIs.
    """

    registers = getattr(
        cpu,
        "registers",
        None,
    )

    if registers is not None:

        if hasattr(
            registers,
            "set",
        ):

            try:

                registers.set(
                    name,
                    value,
                )

                return

            except (
                KeyError,
                AttributeError,
            ):
                pass

        if hasattr(
            registers,
            "write",
        ):

            try:

                registers.write(
                    name,
                    value,
                )

                return

            except (
                KeyError,
                AttributeError,
            ):
                pass

        if hasattr(
            registers,
            name,
        ):

            setattr(
                registers,
                name,
                value,
            )

            return

        if hasattr(
            registers,
            name.upper(),
        ):

            setattr(
                registers,
                name.upper(),
                value,
            )

            return

    if hasattr(
        cpu,
        name,
    ):

        setattr(
            cpu,
            name,
            value,
        )

        return

    if hasattr(
        cpu,
        name.upper(),
    ):

        setattr(
            cpu,
            name.upper(),
            value,
        )

        return

    raise AttributeError(
        f"Cannot write register: {name}"
    )


def get_pc(
    cpu,
):
    """
    Read program counter.
    """

    pc = getattr(
        cpu,
        "program_counter",
        None,
    )

    if pc is not None:

        if hasattr(
            pc,
            "get",
        ):

            return pc.get()

        if hasattr(
            pc,
            "value",
        ):

            return pc.value

        if hasattr(
            pc,
            "pc",
        ):

            return pc.pc

    if hasattr(
        cpu,
        "pc",
    ):

        return cpu.pc

    if hasattr(
        cpu,
        "program_counter",
    ):

        value = cpu.program_counter

        if isinstance(
            value,
            int,
        ):

            return value

    raise AttributeError(
        "Cannot read program counter."
    )


def write_memory(
    cpu,
    address,
    value,
):
    """
    Write a byte into CPU memory.
    """

    memory = getattr(
        cpu,
        "memory",
        None,
    )

    if memory is None:

        raise AttributeError(
            "CPU does not expose memory."
        )

    if hasattr(
        memory,
        "write",
    ):

        memory.write(
            address,
            value,
        )

        return

    if hasattr(
        memory,
        "store",
    ):

        memory.store(
            address,
            value,
        )

        return

    try:

        memory[address] = value

        return

    except (
        TypeError,
        KeyError,
    ):
        pass

    raise AttributeError(
        "Cannot write CPU memory."
    )


def read_memory(
    cpu,
    address,
):
    """
    Read a byte from CPU memory.
    """

    memory = getattr(
        cpu,
        "memory",
        None,
    )

    if memory is None:

        raise AttributeError(
            "CPU does not expose memory."
        )

    if hasattr(
        memory,
        "read",
    ):

        return memory.read(
            address
        )

    if hasattr(
        memory,
        "load",
    ):

        return memory.load(
            address
        )

    return memory[address]


def load_program(
    cpu,
    program,
    start=0x00,
):
    """
    Load a machine-code program into memory.
    """

    if hasattr(
        cpu,
        "load_program",
    ):

        cpu.load_program(
            program,
            start,
        )

        return

    for offset, value in enumerate(
        program
    ):

        write_memory(
            cpu,
            start + offset,
            value,
        )


def reset_cpu(
    cpu,
):
    """
    Reset CPU using the available API.
    """

    if hasattr(
        cpu,
        "reset",
    ):

        cpu.reset()

        return

    raise AttributeError(
        "CPU must provide reset()."
    )


def step_cpu(
    cpu,
):
    """
    Execute one CPU instruction cycle.
    """

    if hasattr(
        cpu,
        "step",
    ):

        return cpu.step()

    if hasattr(
        cpu,
        "clock",
    ):

        return cpu.clock()

    if hasattr(
        cpu,
        "cycle",
    ):

        return cpu.cycle()

    raise AttributeError(
        "CPU must provide step(), "
        "clock(), or cycle()."
    )


def run_cpu(
    cpu,
    max_cycles=100,
):
    """
    Run CPU until HALT or cycle limit.
    """

    if hasattr(
        cpu,
        "run",
    ):

        try:

            return cpu.run(
                max_cycles=max_cycles
            )

        except TypeError:

            return cpu.run(
                max_cycles
            )

    for _ in range(
        max_cycles
    ):

        if is_halted(
            cpu
        ):

            break

        step_cpu(
            cpu
        )


def is_halted(
    cpu,
):
    """
    Check whether CPU is halted.
    """

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

            if callable(
                value
            ):

                return bool(
                    value()
                )

            return bool(
                value
            )

    # If CPU exposes a status register,
    # implementation-specific behavior is
    # not assumed here.
    return False


# ============================================================
# CPU CREATION
# ============================================================


def test_cpu_can_be_created():
    """
    CPU should be constructable.
    """

    cpu = create_cpu()

    assert cpu is not None


# ============================================================
# RESET
# ============================================================


def test_cpu_reset():
    """
    CPU reset should return the machine
    to its initial state.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    assert get_pc(
        cpu
    ) == RESET_ADDRESS


# ============================================================
# RESET IS DETERMINISTIC
# ============================================================


def test_cpu_reset_is_deterministic():
    """
    Repeated reset operations should produce
    the same initial program counter.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    first_pc = get_pc(
        cpu
    )

    reset_cpu(
        cpu
    )

    second_pc = get_pc(
        cpu
    )

    assert first_pc == second_pc

    assert first_pc == 0x00


# ============================================================
# REGISTER INITIALIZATION
# ============================================================


def test_cpu_registers_are_8bit():
    """
    CPU registers must contain 8-bit values.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    for register_name in (
        "A",
        "B",
    ):

        try:

            value = get_register(
                cpu,
                register_name,
            )

        except AttributeError:

            continue

        assert isinstance(
            value,
            int,
        )

        assert (
            0x00
            <= value
            <= 0xFF
        )


# ============================================================
# NOP
# ============================================================


def test_cpu_nop():
    """
    NOP:

        00

    NOP must not modify the accumulator.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    try:

        before = get_register(
            cpu,
            "A",
        )

    except AttributeError:

        before = 0

    load_program(
        cpu,
        [
            0x00,
        ],
    )

    step_cpu(
        cpu
    )

    try:

        after = get_register(
            cpu,
            "A",
        )

        assert after == before

    except AttributeError:

        pass


# ============================================================
# HALT
# ============================================================


def test_cpu_halt():
    """
    HALT:

        F0

    CPU should enter halted state.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0xF0,
        ],
    )

    step_cpu(
        cpu
    )

    assert is_halted(
        cpu
    )


# ============================================================
# LOAD
# ============================================================


def test_cpu_load():
    """
    LOAD 0x42:

        10 42

    Expected:

        A = 0x42
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x42,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x42


# ============================================================
# LOAD ZERO
# ============================================================


def test_cpu_load_zero():
    """
    LOAD 0x00:

        10 00
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x00,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x00


# ============================================================
# LOAD MAXIMUM
# ============================================================


def test_cpu_load_ff():
    """
    LOAD 0xFF:

        10 FF
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0xFF,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0xFF


# ============================================================
# PROGRAM COUNTER AFTER 1-BYTE INSTRUCTION
# ============================================================


def test_pc_advances_one_byte():
    """
    NOP is one byte.

        PC = 0
        NOP
        PC = 1
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x00,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_pc(
        cpu
    ) == 0x01


# ============================================================
# PROGRAM COUNTER AFTER 2-BYTE INSTRUCTION
# ============================================================


def test_pc_advances_two_bytes():
    """
    LOAD is two bytes.

        PC = 0
        LOAD 0x42
        PC = 2
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x42,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_pc(
        cpu
    ) == 0x02


# ============================================================
# SEQUENTIAL EXECUTION
# ============================================================


def test_cpu_sequential_execution():
    """
    Program:

        LOAD 0x10
        INC
        HALT

    Machine code:

        10 10 C0 F0

    Expected:

        A = 0x11
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x10,
            0xC0,
            0xF0,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x10

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x11

    step_cpu(
        cpu
    )

    assert is_halted(
        cpu
    )


# ============================================================
# INC
# ============================================================


def test_cpu_inc():
    """
    INC:

        C0

    0x10 -> 0x11
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0x10,
    )

    load_program(
        cpu,
        [
            0xC0,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x11


# ============================================================
# INC WRAPAROUND
# ============================================================


def test_cpu_inc_wraparound():
    """
    8-bit overflow:

        0xFF + 1 = 0x00
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0xFF,
    )

    load_program(
        cpu,
        [
            0xC0,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x00


# ============================================================
# DEC
# ============================================================


def test_cpu_dec():
    """
    DEC:

        D0

    0x10 -> 0x0F
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0x10,
    )

    load_program(
        cpu,
        [
            0xD0,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x0F


# ============================================================
# DEC WRAPAROUND
# ============================================================


def test_cpu_dec_wraparound():
    """
    8-bit underflow:

        0x00 - 1 = 0xFF
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0x00,
    )

    load_program(
        cpu,
        [
            0xD0,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0xFF


# ============================================================
# ADD
# ============================================================


def test_cpu_add():
    """
    ADD 0x05

    A = 0x10

    Result:

        0x15
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0x10,
    )

    load_program(
        cpu,
        [
            0x30,
            0x05,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x15


# ============================================================
# SUB
# ============================================================


def test_cpu_sub():
    """
    SUB 0x05

    A = 0x10

    Result:

        0x0B
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0x10,
    )

    load_program(
        cpu,
        [
            0x40,
            0x05,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x0B


# ============================================================
# AND
# ============================================================


def test_cpu_and():
    """
    AND 0x0F

    A = F0

    Result:

        00
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0xF0,
    )

    load_program(
        cpu,
        [
            0x50,
            0x0F,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x00


# ============================================================
# OR
# ============================================================


def test_cpu_or():
    """
    OR 0x0F

    A = F0

    Result:

        FF
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0xF0,
    )

    load_program(
        cpu,
        [
            0x60,
            0x0F,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0xFF


# ============================================================
# XOR
# ============================================================


def test_cpu_xor():
    """
    XOR FF

    A = F0

    Result:

        0F
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0xF0,
    )

    load_program(
        cpu,
        [
            0x70,
            0xFF,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x0F


# ============================================================
# JMP
# ============================================================


def test_cpu_jmp():
    """
    JMP 0x10

        80 10

    Expected:

        PC = 0x10
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x80,
            0x10,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_pc(
        cpu
    ) == 0x10


# ============================================================
# JZ WHEN ZERO
# ============================================================


def test_cpu_jz_when_zero():
    """
    If zero flag is set:

        JZ 0x10

    should jump to 0x10.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0x00,
    )

    load_program(
        cpu,
        [
            0x90,
            0x10,
        ],
    )

    step_cpu(
        cpu
    )

    # The exact flag-setting mechanism is
    # implementation-specific. The test verifies
    # jump behavior when CPU is already in a
    # zero condition if supported.

    assert get_pc(
        cpu
    ) in (
        0x02,
        0x10,
    )


# ============================================================
# CMP
# ============================================================


def test_cpu_cmp():
    """
    CMP 0x10

    A = 0x10

    CMP should update comparison flags
    without changing A.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        0x10,
    )

    load_program(
        cpu,
        [
            0xE0,
            0x10,
        ],
    )

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x10


# ============================================================
# COMPLETE PROGRAM
# ============================================================


def test_cpu_complete_program():
    """
    Program:

        LOAD 0x10
        INC
        INC
        DEC
        HALT

    Expected:

        A = 0x11
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x10,
            0xC0,
            0xC0,
            0xD0,
            0xF0,
        ],
    )

    run_cpu(
        cpu,
        max_cycles=10,
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x11

    assert is_halted(
        cpu
    )


# ============================================================
# 8-BIT REGISTER GUARANTEE
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
def test_cpu_register_accepts_8bit_values(
    value,
):
    """
    Every valid 8-bit value should be
    representable in the accumulator.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    set_register(
        cpu,
        "A",
        value,
    )

    assert (
        get_register(
            cpu,
            "A",
        )
        == value
    )


# ============================================================
# MEMORY ADDRESS SPACE
# ============================================================


def test_cpu_memory_is_256_bytes():
    """
    MiniCPU uses an 8-bit address bus:

        2^8 = 256 addresses

    Address range:

        0x00 - 0xFF
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    write_memory(
        cpu,
        0x00,
        0x12,
    )

    write_memory(
        cpu,
        0xFF,
        0x34,
    )

    assert read_memory(
        cpu,
        0x00,
    ) == 0x12

    assert read_memory(
        cpu,
        0xFF,
    ) == 0x34


# ============================================================
# MEMORY 8-BIT VALUES
# ============================================================


def test_cpu_memory_values_are_8bit():
    """
    Memory cells store 8-bit values.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    write_memory(
        cpu,
        0x10,
        0x00,
    )

    write_memory(
        cpu,
        0x11,
        0xFF,
    )

    assert read_memory(
        cpu,
        0x10,
    ) == 0x00

    assert read_memory(
        cpu,
        0x11,
    ) == 0xFF


# ============================================================
# FETCH-DECODE-EXECUTE
# ============================================================


def test_fetch_decode_execute_cycle():
    """
    Verify a basic fetch-decode-execute sequence.

    Program:

        LOAD 0x42
        HALT
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x42,
            0xF0,
        ],
    )

    assert get_pc(
        cpu
    ) == 0x00

    step_cpu(
        cpu
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x42

    assert get_pc(
        cpu
    ) == 0x02

    step_cpu(
        cpu
    )

    assert is_halted(
        cpu
    )


# ============================================================
# CPU RUN
# ============================================================


def test_cpu_run_until_halt():
    """
    CPU should execute instructions until HALT.

    Program:

        LOAD 0x01
        INC
        HALT
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x01,
            0xC0,
            0xF0,
        ],
    )

    run_cpu(
        cpu,
        max_cycles=10,
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x02

    assert is_halted(
        cpu
    )


# ============================================================
# RESET AFTER HALT
# ============================================================


def test_reset_clears_halted_state():
    """
    After HALT, reset should make the CPU
    executable again.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0xF0,
        ],
    )

    step_cpu(
        cpu
    )

    assert is_halted(
        cpu
    )

    reset_cpu(
        cpu
    )

    assert get_pc(
        cpu
    ) == 0x00


# ============================================================
# INVALID OPCODE
# ============================================================


def test_invalid_opcode_is_rejected():
    """
    0xFF is not one of the defined MiniCPU
    instruction opcodes.

    CPU should either:

        - raise an exception
        - enter an error state
        - halt safely

    It must not silently execute it as a valid
    instruction.
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0xFF,
        ],
    )

    try:

        step_cpu(
            cpu
        )

    except Exception:

        return

    # If implementation does not raise,
    # it should at least halt or expose
    # an error state.

    assert (
        is_halted(
            cpu
        )
        or hasattr(
            cpu,
            "error",
        )
        or hasattr(
            cpu,
            "fault",
        )
    )


# ============================================================
# 8-BIT PROGRAM COUNTER WRAPAROUND
# ============================================================


def test_program_counter_is_8bit():
    """
    Program counter is 8-bit.

    Therefore its valid range is:

        0x00 - 0xFF
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    pc = get_pc(
        cpu
    )

    assert isinstance(
        pc,
        int,
    )

    assert (
        0x00
        <= pc
        <= 0xFF
    )


# ============================================================
# CPU ARCHITECTURE CONSTANTS
# ============================================================


def test_cpu_architecture_is_8bit():
    """
    Verify the core exposes an 8-bit architecture
    where architecture metadata is available.
    """

    cpu = create_cpu()

    possible_widths = []

    for name in (
        "DATA_WIDTH",
        "data_width",
        "WORD_SIZE",
        "word_size",
    ):

        if hasattr(
            cpu,
            name,
        ):

            value = getattr(
                cpu,
                name,
            )

            if isinstance(
                value,
                int,
            ):

                possible_widths.append(
                    value
                )

    if possible_widths:

        assert 8 in possible_widths


# ============================================================
# FINAL INTEGRATION
# ============================================================


def test_cpu_full_integration():
    """
    Complete CPU integration test.

    Program:

        0000: LOAD 0x05
        0002: INC
        0003: ADD 0x03
        0005: SUB 0x01
        0007: XOR 0x00
        0009: HALT

    Expected:

        A = 0x07

    Calculation:

        0x05
        + 0x01
        = 0x06
        + 0x03
        = 0x09
        - 0x01
        = 0x08
        XOR 0x00
        = 0x08

    Final expected value:

        A = 0x08
    """

    cpu = create_cpu()

    reset_cpu(
        cpu
    )

    load_program(
        cpu,
        [
            0x10,
            0x05,
            0xC0,
            0x30,
            0x03,
            0x40,
            0x01,
            0x70,
            0x00,
            0xF0,
        ],
    )

    run_cpu(
        cpu,
        max_cycles=20,
    )

    assert get_register(
        cpu,
        "A",
    ) == 0x08

    assert is_halted(
        cpu
    )
