"""
tools/dump_memory.py

MiniCPU 8-bit CPU Architecture
Memory Dump Command-Line Tool

Usage:

    python tools/dump_memory.py program.bin

    python tools/dump_memory.py program.bin --start 0x00

    python tools/dump_memory.py program.bin --start 0x10 --end 0x7F

    python tools/dump_memory.py program.bin --format binary

    python tools/dump_memory.py program.bin --format hex

    python tools/dump_memory.py program.bin -o memory.txt

Workflow:

    Binary / Memory File
            ↓
        Read Bytes
            ↓
       Address Range
            ↓
       Format Memory
            ↓
        HEX / Binary
            ↓
        Terminal / File
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ============================================================
# CONSTANTS
# ============================================================

MIN_BYTE = 0x00

MAX_BYTE = 0xFF

MEMORY_SIZE = 256

DEFAULT_START_ADDRESS = 0x00

DEFAULT_END_ADDRESS = 0xFF

BYTES_PER_LINE = 16


# ============================================================
# ARGUMENT PARSER
# ============================================================


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="dump_memory",
        description=(
            "Display MiniCPU 8-bit memory "
            "contents in hexadecimal or binary."
        ),
    )

    parser.add_argument(
        "memory",
        type=Path,
        help=(
            "Path to binary memory/program file."
        ),
    )

    parser.add_argument(
        "--start",
        type=parse_byte,
        default=DEFAULT_START_ADDRESS,
        help=(
            "Starting memory address "
            "(default: 0x00)."
        ),
    )

    parser.add_argument(
        "--end",
        type=parse_byte,
        default=DEFAULT_END_ADDRESS,
        help=(
            "Ending memory address "
            "(default: 0xFF)."
        ),
    )

    parser.add_argument(
        "--format",
        choices=(
            "hex",
            "binary",
        ),
        default="hex",
        help=(
            "Memory output format "
            "(default: hex)."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Write memory dump to file."
        ),
    )

    parser.add_argument(
        "--no-address",
        action="store_true",
        help=(
            "Do not display memory addresses."
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
# READ MEMORY
# ============================================================


def read_memory(
    path: Path,
) -> bytes:
    """
    Read binary memory image.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"Memory file not found: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"Memory path is not a file: {path}"
        )

    try:

        data = path.read_bytes()

    except OSError as exc:

        raise OSError(
            f"Unable to read memory file: {path}"
        ) from exc

    if len(
        data
    ) > MEMORY_SIZE:

        raise ValueError(
            "Memory image exceeds MiniCPU "
            f"memory size of {MEMORY_SIZE} bytes."
        )

    return data


# ============================================================
# MEMORY RANGE
# ============================================================


def validate_range(
    start: int,
    end: int,
) -> None:
    """
    Validate memory address range.
    """

    if not (
        MIN_BYTE
        <= start
        <= MAX_BYTE
    ):

        raise ValueError(
            "Start address must be "
            "between 0x00 and 0xFF."
        )

    if not (
        MIN_BYTE
        <= end
        <= MAX_BYTE
    ):

        raise ValueError(
            "End address must be "
            "between 0x00 and 0xFF."
        )

    if start > end:

        raise ValueError(
            "Start address cannot be "
            "greater than end address."
        )


# ============================================================
# FORMAT BYTE
# ============================================================


def format_byte(
    value: int,
    output_format: str,
) -> str:
    """
    Format one memory byte.
    """

    if not (
        MIN_BYTE
        <= value
        <= MAX_BYTE
    ):

        raise ValueError(
            f"Invalid memory byte: {value}"
        )

    if output_format == "hex":

        return f"{value:02X}"

    if output_format == "binary":

        return f"{value:08b}"

    raise ValueError(
        f"Unsupported format: {output_format}"
    )


# ============================================================
# FORMAT MEMORY DUMP
# ============================================================


def format_memory_dump(
    memory: bytes,
    start_address: int,
    end_address: int,
    output_format: str = "hex",
    show_address: bool = True,
) -> str:
    """
    Format memory contents.

    Missing addresses are displayed as:

        00

    for HEX format.

    This represents zero-initialized memory.
    """

    validate_range(
        start_address,
        end_address,
    )

    lines = []

    # --------------------------------------------------------
    # Determine value width
    # --------------------------------------------------------

    if output_format == "hex":

        value_width = 2

    elif output_format == "binary":

        value_width = 8

    else:

        raise ValueError(
            f"Unsupported format: {output_format}"
        )

    # --------------------------------------------------------
    # Process memory in 16-byte rows
    # --------------------------------------------------------

    current = start_address

    while current <= end_address:

        row_end = min(
            current
            + BYTES_PER_LINE
            - 1,
            end_address,
        )

        values = []

        for address in range(
            current,
            row_end + 1,
        ):

            if address < len(
                memory
            ):

                value = memory[
                    address
                ]

            else:

                # Uninitialized memory
                value = 0x00

            values.append(
                format_byte(
                    value,
                    output_format,
                )
            )

        # ----------------------------------------------------
        # Format row
        # ----------------------------------------------------

        formatted_values = " ".join(
            values
        )

        if show_address:

            lines.append(
                f"{current:02X}: "
                f"{formatted_values}"
            )

        else:

            lines.append(
                formatted_values
            )

        current = (
            row_end
            + 1
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
    Write memory dump to text file.
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
    Main memory dump CLI entry point.
    """

    parser = create_argument_parser()

    args = parser.parse_args(
        argv
    )

    # --------------------------------------------------------
    # Validate range
    # --------------------------------------------------------

    try:

        validate_range(
            args.start,
            args.end,
        )

    except ValueError as exc:

        parser.error(
            str(exc)
        )

    # --------------------------------------------------------
    # Read memory
    # --------------------------------------------------------

    try:

        memory = read_memory(
            args.memory
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

    # --------------------------------------------------------
    # Format dump
    # --------------------------------------------------------

    try:

        dump = format_memory_dump(
            memory=memory,
            start_address=args.start,
            end_address=args.end,
            output_format=args.format,
            show_address=not args.no_address,
        )

    except ValueError as exc:

        print(
            f"Error: {exc}",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    if args.output is not None:

        try:

            write_output(
                args.output,
                dump,
            )

        except OSError as exc:

            print(
                f"Error: {exc}",
                file=sys.stderr,
            )

            return 1

        print(
            "Memory dump successful."
        )

        print(
            f"Input: {args.memory}"
        )

        print(
            f"Range: "
            f"0x{args.start:02X}"
            f"-"
            f"0x{args.end:02X}"
        )

        print(
            f"Format: {args.format}"
        )

        print(
            f"Output: {args.output}"
        )

        return 0

    # --------------------------------------------------------
    # Print to stdout
    # --------------------------------------------------------

    print(
        dump
    )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    sys.exit(
        main()
    )
