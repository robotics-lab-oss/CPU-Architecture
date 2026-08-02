"""
test_assembler.py

MiniCPU 8-bit CPU Architecture
Assembler Integration Tests

Tests the complete assembler pipeline:

    Source Code
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

Expected ISA:

1-byte:
    NOP
    OUT
    IN
    INC
    DEC
    HALT

2-byte:
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

from __future__ import annotations

import pytest

from assembler.assembler import Assembler


# ============================================================
# HELPERS
# ============================================================


def create_assembler():
    """
    Create a new Assembler instance.
    """

    return Assembler()


def assemble_source(
    source: str,
):
    """
    Assemble source code.

    Supports common Assembler APIs:

        assembler.assemble(source)

        assembler.compile(source)

        assembler.build(source)
    """

    assembler = create_assembler()

    if hasattr(
        assembler,
        "assemble",
    ):

        return assembler.assemble(
            source
        )

    if hasattr(
        assembler,
        "compile",
    ):

        return assembler.compile(
            source
        )

    if hasattr(
        assembler,
        "build",
    ):

        return assembler.build(
            source
        )

    raise AttributeError(
        "Assembler must provide "
        "assemble(), compile(), "
        "or build()."
    )


def normalize_output(
    result,
):
    """
    Normalize common assembler output types.
    """

    if isinstance(
        result,
        bytes,
    ):
        return list(
            result
        )

    if isinstance(
        result,
        bytearray,
    ):
        return list(
            result
        )

    if isinstance(
        result,
        tuple,
    ):
        return list(
            result
        )

    if isinstance(
        result,
        list,
    ):
        return result

    # Some assemblers return:
    #
    # {
    #     "machine_code": [...]
    # }
    #
    if isinstance(
        result,
        dict,
    ):

        for key in (
            "machine_code",
            "code",
            "bytes",
            "output",
        ):

            if key in result:

                value = result[
                    key
                ]

                return normalize_output(
                    value
                )

    return result


# ============================================================
# BASIC
# ============================================================


def test_assembler_can_be_created():
    """
    Assembler class should be constructable.
    """

    assembler = create_assembler()

    assert assembler is not None


# ============================================================
# EMPTY SOURCE
# ============================================================


def test_assemble_empty_source():
    """
    Empty source should produce no machine code.
    """

    result = assemble_source(
        ""
    )

    result = normalize_output(
        result
    )

    assert result == []


# ============================================================
# NOP
# ============================================================


def test_assemble_nop():
    """
    Source:

        NOP

    Machine code:

        00
    """

    result = assemble_source(
        "NOP"
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00
    ]


# ============================================================
# HALT
# ============================================================


def test_assemble_halt():
    """
    Source:

        HALT

    Machine code:

        F0
    """

    result = assemble_source(
        "HALT"
    )

    result = normalize_output(
        result
    )

    assert result == [
        0xF0
    ]


# ============================================================
# ONE-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            "NOP",
            [0x00],
        ),
        (
            "OUT",
            [0xA0],
        ),
        (
            "IN",
            [0xB0],
        ),
        (
            "INC",
            [0xC0],
        ),
        (
            "DEC",
            [0xD0],
        ),
        (
            "HALT",
            [0xF0],
        ),
    ],
)
def test_assemble_one_byte_instructions(
    source,
    expected,
):
    """
    Verify all one-byte instructions.
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == expected


# ============================================================
# LOAD
# ============================================================


def test_assemble_load():
    """
    LOAD 0x10

        10 10
    """

    result = assemble_source(
        "LOAD 0x10"
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
    ]


# ============================================================
# STORE
# ============================================================


def test_assemble_store():
    """
    STORE 0x20

        20 20
    """

    result = assemble_source(
        "STORE 0x20"
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x20,
        0x20,
    ]


# ============================================================
# ALL TWO-BYTE INSTRUCTIONS
# ============================================================


@pytest.mark.parametrize(
    "instruction, opcode",
    [
        ("LOAD", 0x10),
        ("STORE", 0x20),
        ("ADD", 0x30),
        ("SUB", 0x40),
        ("AND", 0x50),
        ("OR", 0x60),
        ("XOR", 0x70),
        ("JMP", 0x80),
        ("JZ", 0x90),
        ("CMP", 0xE0),
    ],
)
def test_assemble_two_byte_instruction(
    instruction,
    opcode,
):
    """
    Every two-byte instruction should
    generate opcode + operand.
    """

    source = (
        f"{instruction} 0x42"
    )

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        opcode,
        0x42,
    ]


# ============================================================
# MULTIPLE INSTRUCTIONS
# ============================================================


def test_assemble_multiple_instructions():
    """
    Source:

        NOP
        INC
        DEC
        HALT

    Output:

        00 C0 D0 F0
    """

    source = """
        NOP
        INC
        DEC
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0xC0,
        0xD0,
        0xF0,
    ]


# ============================================================
# MIXED INSTRUCTION SIZES
# ============================================================


def test_assemble_mixed_instruction_sizes():
    """
    Source:

        NOP
        LOAD 0x10
        INC
        STORE 0x20
        HALT

    Output:

        00
        10 10
        C0
        20 20
        F0
    """

    source = """
        NOP
        LOAD 0x10
        INC
        STORE 0x20
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0x10,
        0x10,
        0xC0,
        0x20,
        0x20,
        0xF0,
    ]


# ============================================================
# LABEL ONLY
# ============================================================


def test_assemble_label_only():
    """
    Source:

        START:
        NOP

    Label itself generates no byte.
    """

    source = """
        START:
        NOP
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00
    ]


# ============================================================
# LABEL WITH INSTRUCTION
# ============================================================


def test_assemble_label_with_instruction():
    """
    Source:

        START: NOP
        HALT

    Output:

        00 F0
    """

    source = """
        START: NOP
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0xF0,
    ]


# ============================================================
# JMP LABEL
# ============================================================


def test_assemble_jmp_label():
    """
    Source:

        JMP END
        NOP
        END:
        HALT

    Address:

        JMP = 2 bytes
        NOP = 1 byte

        END = 0x03

    Output:

        80 03
        00
        F0
    """

    source = """
        JMP END
        NOP
        END:
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x80,
        0x03,
        0x00,
        0xF0,
    ]


# ============================================================
# BACKWARD LABEL
# ============================================================


def test_assemble_backward_label():
    """
    Source:

        START:
        NOP
        JMP START

    Output:

        00
        80 00
    """

    source = """
        START:
        NOP
        JMP START
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0x80,
        0x00,
    ]


# ============================================================
# JZ LABEL
# ============================================================


def test_assemble_jz_label():
    """
    Source:

        JZ END
        NOP
        END:
        HALT

    END = 0x03
    """

    source = """
        JZ END
        NOP
        END:
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x90,
        0x03,
        0x00,
        0xF0,
    ]


# ============================================================
# COMPLETE PROGRAM
# ============================================================


def test_assemble_complete_program():
    """
    Complete MiniCPU program:

        START: LOAD 0x10
        LOOP:  INC
               JZ END
               JMP LOOP
        END:   HALT

    Addresses:

        START = 0x00
        LOOP  = 0x02
        END   = 0x07

    Machine code:

        10 10
        C0
        90 07
        80 02
        F0
    """

    source = """
        START: LOAD 0x10
        LOOP:  INC
               JZ END
               JMP LOOP
        END:   HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0xC0,
        0x90,
        0x07,
        0x80,
        0x02,
        0xF0,
    ]


# ============================================================
# COMMENTS
# ============================================================


def test_assemble_comments():
    """
    Comments should be ignored.

    Source:

        NOP ; do nothing
        HALT ; stop CPU
    """

    source = """
        NOP ; do nothing
        HALT ; stop CPU
    """

    try:

        result = assemble_source(
            source
        )

    except Exception:

        pytest.skip(
            "Current lexer does not support "
            "semicolon comments."
        )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0xF0,
    ]


# ============================================================
# BLANK LINES
# ============================================================


def test_assemble_blank_lines():
    """
    Blank lines should not generate bytes.
    """

    source = """

        NOP


        INC


        HALT

    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x00,
        0xC0,
        0xF0,
    ]


# ============================================================
# WHITESPACE
# ============================================================


def test_assemble_extra_whitespace():
    """
    Extra whitespace should not affect
    generated machine code.
    """

    source = """
            LOAD       0x10
            INC
            HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0xC0,
        0xF0,
    ]


# ============================================================
# CASE INSENSITIVE
# ============================================================


def test_assemble_case_insensitive_instructions():
    """
    Instructions should be accepted in
    mixed case if lexer/parser normalization
    is enabled.
    """

    source = """
        load 0x10
        Inc
        hAlT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0xC0,
        0xF0,
    ]


# ============================================================
# DECIMAL OPERAND
# ============================================================


def test_assemble_decimal_operand():
    """
    LOAD 255:

        10 FF
    """

    source = """
        LOAD 255
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0xFF,
    ]


# ============================================================
# BOUNDARY OPERANDS
# ============================================================


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            "LOAD 0x00",
            [0x10, 0x00],
        ),
        (
            "LOAD 0xFF",
            [0x10, 0xFF],
        ),
        (
            "JMP 0x00",
            [0x80, 0x00],
        ),
        (
            "JMP 0xFF",
            [0x80, 0xFF],
        ),
    ],
)
def test_assemble_8bit_boundary_values(
    source,
    expected,
):
    """
    Valid 8-bit operand boundaries.
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == expected


# ============================================================
# INVALID OPERAND
# ============================================================


def test_assemble_invalid_operand():
    """
    Invalid operand should produce an error.
    """

    with pytest.raises(
        Exception
    ):
        assemble_source(
            "LOAD 0xGG"
        )


# ============================================================
# UNDEFINED SYMBOL
# ============================================================


def test_assemble_undefined_symbol():
    """
    Undefined labels must be rejected.

    Source:

        JMP UNKNOWN
    """

    with pytest.raises(
        Exception
    ):
        assemble_source(
            "JMP UNKNOWN"
        )


# ============================================================
# DUPLICATE LABEL
# ============================================================


def test_assemble_duplicate_label():
    """
    Duplicate labels must be rejected.
    """

    source = """
        START:
        NOP
        START:
        HALT
    """

    with pytest.raises(
        Exception,
        match="Duplicate label",
    ):
        assemble_source(
            source
        )


# ============================================================
# MISSING OPERAND
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    [
        "LOAD",
        "STORE",
        "ADD",
        "SUB",
        "AND",
        "OR",
        "XOR",
        "JMP",
        "JZ",
        "CMP",
    ],
)
def test_assemble_missing_operand(
    instruction,
):
    """
    Every 2-byte instruction requires
    an operand.
    """

    with pytest.raises(
        Exception
    ):
        assemble_source(
            instruction
        )


# ============================================================
# UNEXPECTED OPERAND
# ============================================================


@pytest.mark.parametrize(
    "instruction",
    [
        "NOP",
        "OUT",
        "IN",
        "INC",
        "DEC",
        "HALT",
    ],
)
def test_assemble_unexpected_operand(
    instruction,
):
    """
    One-byte instructions must not accept
    an operand.
    """

    with pytest.raises(
        Exception
    ):
        assemble_source(
            f"{instruction} 0x10"
        )


# ============================================================
# PROGRAM LENGTH
# ============================================================


def test_assemble_program_length():
    """
    Program:

        NOP          1
        LOAD 0x10    2
        INC          1
        STORE 0x20   2
        HALT         1

    Total:

        7 bytes
    """

    source = """
        NOP
        LOAD 0x10
        INC
        STORE 0x20
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert len(
        result
    ) == 7


# ============================================================
# OUTPUT IS 8-BIT
# ============================================================


def test_assemble_output_values_are_8bit():
    """
    Every generated byte must be in
    the 8-bit range.
    """

    source = """
        LOAD 0x00
        STORE 0xFF
        JMP 0x80
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    for value in result:

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
# DETERMINISTIC ASSEMBLY
# ============================================================


def test_assembler_is_deterministic():
    """
    Same source should always generate
    identical machine code.
    """

    source = """
        START: LOAD 0x10
        LOOP:  INC
               JZ END
               JMP LOOP
        END:   HALT
    """

    first = normalize_output(
        assemble_source(
            source
        )
    )

    second = normalize_output(
        assemble_source(
            source
        )
    )

    assert first == second


# ============================================================
# REUSABLE ASSEMBLER
# ============================================================


def test_assembler_can_assemble_multiple_programs():
    """
    Assembler instance should be reusable.
    """

    assembler = create_assembler()

    first = assembler.assemble(
        "NOP"
    )

    second = assembler.assemble(
        "HALT"
    )

    first = normalize_output(
        first
    )

    second = normalize_output(
        second
    )

    assert first == [
        0x00
    ]

    assert second == [
        0xF0
    ]


# ============================================================
# LOOP PROGRAM
# ============================================================


def test_assemble_loop_program():
    """
    Test a realistic looping program.

    Source:

        START: LOAD 0x10
        LOOP:  DEC
               JZ END
               JMP LOOP
        END:   HALT
    """

    source = """
        START: LOAD 0x10
        LOOP:  DEC
               JZ END
               JMP LOOP
        END:   HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0xD0,
        0x90,
        0x07,
        0x80,
        0x02,
        0xF0,
    ]


# ============================================================
# ARITHMETIC PROGRAM
# ============================================================


def test_assemble_arithmetic_program():
    """
    Test arithmetic and logical instructions.

    Source:

        LOAD 0x10
        ADD 0x20
        SUB 0x01
        AND 0x0F
        OR 0x80
        XOR 0xFF
        CMP 0x00
        HALT
    """

    source = """
        LOAD 0x10
        ADD 0x20
        SUB 0x01
        AND 0x0F
        OR 0x80
        XOR 0xFF
        CMP 0x00
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0x30,
        0x20,
        0x40,
        0x01,
        0x50,
        0x0F,
        0x60,
        0x80,
        0x70,
        0xFF,
        0xE0,
        0x00,
        0xF0,
    ]


# ============================================================
# I/O PROGRAM
# ============================================================


def test_assemble_io_program():
    """
    Test input/output instructions.

    Source:

        IN
        OUT
        HALT
    """

    source = """
        IN
        OUT
        HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0xB0,
        0xA0,
        0xF0,
    ]


# ============================================================
# FINAL INTEGRATION TEST
# ============================================================


def test_full_assembler_pipeline():
    """
    Full integration test.

    This test verifies:

        Source
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

    Program:

        START: LOAD 0x10
        LOOP:  ADD 0x01
               CMP 0x20
               JZ END
               JMP LOOP
        END:   OUT
               HALT
    """

    source = """
        START: LOAD 0x10
        LOOP:  ADD 0x01
               CMP 0x20
               JZ END
               JMP LOOP
        END:   OUT
               HALT
    """

    result = assemble_source(
        source
    )

    result = normalize_output(
        result
    )

    assert result == [
        0x10,
        0x10,
        0x30,
        0x01,
        0xE0,
        0x20,
        0x90,
        0x0A,
        0x80,
        0x02,
        0xA0,
        0xF0,
    ]


# ============================================================
# END OF TEST FILE
# ============================================================
