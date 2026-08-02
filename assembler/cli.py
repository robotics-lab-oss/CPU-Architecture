"""
cli.py

MiniCPU 8-bit CPU Architecture
Assembler Command Line Interface

Usage:

    python -m assembler.cli program.asm

    python -m assembler.cli program.asm -o program.bin

    python -m assembler.cli program.asm -f bin

    python -m assembler.cli program.asm -f hex

    python -m assembler.cli program.asm --dump-symbols

    python -m assembler.cli program.asm --verbose
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence


# ============================================================
# IMPORT ASSEMBLER
# ============================================================

try:
    from .assembler import Assembler
except ImportError:
    from assembler import Assembler


# ============================================================
# CONSTANTS
# ============================================================

VERSION = "1.0.0"

SUPPORTED_FORMATS = (
    "bin",
    "hex",
)

DEFAULT_FORMAT = "bin"


# ============================================================
# ARGUMENT PARSER
# ============================================================

def create_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="minicpu-as",
        description=(
            "MiniCPU 8-bit CPU Architecture "
            "Assembler"
        ),
    )

    parser.add_argument(
        "source",
        type=Path,
        help=(
            "Input assembly source file "
            "(.asm)"
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help=(
            "Output file path. "
            "If omitted, it is generated "
            "automatically."
        ),
    )

    parser.add_argument(
        "-f",
        "--format",
        choices=SUPPORTED_FORMATS,
        default=DEFAULT_FORMAT,
        help=(
            "Output format: bin or hex "
            "(default: bin)"
        ),
    )

    parser.add_argument(
        "--dump-symbols",
        action="store_true",
        help=(
            "Display symbol table after "
            "assembly."
        ),
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help=(
            "Display detailed assembly "
            "information."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=(
            f"MiniCPU Assembler {VERSION}"
        ),
    )

    return parser


# ============================================================
# VALIDATE SOURCE
# ============================================================

def validate_source(
    source: Path,
) -> None:
    """
    Validate source assembly file.
    """

    if not source.exists():
        raise FileNotFoundError(
            f"Source file not found: "
            f"{source}"
        )

    if not source.is_file():
        raise ValueError(
            f"Source path is not a file: "
            f"{source}"
        )


# ============================================================
# OUTPUT PATH
# ============================================================

def get_output_path(
    source: Path,
    output: Optional[Path],
    output_format: str,
) -> Path:
    """
    Generate output path when user
    does not provide one.
    """

    if output is not None:
        return output

    if output_format == "bin":
        extension = ".bin"

    elif output_format == "hex":
        extension = ".hex"

    else:
        raise ValueError(
            f"Unsupported output format: "
            f"{output_format}"
        )

    return source.with_suffix(
        extension
    )


# ============================================================
# NORMALIZE ASSEMBLER RESULT
# ============================================================

def normalize_machine_code(
    result,
) -> bytes:
    """
    Convert assembler output into bytes.

    Supported results:

    - bytes
    - bytearray
    - list[int]
    - tuple[int, ...]
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
        return bytes(result)

    if isinstance(
        result,
        (list, tuple),
    ):
        try:
            return bytes(result)

        except ValueError as exc:
            raise ValueError(
                "Assembler returned invalid "
                "byte values."
            ) from exc

    raise TypeError(
        "Unsupported assembler result type: "
        f"{type(result).__name__}"
    )


# ============================================================
# WRITE BINARY
# ============================================================

def write_binary(
    output: Path,
    machine_code: bytes,
) -> None:
    """
    Write raw binary machine code.
    """

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_bytes(
        machine_code
    )


# ============================================================
# WRITE HEX
# ============================================================

def write_hex(
    output: Path,
    machine_code: bytes,
) -> None:
    """
    Write machine code as hexadecimal.

    Example:

        0000: 00 10 20 80
    """

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = []

    for address in range(
        0,
        len(machine_code),
        16,
    ):
        chunk = machine_code[
            address:address + 16
        ]

        hex_data = " ".join(
            f"{byte:02X}"
            for byte in chunk
        )

        lines.append(
            f"{address:04X}: "
            f"{hex_data}"
        )

    output.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


# ============================================================
# WRITE OUTPUT
# ============================================================

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

        return

    if output_format == "hex":

        write_hex(
            output,
            machine_code,
        )

        return

    raise ValueError(
        f"Unsupported output format: "
        f"{output_format}"
    )


# ============================================================
# SYMBOL TABLE
# ============================================================

def dump_symbol_table(
    assembler,
) -> None:
    """
    Display symbol table if available.
    """

    symbol_table = getattr(
        assembler,
        "symbol_table",
        None,
    )

    if symbol_table is None:

        print(
            "[WARNING] "
            "Symbol table is not available."
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

    symbols = getattr(
        symbol_table,
        "symbols",
        None,
    )

    if symbols is None:

        print(
            "[WARNING] "
            "Unable to display symbol table."
        )

        return

    print(
        "------ SYMBOL TABLE ------"
    )

    for name in sorted(
        symbols
    ):

        value = symbols[name]

        if isinstance(
            value,
            int,
        ):

            print(
                f"{name:<16} "
                f"0x{value:02X}"
            )

        else:

            print(
                f"{name:<16} "
                f"{value}"
            )

    print(
        "--------------------------"
    )


# ============================================================
# ASSEMBLE SOURCE
# ============================================================

def assemble_source(
    source: Path,
    *,
    verbose: bool = False,
):
    """
    Assemble source using the project's
    Assembler class.

    The actual assembler implementation
    is responsible for:

    - Lexer
    - Parser
    - First pass
    - Symbol table
    - Second pass
    - Opcode encoding
    """

    assembler = Assembler()

    source_text = source.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Preferred API
    # --------------------------------------------------------

    try:

        result = assembler.assemble(
            source_text
        )

    except TypeError:

        # ----------------------------------------------------
        # Compatibility fallback
        # ----------------------------------------------------

        result = assembler.assemble(
            source
        )

    if verbose:

        print(
            f"[INFO] Source: "
            f"{source}"
        )

    return (
        assembler,
        normalize_machine_code(
            result
        ),
    )


# ============================================================
# MAIN ASSEMBLY FUNCTION
# ============================================================

def assemble_file(
    source: Path,
    output: Optional[Path] = None,
    output_format: str = DEFAULT_FORMAT,
    *,
    dump_symbols: bool = False,
    verbose: bool = False,
) -> Path:
    """
    Assemble one .asm file.

    Returns:
        Generated output path.
    """

    validate_source(
        source
    )

    output_path = get_output_path(
        source,
        output,
        output_format,
    )

    if verbose:

        print(
            f"[INFO] Format: "
            f"{output_format}"
        )

        print(
            f"[INFO] Output: "
            f"{output_path}"
        )

    assembler, machine_code = (
        assemble_source(
            source,
            verbose=verbose,
        )
    )

    write_output(
        output_path,
        machine_code,
        output_format,
    )

    if dump_symbols:

        dump_symbol_table(
            assembler
        )

    if verbose:

        print(
            f"[INFO] Machine code size: "
            f"{len(machine_code)} byte(s)"
        )

        print(
            "[INFO] Assembly successful."
        )

    return output_path


# ============================================================
# CLI MAIN
# ============================================================

def main(
    argv: Optional[Sequence[str]] = None,
) -> int:
    """
    Main command-line entry point.
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
            dump_symbols=args.dump_symbols,
            verbose=args.verbose,
        )

        print(
            f"Generated: "
            f"{output}"
        )

        return 0

    except FileNotFoundError as exc:

        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )

        return 1

    except (
        ValueError,
        TypeError,
    ) as exc:

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


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    raise SystemExit(
        main()
    )
