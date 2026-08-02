"""
assembler/cli.py

Command-line interface for the MiniCPU 8-bit Assembler.

Usage examples:

    python -m assembler.cli program.asm

    python -m assembler.cli program.asm -o program.bin

    python -m assembler.cli program.asm --format bin

    python -m assembler.cli program.asm --format hex

    python -m assembler.cli program.asm --dump-symbols

    python -m assembler.cli program.asm --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence


# ---------------------------------------------------------------------------
# Project imports
# ---------------------------------------------------------------------------

try:
    from .assembler import Assembler
except ImportError:
    # Allows direct execution:
    # python assembler/cli.py program.asm
    from assembler import Assembler


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_OUTPUT_FORMAT = "bin"

SUPPORTED_FORMATS = (
    "bin",
    "hex",
)


# ---------------------------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------------------------

def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="minicpu-as",
        description=(
            "MiniCPU 8-bit Assembly Language Compiler"
        ),
        epilog=(
            "Assembles MiniCPU assembly source into "
            "binary or hexadecimal machine code."
        ),
    )

    parser.add_argument(
        "source",
        metavar="SOURCE",
        type=Path,
        help="Input assembly source file (.asm)",
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="OUTPUT",
        type=Path,
        help=(
            "Output file. If omitted, the output name "
            "is generated automatically."
        ),
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=SUPPORTED_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=(
            "Output format: bin or hex "
            f"(default: {DEFAULT_OUTPUT_FORMAT})"
        ),
    )

    parser.add_argument(
        "--dump-symbols",
        action="store_true",
        help=(
            "Display the symbol table after assembly."
        ),
    )

    parser.add_argument(
        "--dump-tokens",
        action="store_true",
        help=(
            "Display lexer/parser tokens if supported "
            "by the assembler."
        ),
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display detailed assembly information.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="MiniCPU Assembler 1.0.0",
    )

    return parser


# ---------------------------------------------------------------------------
# Output filename
# ---------------------------------------------------------------------------

def get_output_path(
    source: Path,
    output: Optional[Path],
    output_format: str,
) -> Path:
    """
    Determine the output filename.
    """

    if output is not None:
        return output

    extension = (
        ".bin"
        if output_format == "bin"
        else ".hex"
    )

    return source.with_suffix(extension)


# ---------------------------------------------------------------------------
# File Validation
# ---------------------------------------------------------------------------

def validate_source(source: Path) -> None:
    """
    Validate the input source file.
    """

    if not source.exists():
        raise FileNotFoundError(
            f"Source file not found: {source}"
        )

    if not source.is_file():
        raise ValueError(
            f"Source path is not a file: {source}"
        )


# ---------------------------------------------------------------------------
# Binary Output
# ---------------------------------------------------------------------------

def write_binary(
    output: Path,
    machine_code: bytes,
) -> None:
    """
    Write machine code as raw binary.
    """

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_bytes(machine_code)


# ---------------------------------------------------------------------------
# HEX Output
# ---------------------------------------------------------------------------

def write_hex(
    output: Path,
    machine_code: bytes,
) -> None:
    """
    Write machine code as a simple hexadecimal dump.

    Example:

        10 20 30 FF
    """

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = []

    for index in range(
        0,
        len(machine_code),
        16,
    ):
        chunk = machine_code[
            index:index + 16
        ]

        hex_values = " ".join(
            f"{byte:02X}"
            for byte in chunk
        )

        lines.append(
            f"{index:04X}: {hex_values}"
        )

    output.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Generic Output
# ---------------------------------------------------------------------------

def write_output(
    output: Path,
    machine_code: bytes,
    output_format: str,
) -> None:
    """
    Write assembled machine code.
    """

    if output_format == "bin":
        write_binary(
            output,
            machine_code,
        )

    elif output_format == "hex":
        write_hex(
            output,
            machine_code,
        )

    else:
        raise ValueError(
            f"Unsupported output format: "
            f"{output_format}"
        )


# ---------------------------------------------------------------------------
# Assembler Compatibility
# ---------------------------------------------------------------------------

def run_assembler(
    source: Path,
    *,
    verbose: bool = False,
):
    """
    Run the project's Assembler implementation.

    This function supports common assembler APIs.

    Preferred API:

        assembler.assemble(source)

    Alternative API:

        assembler.assemble(source.read_text())

    The exact call is delegated to assembler.py.
    """

    assembler = Assembler()

    # Preferred API: assemble(Path)
    try:
        result = assembler.assemble(source)
    except (TypeError, AttributeError):
        # Fallback API: assemble(source_text)
        source_text = source.read_text(
            encoding="utf-8"
        )

        result = assembler.assemble(
            source_text
        )

    if verbose:
        print(
            f"[INFO] Assembled: {source}"
        )

    return result


# ---------------------------------------------------------------------------
# Result Normalization
# ---------------------------------------------------------------------------

def normalize_machine_code(result) -> bytes:
    """
    Convert common assembler result types into bytes.

    Supported:

    - bytes
    - bytearray
    - list[int]
    - tuple[int, ...]
    """

    if isinstance(result, bytes):
        return result

    if isinstance(result, bytearray):
        return bytes(result)

    if isinstance(result, (list, tuple)):
        try:
            return bytes(result)
        except ValueError as exc:
            raise ValueError(
                "Assembler returned invalid byte values."
            ) from exc

    raise TypeError(
        "Assembler returned unsupported result type: "
        f"{type(result).__name__}"
    )


# ---------------------------------------------------------------------------
# Symbol Table Dump
# ---------------------------------------------------------------------------

def dump_symbols(assembler) -> None:
    """
    Print the symbol table if available.
    """

    symbol_table = getattr(
        assembler,
        "symbol_table",
        None,
    )

    if symbol_table is None:
        print(
            "[WARNING] Symbol table is not available."
        )
        return

    if hasattr(
        symbol_table,
        "dump",
    ):
        print(
            symbol_table.dump()
        )
        return

    if hasattr(
        symbol_table,
        "symbols",
    ):
        print(
            "------ SYMBOL TABLE ------"
        )

        for name in sorted(
            symbol_table.symbols
        ):
            value = symbol_table.symbols[name]

            print(
                f"{name:<16} "
                f"{value:02X}"
            )

        print(
            "--------------------------"
        )

        return

    print(
        "[WARNING] Unable to display symbol table."
    )


# ---------------------------------------------------------------------------
# Main Assembly Function
# ---------------------------------------------------------------------------

def assemble_file(
    source: Path,
    output: Optional[Path] = None,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    *,
    dump_symbol_table: bool = False,
    verbose: bool = False,
) -> Path:
    """
    Assemble one source file.

    Returns:
        Path to generated output.
    """

    validate_source(source)

    if output_format not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported output format: "
            f"{output_format}"
        )

    output_path = get_output_path(
        source,
        output,
        output_format,
    )

    if verbose:
        print(
            f"[INFO] Source : {source}"
        )

        print(
            f"[INFO] Format : {output_format}"
        )

        print(
            f"[INFO] Output : {output_path}"
        )

    assembler = Assembler()

    # Try the common Path-based API first.
    try:
        result = assembler.assemble(
            source
        )

    except (TypeError, AttributeError):
        source_text = source.read_text(
            encoding="utf-8"
        )

        result = assembler.assemble(
            source_text
        )

    machine_code = normalize_machine_code(
        result
    )

    write_output(
        output_path,
        machine_code,
        output_format,
    )

    if dump_symbol_table:
        dump_symbols(
            assembler
        )

    if verbose:
        print(
            f"[INFO] Bytes  : "
            f"{len(machine_code)}"
        )

        print(
            "[INFO] Assembly successful."
        )

    return output_path


# ---------------------------------------------------------------------------
# CLI Main
# ---------------------------------------------------------------------------

def main(
    argv: Optional[Sequence[str]] = None,
) -> int:
    """
    Command-line entry point.
    """

    parser = create_parser()

    args = parser.parse_args(
        argv
    )

    try:
        output = assemble_file(
            source=args.source,
            output=args.output,
            output_format=args.format,
            dump_symbol_table=args.dump_symbols,
            verbose=args.verbose,
        )

        print(
            f"Generated: {output}"
        )

        return 0

    except FileNotFoundError as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        return 1

    except (ValueError, TypeError) as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        return 1

    except Exception as exc:
        print(
            f"ASSEMBLY ERROR: {exc}",
            file=sys.stderr,
        )

        if args.verbose:
            raise

        return 1


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    raise SystemExit(
        main()
  )
