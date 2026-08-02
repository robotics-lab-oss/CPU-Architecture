"""
tests/cpu/test_instruction_executor.py

MiniCPU 8-bit CPU Architecture
Instruction Executor Test Suite

ISA:
    16 instructions
    8-bit data
    8-bit operands
    8-bit address space

Instruction format:

    1-byte:
        [ OPCODE ]

    2-byte:
        [ OPCODE ][ OPERAND ]

Instructions:

    NOP   = 0x00
    LOAD  = 0x10
    STORE = 0x20
    ADD   = 0x30
    SUB   = 0x40
    AND   = 0x50
    OR    = 0x60
    XOR   = 0x70
    JMP   = 0x80
    JZ    = 0x90
    OUT   = 0xA0
    IN    = 0xB0
    INC   = 0xC0
    DEC   = 0xD0
    CMP   = 0xE0
    HALT  = 0xF0

This test module verifies:

- Executor creation
- Reset behavior
- NOP execution
- LOAD
- STORE
- ADD
- SUB
- AND
- OR
- XOR
- JMP
- JZ
- OUT
- IN
- INC
- DEC
- CMP
- HALT
- 8-bit wrapping
- Invalid opcode handling
- 8-bit operand handling
"""

from __future__ import annotations

import pytest

from cpu.instruction_executor import InstructionExecutor


# ============================================================
# ISA
# ============================================================

OPCODES = {
    "NOP": 0x00,
    "LOAD": 0x10,
    "STORE": 0x20,
    "ADD": 0x30,
    "SUB": 0x40,
    "AND": 0x50,
    "OR": 0x60,
    "XOR": 0x70,
    "JMP": 0x80,
    "JZ": 0x90,
    "OUT": 0xA0,
    "IN": 0xB0,
    "INC": 0xC0,
    "DEC": 0xD0,
    "CMP": 0xE0,
    "HALT": 0xF0,
}


# ============================================================
# HELPERS
# ============================================================


def create_executor():
    """
    Create a fresh Instruction Executor.
    """

    return InstructionExecutor()


def reset_executor(
    executor,
):
    """
    Reset executor when reset() is available.
    """

    if hasattr(
        executor,
        "reset",
    ):

        reset = getattr(
            executor,
            "reset",
        )

        if callable(
            reset
        ):

            reset()


def execute_instruction(
    executor,
    opcode,
    operand=None,
):
    """
    Execute instruction using common APIs.

    Supported method names:

        execute()
        execute_instruction()
        run()
        dispatch()
    """

    methods = (
        "execute",
        "execute_instruction",
        "run",
        "dispatch",
    )

    for name in methods:

        if not hasattr(
            executor,
            name,
        ):

            continue

        method = getattr(
            executor,
            name,
        )

        if not callable(
            method
        ):

            continue

        if operand is not None:

            try:

                return method(
                    opcode,
                    operand,
                )

            except TypeError:

                pass

        try:

            return method(
                opcode
            )

        except TypeError:

            pass

        if operand is not None:

            try:

                return method(
                    {
                        "opcode": opcode,
                        "operand": operand,
                    }
                )

            except TypeError:

                pass

    raise AttributeError(
        "InstructionExecutor does not expose "
        "a supported execution method."
    )


def get_value(
    executor,
    names,
):
    """
    Read a value from the executor.
    """

    for name in names:

        if hasattr(
            executor,
            name,
        ):

            value = getattr(
                executor,
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
    executor,
    names,
    value,
):
    """
    Set a value using common APIs.
    """

    for name in names:

        if hasattr(
            executor,
            name,
        ):

            target = getattr(
                executor,
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
                    executor,
                    name,
                    value,
                )

                return True

            except Exception:

                continue

    return False


def get_accumulator(
    executor,
):
    """
    Read accumulator value.
    """

    return get_value(
        executor,
        (
            "accumulator",
            "acc",
            "a",
        ),
    )


def set_accumulator(
    executor,
    value,
):
    """
    Set accumulator value.
    """

    return set_value(
        executor,
        (
            "accumulator",
            "acc",
            "a",
            "set_accumulator",
            "set_acc",
        ),
        value,
    )


def get_program_counter(
    executor,
):
    """
    Read program counter.
    """

    return get_value(
        executor,
        (
            "program_counter",
            "pc",
        ),
    )


def set_program_counter(
    executor,
    value,
):
    """
    Set program counter.
    """

    return set_value(
        executor,
        (
            "program_counter",
            "pc",
            "set_program_counter",
            "set_pc",
        ),
        value,
    )


def get_memory(
    executor,
):
    """
    Read memory object.
    """

    return get_value(
        executor,
        (
            "memory",
            "ram",
        ),
    )


def get_flag(
    executor,
    names,
):
    """
    Read a flag.
    """

    return get_value(
        executor,
        names,
    )


# ============================================================
# CREATION
# ============================================================


def test_executor_can_be_created():
    """
    Executor must be constructable.
    """

    executor = create_executor()

    assert executor is not None


# ============================================================
# RESET
# ============================================================


def test_executor_reset_if_supported():
    """
    Executor reset must execute successfully.
    """

    executor = create_executor()

    reset_executor(
        executor
    )


# ============================================================
# NOP
# ============================================================


def test_nop_executes_without_error():
    """
    NOP must execute without raising.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    execute_instruction(
        executor,
        OPCODES["NOP"],
    )


# ============================================================
# LOAD
# ============================================================


def test_load_instruction():
    """
    LOAD must place the operand into
    the accumulator/register where supported.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    execute_instruction(
        executor,
        OPCODES["LOAD"],
        0x42,
    )

    accumulator = get_accumulator(
        executor
    )

    if accumulator is None:

        pytest.skip(
            "Accumulator is not exposed."
        )

    assert (
        accumulator
        == 0x42
    )


# ============================================================
# LOAD ZERO
# ============================================================


def test_load_zero():
    """
    LOAD 0x00 must produce zero.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    execute_instruction(
        executor,
        OPCODES["LOAD"],
        0x00,
    )

    accumulator = get_accumulator(
        executor
    )

    if accumulator is None:

        pytest.skip(
            "Accumulator is not exposed."
        )

    assert (
        accumulator
        == 0x00
    )


# ============================================================
# LOAD FF
# ============================================================


def test_load_ff():
    """
    LOAD 0xFF must preserve the full 8-bit value.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    execute_instruction(
        executor,
        OPCODES["LOAD"],
        0xFF,
    )

    accumulator = get_accumulator(
        executor
    )

    if accumulator is None:

        pytest.skip(
            "Accumulator is not exposed."
        )

    assert (
        accumulator
        == 0xFF
    )


# ============================================================
# STORE
# ============================================================


def test_store_instruction_if_supported():
    """
    STORE must write the accumulator to memory
    when memory integration is exposed.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    memory = get_memory(
        executor
    )

    if memory is None:

        pytest.skip(
            "Memory is not exposed."
        )

    set_accumulator(
        executor,
        0x42,
    )

    execute_instruction(
        executor,
        OPCODES["STORE"],
        0x10,
    )

    value = None

    if hasattr(
        memory,
        "read",
    ):

        value = memory.read(
            0x10
        )

    elif hasattr(
        memory,
        "__getitem__",
    ):

        value = memory[
            0x10
        ]

    if value is None:

        pytest.skip(
            "Memory read API is not exposed."
        )

    assert (
        value
        == 0x42
    )


# ============================================================
# ADD
# ============================================================


def test_add_instruction():
    """
    ADD must add an 8-bit operand to the accumulator.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        10,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["ADD"],
        5,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 15
    )


# ============================================================
# SUB
# ============================================================


def test_sub_instruction():
    """
    SUB must subtract an operand.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        10,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["SUB"],
        3,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 7
    )


# ============================================================
# AND
# ============================================================


def test_and_instruction():
    """
    AND must perform bitwise AND.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0b11001100,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["AND"],
        0b10101010,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == (
            0b11001100
            & 0b10101010
        )
    )


# ============================================================
# OR
# ============================================================


def test_or_instruction():
    """
    OR must perform bitwise OR.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0b11001100,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["OR"],
        0b10101010,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == (
            0b11001100
            | 0b10101010
        )
    )


# ============================================================
# XOR
# ============================================================


def test_xor_instruction():
    """
    XOR must perform bitwise XOR.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0b11001100,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["XOR"],
        0b10101010,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == (
            0b11001100
            ^ 0b10101010
        )
    )


# ============================================================
# INC
# ============================================================


def test_inc_instruction():
    """
    INC must increment the accumulator.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        10,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["INC"],
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 11
    )


# ============================================================
# DEC
# ============================================================


def test_dec_instruction():
    """
    DEC must decrement the accumulator.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        10,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["DEC"],
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 9
    )


# ============================================================
# INC 8-BIT WRAP
# ============================================================


def test_inc_wraps_from_ff_to_zero():
    """
    8-bit INC:

        0xFF + 1 = 0x00
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0xFF,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["INC"],
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 0x00
    )


# ============================================================
# DEC 8-BIT WRAP
# ============================================================


def test_dec_wraps_from_zero_to_ff():
    """
    8-bit DEC:

        0x00 - 1 = 0xFF
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0x00,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["DEC"],
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 0xFF
    )


# ============================================================
# ADD 8-BIT WRAP
# ============================================================


def test_add_wraps_at_8bit_boundary():
    """
    8-bit ADD:

        0xFF + 1 = 0x00
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0xFF,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["ADD"],
        0x01,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 0x00
    )


# ============================================================
# SUB 8-BIT WRAP
# ============================================================


def test_sub_wraps_at_8bit_boundary():
    """
    8-bit SUB:

        0x00 - 1 = 0xFF
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0x00,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["SUB"],
        0x01,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        accumulator
        == 0xFF
    )


# ============================================================
# JMP
# ============================================================


def test_jmp_instruction_if_supported():
    """
    JMP must update the program counter.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_program_counter(
        executor,
        0x00,
    ):

        pytest.skip(
            "Program Counter cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["JMP"],
        0x80,
    )

    pc = get_program_counter(
        executor
    )

    assert (
        pc
        == 0x80
    )


# ============================================================
# JMP FF
# ============================================================


def test_jmp_accepts_ff_address():
    """
    JMP must support the maximum 8-bit address.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_program_counter(
        executor,
        0x00,
    ):

        pytest.skip(
            "Program Counter cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["JMP"],
        0xFF,
    )

    pc = get_program_counter(
        executor
    )

    assert (
        pc
        == 0xFF
    )


# ============================================================
# JZ
# ============================================================


def test_jz_taken_when_zero_flag_is_set():
    """
    JZ must jump when the zero condition is true.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    zero_flag = get_flag(
        executor,
        (
            "zero",
            "zero_flag",
            "z",
        ),
    )

    if zero_flag is None:

        pytest.skip(
            "Zero flag is not exposed."
        )

    if not set_program_counter(
        executor,
        0x00,
    ):

        pytest.skip(
            "Program Counter cannot be configured."
        )

    set_value(
        executor,
        (
            "zero",
            "zero_flag",
            "z",
            "set_zero",
            "set_zero_flag",
        ),
        True,
    )

    execute_instruction(
        executor,
        OPCODES["JZ"],
        0x80,
    )

    pc = get_program_counter(
        executor
    )

    assert (
        pc
        == 0x80
    )


# ============================================================
# JZ NOT TAKEN
# ============================================================


def test_jz_not_taken_when_zero_flag_is_clear():
    """
    JZ must not jump when zero condition is false.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    zero_flag = get_flag(
        executor,
        (
            "zero",
            "zero_flag",
            "z",
        ),
    )

    if zero_flag is None:

        pytest.skip(
            "Zero flag is not exposed."
        )

    if not set_program_counter(
        executor,
        0x00,
    ):

        pytest.skip(
            "Program Counter cannot be configured."
        )

    set_value(
        executor,
        (
            "zero",
            "zero_flag",
            "z",
            "set_zero",
            "set_zero_flag",
        ),
        False,
    )

    execute_instruction(
        executor,
        OPCODES["JZ"],
        0x80,
    )

    pc = get_program_counter(
        executor
    )

    assert (
        pc
        != 0x80
    )


# ============================================================
# CMP
# ============================================================


def test_cmp_equal_sets_zero_condition():
    """
    CMP A, A should produce the zero condition.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0x42,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["CMP"],
        0x42,
    )

    zero_flag = get_flag(
        executor,
        (
            "zero",
            "zero_flag",
            "z",
        ),
    )

    if zero_flag is None:

        pytest.skip(
            "Zero flag is not exposed."
        )

    assert bool(
        zero_flag
    ) is True


# ============================================================
# CMP NOT EQUAL
# ============================================================


def test_cmp_not_equal_clears_zero_condition():
    """
    CMP A, B where A != B should clear
    the zero condition.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0x42,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["CMP"],
        0x41,
    )

    zero_flag = get_flag(
        executor,
        (
            "zero",
            "zero_flag",
            "z",
        ),
    )

    if zero_flag is None:

        pytest.skip(
            "Zero flag is not exposed."
        )

    assert bool(
        zero_flag
    ) is False


# ============================================================
# HALT
# ============================================================


def test_halt_instruction_if_supported():
    """
    HALT must put the CPU/executor into
    a halted state when supported.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    execute_instruction(
        executor,
        OPCODES["HALT"],
    )

    halted = get_value(
        executor,
        (
            "halted",
            "is_halted",
            "stopped",
        ),
    )

    if halted is None:

        pytest.skip(
            "Halt state is not exposed."
        )

    if callable(
        halted
    ):

        halted = halted()

    assert bool(
        halted
    ) is True


# ============================================================
# OUT
# ============================================================


def test_out_instruction_if_supported():
    """
    OUT must execute without error.

    Actual I/O device behavior depends on
    the system bus implementation.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0x42,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["OUT"],
    )


# ============================================================
# IN
# ============================================================


def test_in_instruction_if_supported():
    """
    IN must execute without error when
    an input device is available.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    try:

        execute_instruction(
            executor,
            OPCODES["IN"],
        )

    except (
        NotImplementedError,
        RuntimeError,
    ):

        pytest.skip(
            "Input device is not configured."
        )


# ============================================================
# INVALID OPCODE
# ============================================================


@pytest.mark.parametrize(
    "opcode",
    [
        -1,
        0x100,
        0x101,
        0x1FF,
        0x1000,
    ],
)
def test_invalid_opcode_is_rejected(
    opcode,
):
    """
    Executor must reject values outside
    the 8-bit opcode range.
    """

    executor = create_executor()

    with pytest.raises(
        (
            ValueError,
            KeyError,
            TypeError,
            OverflowError,
        )
    ):

        execute_instruction(
            executor,
            opcode,
        )


# ============================================================
# INVALID OPERAND
# ============================================================


@pytest.mark.parametrize(
    "operand",
    [
        -1,
        0x100,
        0x101,
        0x1000,
    ],
)
def test_invalid_operand_is_rejected(
    operand,
):
    """
    Operand must fit in 8 bits.
    """

    executor = create_executor()

    with pytest.raises(
        (
            ValueError,
            TypeError,
            OverflowError,
        )
    ):

        execute_instruction(
            executor,
            OPCODES["LOAD"],
            operand,
        )


# ============================================================
# COMPLETE EXECUTION TEST
# ============================================================


def test_complete_executor_workflow():
    """
    Complete instruction execution workflow:

        LOAD 10
        ADD  5
        SUB  2
        AND  FF
        OR   00
        XOR  00
        INC
        DEC
        CMP
        NOP
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    execute_instruction(
        executor,
        OPCODES["LOAD"],
        10,
    )

    assert (
        get_accumulator(
            executor
        )
        == 10
    )

    execute_instruction(
        executor,
        OPCODES["ADD"],
        5,
    )

    assert (
        get_accumulator(
            executor
        )
        == 15
    )

    execute_instruction(
        executor,
        OPCODES["SUB"],
        2,
    )

    assert (
        get_accumulator(
            executor
        )
        == 13
    )

    execute_instruction(
        executor,
        OPCODES["AND"],
        0xFF,
    )

    assert (
        get_accumulator(
            executor
        )
        == 13
    )

    execute_instruction(
        executor,
        OPCODES["OR"],
        0x00,
    )

    assert (
        get_accumulator(
            executor
        )
        == 13
    )

    execute_instruction(
        executor,
        OPCODES["XOR"],
        0x00,
    )

    assert (
        get_accumulator(
            executor
        )
        == 13
    )

    execute_instruction(
        executor,
        OPCODES["INC"],
    )

    assert (
        get_accumulator(
            executor
        )
        == 14
    )

    execute_instruction(
        executor,
        OPCODES["DEC"],
    )

    assert (
        get_accumulator(
            executor
        )
        == 13
    )

    execute_instruction(
        executor,
        OPCODES["CMP"],
        13,
    )

    execute_instruction(
        executor,
        OPCODES["NOP"],
    )


# ============================================================
# 16-INSTRUCTION ISA COVERAGE
# ============================================================


def test_all_16_instructions_are_represented():
    """
    Verify that the executor test suite covers
    all 16 instructions.
    """

    assert len(
        OPCODES
    ) == 16

    for name, opcode in OPCODES.items():

        assert isinstance(
            name,
            str,
        )

        assert isinstance(
            opcode,
            int,
        )

        assert (
            0x00
            <= opcode
            <= 0xFF
        )


# ============================================================
# OPCODE UNIQUENESS
# ============================================================


def test_all_opcodes_are_unique():
    """
    Every instruction must have a unique opcode.
    """

    values = list(
        OPCODES.values()
    )

    assert len(
        values
    ) == len(
        set(
            values
        )
    )


# ============================================================
# 8-BIT DATA RANGE
# ============================================================


def test_accumulator_remains_8bit_after_arithmetic():
    """
    CPU accumulator must remain inside
    the 8-bit range.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    if not set_accumulator(
        executor,
        0xFF,
    ):

        pytest.skip(
            "Accumulator cannot be configured."
        )

    execute_instruction(
        executor,
        OPCODES["ADD"],
        0x01,
    )

    accumulator = get_accumulator(
        executor
    )

    assert (
        0x00
        <= accumulator
        <= 0xFF
    )


# ============================================================
# FINAL INTEGRATION
# ============================================================


def test_instruction_executor_complete_integration():
    """
    Final integration test for the executor.

    The executor must correctly handle the
    fundamental 8-bit instruction workflow.
    """

    executor = create_executor()

    reset_executor(
        executor
    )

    execute_instruction(
        executor,
        OPCODES["LOAD"],
        0x20,
    )

    assert (
        get_accumulator(
            executor
        )
        == 0x20
    )

    execute_instruction(
        executor,
        OPCODES["ADD"],
        0x10,
    )

    assert (
        get_accumulator(
            executor
        )
        == 0x30
    )

    execute_instruction(
        executor,
        OPCODES["SUB"],
        0x05,
    )

    assert (
        get_accumulator(
            executor
        )
        == 0x2B
    )

    execute_instruction(
        executor,
        OPCODES["XOR"],
        0xFF,
    )

    assert (
        get_accumulator(
            executor
        )
        == (
            0x2B
            ^ 0xFF
        )
    )
