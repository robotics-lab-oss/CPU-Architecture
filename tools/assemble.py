"""
tools/assemble.py

MiniCPU 8-bit CPU Architecture
Assembly Command-Line Tool

Usage:

    python tools/assemble.py program.asm

Output:

    program.bin

Optional:

    python tools/assemble.py program.asm -o output.bin

    python tools/assemble.py program.asm --hex

    python tools/assemble.py program.asm --stdout

    python tools/assemble.py program.asm -o output.bin --hex

Workflow:

    .asm
      ↓
    Assembler
      ↓
    Machine Code
      ↓
    .bin / HEX / stdout
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ============================================================
# PROJECT IMPORT
# ============================================================

try:
    from assembler.assembler import Assembler
except ImportError as exc:

    print(
        "Error: Unable to import assembler.",
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
# ARGUMENT PARSER
# ============================================================


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="assemble",
        description=(
            "Assemble MiniCPU 8-bit "
            "assembly source into machine code."
        ),
    )

    parser.add_argument(
        "source",
        type=Path,
        help=(
            "Path to assembly source file."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help=(
            "Output binary file path."
        ),
    )

    parser.add_argument(
        "--hex",
        action="store_true",
        help=(
            "Print generated machine code "
            "as hexadecimal."
        ),
    )

    parser.add_argument(
        "--stdout",
        action="store_true",
        help=(
            "Print machine code bytes "
            "to stdout."
        ),
    )

    parser.add_argument(
        "--no-write",
        action="store_true",
        help=(
            "Do not write an output file."
        ),
    )

    return parser


# ============================================================
# SOURCE READING
# ============================================================


def read_source(
    path: Path,
) -> str:
    """
    Read assembly source file.
    """

    if not path.exists():

        raise FileNotFoundError(
            f"Source file not found: {path}"
        )

    if not path.is_file():

        raise ValueError(
            f"Source path is not a file: {path}"
        )

    try:

        return path.read_text(
            encoding="utf-8"
        )

    except OSError as exc:

        raise OSError(
            f"Unable to read source file: {path}"
        ) from exc


# ============================================================
# ASSEMBLY
# ============================================================


def assemble_source(
    source: str,
) -> object:
    """
    Assemble source code using project Assembler.
    """

    assembler = Assembler()

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

    raise AttributeError(
        "Assembler does not expose "
        "assemble(), compile(), or build()."
    )


# ============================================================
# MACHINE CODE EXTRACTION
# ============================================================


def extract_machine_code(
    result: object,
) -> bytes:
    """
    Convert assembler result into bytes.

    Supported result formats:

        bytes
        bytearray
        list[int]
        tuple[int]
        dict containing:
            machine_code
            code
            binary
            output
            bytes
    """

    # --------------------------------------------------------
    # bytes
    # --------------------------------------------------------

    if isinstance(
        result,
        bytes,
    ):

        return result

    # --------------------------------------------------------
    # bytearray
    # --------------------------------------------------------

    if isinstance(
        result,
        bytearray,
    ):

        return bytes(
            result
        )

    # --------------------------------------------------------
    # list / tuple
    # --------------------------------------------------------

    if isinstance(
        result,
        (
            list,
            tuple,
        ),
    ):

        return validate_machine_code(
            result
        )

    # --------------------------------------------------------
    # dictionary
    # --------------------------------------------------------

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
                (
                    list,
                    tuple,
                ),
            ):

                return validate_machine_code(
                    value
                )

    # --------------------------------------------------------
    # Unsupported
    # --------------------------------------------------------

    raise TypeError(
        "Unsupported assembler result. "
        "Expected bytes, bytearray, "
        "list, tuple, or dictionary."
    )


# ============================================================
# MACHINE CODE VALIDATION
# ============================================================


def validate_machine_code(
    machine_code,
) -> bytes:
    """
    Validate machine code bytes.

    MiniCPU uses 8-bit values:

        0x00 - 0xFF
    """

    result = []

    for index, value in enumerate(
        machine_code
    ):

        if not isinstance(
            value,
            int,
        ):

            raise TypeError(
                f"Machine code byte at "
                f"index {index} must be integer."
            )

        if not (
            MIN_BYTE
            <= value
            <= MAX_BYTE
        ):

            raise ValueError(
                f"Machine code byte at "
                f"index {index} is outside "
                f"8-bit range: {value}"
            )

        result.append(
            value
        )

    if len(
        result
    ) > MEMORY_SIZE:

        raise ValueError(
            "Program is too large for "
            "MiniCPU 8-bit address space. "
            f"Maximum size: {MEMORY_SIZE} bytes."
        )

    return bytes(
        result
    )


# ============================================================
# OUTPUT PATH
# ============================================================


def get_output_path(
    source_path: Path,
    output_path: Path | None,
) -> Path:
    """
    Determine output binary path.

    Default:

        program.asm
            ↓
        program.bin
    """

    if output_path is not None:

        return output_path

    return source_path.with_suffix(
        ".bin"
    )


# ============================================================
# WRITE BINARY
# ============================================================


def write_binary(
    path: Path,
    machine_code: bytes,
) -> None:
    """
    Write machine code to binary file.
    """

    try:

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            machine_code
        )

    except OSError as exc:

        raise OSError(
            f"Unable to write output file: {path}"
        ) from exc


# ============================================================
# HEX FORMAT
# ============================================================


def format_hex(
    machine_code: bytes,
) -> str:
    """
    Format machine code as hexadecimal.

    Example:

        00 10 42 F0
    """

    return " ".join(
        f"{byte:02X}"
        for byte in machine_code
    )


# ============================================================
# BINARY FORMAT
# ============================================================


def format_binary(
    machine_code: bytes,
) -> str:
    """
    Format machine code as binary.

    Example:

        00000000 00010000 01000010 11110000
    """

    return " ".join(
        f"{byte:08b}"
        for byte in machine_code
    )


# ============================================================
# MAIN
# ============================================================


def main(
    argv=None,
) -> int:
    """
    Main CLI entry point.
    """

    parser = create_argument_parser()

    args = parser.parse_args(
        argv
    )

    # --------------------------------------------------------
    # Read source
    # --------------------------------------------------------

    try:

        source = read_source(
            args.source
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
    # Assemble
    # --------------------------------------------------------

    try:

        result = assemble_source(
            source
        )

        machine_code = extract_machine_code(
            result
        )

    except Exception as exc:

        print(
            "Assembly failed:",
            file=sys.stderr,
        )

        print(
            f"  {exc}",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------------------------
    # Output path
    # --------------------------------------------------------

    output_path = get_output_path(
        args.source,
        args.output,
    )

    # --------------------------------------------------------
    # Write binary
    # --------------------------------------------------------

    if not args.no_write:

        try:

            write_binary(
                output_path,
                machine_code,
            )

        except OSError as exc:

            print(
                f"Error: {exc}",
                file=sys.stderr,
            )

            return 1

    # --------------------------------------------------------
    # Print HEX
    # --------------------------------------------------------

    if args.hex:

        print(
            format_hex(
                machine_code
            )
        )

    # --------------------------------------------------------
    # Print binary
    # --------------------------------------------------------

    if args.stdout:

        print(
            format_binary(
                machine_code
            )
        )

    # --------------------------------------------------------
    # Default output information
    # --------------------------------------------------------

    if not args.hex and not args.stdout:

        if args.no_write:

            print(
                "Assembly successful."
            )

            print(
                f"Size: {len(machine_code)} byte(s)"
            )

        else:

            print(
                "Assembly successful."
            )

            print(
                f"Output: {output_path}"
            )

            print(
                f"Size: {len(machine_code)} byte(s)"
            )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    sys.exit(
        main()
    )
