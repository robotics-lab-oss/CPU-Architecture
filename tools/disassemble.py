"""
tools/disassemble.py

MiniCPU 8-bit CPU Architecture
Machine Code Disassembler

Usage:

    python tools/disassemble.py program.bin

Options:

    python tools/disassemble.py program.bin --hex

    python tools/disassemble.py program.bin --start 0x00

    python tools/disassemble.py program.bin -o program.asm

Workflow:

    Binary Machine Code
            ↓
        Read Bytes
            ↓
        Decode Opcode
            ↓
      Read Operand
            ↓
      Assembly Output
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ============================================================
# PROJECT IMPORT
# ============================================================

try:
    from opcode import (
        OPCODES,
        ONE_BYTE_INSTRUCTIONS,
        TWO_BYTE_INSTRUCTIONS,
    )

except ImportError as exc:

    print(
        "Error: Unable to import opcode definitions.",
        file=sys.stderr,
    )

    print(
        f"Details: {exc}",
        file=sys.stderr,
    )

    sys.exit(1)


# ============================================================
# CONSTANTS
# ============================================================

MIN_BYTE = 0x00

MAX_BYTE = 0xFF

MEMORY_SIZE = 256


# ============================================================
# REVERSE OPCODE TABLE
# ============================================================

OPCODE_TO_INSTRUCTION = {
    opcode: instruction
    for instruction, opcode in OPCODES.items()
}


# ============================================================
# ARGUMENT PARSER
# ============================================================


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="disassemble",
        description=(
            "Disassemble MiniCPU 8-bit "
            "machine code into assembly."
        ),
    )

    parser.add_argument(
        "program",
        type=Path,
        help=(
            "Path to binary machine-code file."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Write disassembled assembly "
            "to this file."
        ),
    )

    parser.add_argument(
        "--start",
        type=parse_byte,
        default=0x00,
        help=(
            "Starting memory address "
            "(default: 0x00)."
        ),
    )

    parser.add_argument(
        "--hex",
        action="store_true",
        help=(
            "Show raw machine-code bytes "
            "alongside instructions."
        ),
    )

    return parser


# ============================================================
# BYTE PARSER
# ============================================================


def parse_byte(
    value: str,
) -> int:
    """
    Parse an 8-bit integer.

    Supports:

        10
        0x10
        0b00010000
    """

    try:

        number = int(
            value,
            0,
        )

    except ValueError as exc:

        raise argparse.ArgumentTypeError(
            f"Invalid 8-bit value: {value}"
        ) from exc

    if not (
        MIN_BYTE
        <= number
        <= MAX_BYTE
    ):

        raise argparse.ArgumentTypeError(
            f"Value must be between "
            f"0x00 and 0xFF: {value}"
        )

    return number


# ============================================================
# READ PROGRAM
# ============================================================


def read_program(
    path: Path,
) -> bytes:
    """
    Read binary machine-code file.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"Program file not found: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"Program path is not a file: {path}"
        )

    try:

        data = path.read_bytes()

    except OSError as exc:

        raise OSError(
            f"Unable to read program: {path}"
        ) from exc

    if len(
        data
    ) > MEMORY_SIZE:

        raise ValueError(
            "Program exceeds MiniCPU "
            f"memory size of {MEMORY_SIZE} bytes."
        )

    return data


# ============================================================
# OPCODE LOOKUP
# ============================================================


def get_instruction_name(
    opcode: int,
) -> str | None:
    """
    Return instruction name for opcode.
    """

    return OPCODE_TO_INSTRUCTION.get(
        opcode
    )


# ============================================================
# INSTRUCTION SIZE
# ============================================================


def get_instruction_size(
    instruction: str,
) -> int:
    """
    Return instruction size.

    1-byte instruction:
        opcode only

    2-byte instruction:
        opcode + operand
    """

    if instruction in ONE_BYTE_INSTRUCTIONS:

        return 1

    if instruction in TWO_BYTE_INSTRUCTIONS:

        return 2

    raise ValueError(
        f"Unknown instruction: {instruction}"
    )


# ============================================================
# DISASSEMBLE ONE INSTRUCTION
# ============================================================


def disassemble_instruction(
    program: bytes,
    offset: int,
    address: int,
):
    """
    Decode one instruction.

    Returns:

        address
        instruction
        size
        raw bytes
    """

    if offset >= len(
        program
    ):

        raise IndexError(
            "Instruction offset is outside program."
        )

    opcode = program[
        offset
    ]

    instruction = get_instruction_name(
        opcode
    )

    # --------------------------------------------------------
    # Unknown opcode
    # --------------------------------------------------------

    if instruction is None:

        return {
            "address": address,
            "instruction": (
                f".BYTE 0x{opcode:02X}"
            ),
            "size": 1,
            "bytes": bytes(
                [
                    opcode
                ]
            ),
            "unknown": True,
        }

    size = get_instruction_size(
        instruction
    )

    # --------------------------------------------------------
    # 1-byte instruction
    # --------------------------------------------------------

    if size == 1:

        return {
            "address": address,
            "instruction": instruction,
            "size": 1,
            "bytes": bytes(
                [
                    opcode
                ]
            ),
            "unknown": False,
        }

    # --------------------------------------------------------
    # 2-byte instruction
    # --------------------------------------------------------

    if offset + 1 >= len(
        program
    ):

        raise ValueError(
            "Incomplete 2-byte instruction "
            f"at address 0x{address:02X}: "
            f"{instruction} requires an operand."
        )

    operand = program[
        offset + 1
    ]

    return {
        "address": address,
        "instruction": (
            f"{instruction} "
            f"0x{operand:02X}"
        ),
        "size": 2,
        "bytes": bytes(
            [
                opcode,
                operand,
            ]
        ),
        "unknown": False,
    }


# ============================================================
# DISASSEMBLE PROGRAM
# ============================================================


def disassemble_program(
    program: bytes,
    start_address: int = 0x00,
):
    """
    Disassemble complete machine-code program.
    """

    if not (
        MIN_BYTE
        <= start_address
        <= MAX_BYTE
    ):

        raise ValueError(
            "Start address must be "
            "between 0x00 and 0xFF."
        )

    instructions = []

    offset = 0

    address = start_address

    while offset < len(
        program
    ):

        result = disassemble_instruction(
            program,
            offset,
            address,
        )

        instructions.append(
            result
        )

        offset += result[
            "size"
        ]

        address += result[
            "size"
        ]

        # ----------------------------------------------------
        # 8-bit address space check
        # ----------------------------------------------------

        if (
            address > MAX_BYTE
            and offset < len(
                program
            )
        ):

            raise ValueError(
                "Program crosses the "
                "8-bit address space boundary."
            )

    return instructions


# ============================================================
# FORMAT ASSEMBLY
# ============================================================


def format_assembly(
    instructions,
    show_hex: bool = False,
) -> str:
    """
    Convert disassembled instructions
    into assembly text.
    """

    lines = []

    for item in instructions:

        address = item[
            "address"
        ]

        instruction = item[
            "instruction"
        ]

        if show_hex:

            raw = " ".join(
                f"{byte:02X}"
                for byte in item[
                    "bytes"
                ]
            )

            lines.append(
                f"{address:02X}: "
                f"{raw:<8} "
                f"{instruction}"
            )

        else:

            lines.append(
                instruction
            )

    return "\n".join(
        lines
    )


# ============================================================
# WRITE OUTPUT
# ============================================================


def write_output(
    path: Path,
    content: str,
) -> None:
    """
    Write disassembled assembly to file.
    """

    try:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content
            + "\n",
            encoding="utf-8",
        )

    except OSError as exc:

        raise OSError(
            f"Unable to write output file: {path}"
        ) from exc


# ============================================================
# MAIN
# ============================================================


def main(
    argv=None,
) -> int:
    """
    Main disassembler CLI entry point.
    """

    parser = create_argument_parser()

    args = parser.parse_args(
        argv
    )

    # --------------------------------------------------------
    # Read program
    # --------------------------------------------------------

    try:

        program = read_program(
            args.program
        )

    except (
        FileNotFoundError,
        ValueError,
        OSError,
    ) as exc:

        print(
            f"Error: {exc}",
            file=sys.stderr,
        )

        return 1

    if not program:

        print(
            "Error: Program file is empty.",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------------------------
    # Disassemble
    # --------------------------------------------------------

    try:

        instructions = disassemble_program(
            program,
            args.start,
        )

        assembly = format_assembly(
            instructions,
            args.hex,
        )

    except (
        ValueError,
        IndexError,
    ) as exc:

        print(
            f"Disassembly failed: {exc}",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------------------------
    # Output file
    # --------------------------------------------------------

    if args.output is not None:

        try:

            write_output(
                args.output,
                assembly,
            )

        except OSError as exc:

            print(
                f"Error: {exc}",
                file=sys.stderr,
            )

            return 1

        print(
            "Disassembly successful."
        )

        print(
            f"Output: {args.output}"
        )

        print(
            f"Instructions: "
            f"{len(instructions)}"
        )

        return 0

    # --------------------------------------------------------
    # stdout
    # --------------------------------------------------------

    print(
        assembly
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    sys.exit(
        main()
    )
