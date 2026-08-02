"""
tools/simulate.py

MiniCPU 8-bit CPU Architecture
CPU Simulation Command-Line Tool

Usage:

    python tools/simulate.py program.bin

Options:

    python tools/simulate.py program.bin --max-cycles 1000

    python tools/simulate.py program.bin --debug

    python tools/simulate.py program.bin --dump-memory

    python tools/simulate.py program.bin --start 0x00

Workflow:

    .bin
      ↓
    Load Machine Code
      ↓
    MiniCPU Memory
      ↓
    CPU
      ↓
    Fetch
      ↓
    Decode
      ↓
    Execute
      ↓
    HALT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


# ============================================================
# PROJECT IMPORT
# ============================================================

try:
    from cpu.cpu import CPU
except ImportError as exc:

    print(
        "Error: Unable to import CPU.",
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

DEFAULT_START_ADDRESS = 0x00

DEFAULT_MAX_CYCLES = 100000


# ============================================================
# ARGUMENT PARSER
# ============================================================


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="simulate",
        description=(
            "Run MiniCPU 8-bit machine code "
            "in the CPU simulator."
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
        "--start",
        type=parse_byte,
        default=DEFAULT_START_ADDRESS,
        help=(
            "Program start address "
            "(default: 0x00)."
        ),
    )

    parser.add_argument(
        "--max-cycles",
        type=int,
        default=DEFAULT_MAX_CYCLES,
        help=(
            "Maximum CPU cycles before stopping "
            "(default: 100000)."
        ),
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help=(
            "Enable debug output if supported "
            "by the CPU."
        ),
    )

    parser.add_argument(
        "--dump-memory",
        action="store_true",
        help=(
            "Print memory contents after execution."
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
# PROGRAM READING
# ============================================================


def read_program(
    path: Path,
) -> bytes:
    """
    Read binary program file.
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

        program = path.read_bytes()

    except OSError as exc:

        raise OSError(
            f"Unable to read program: {path}"
        ) from exc

    if len(
        program
    ) > MEMORY_SIZE:

        raise ValueError(
            "Program is larger than MiniCPU "
            f"memory ({MEMORY_SIZE} bytes)."
        )

    return program


# ============================================================
# CPU CREATION
# ============================================================


def create_cpu():
    """
    Create MiniCPU instance.
    """

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

    raise RuntimeError(
        "Unable to construct CPU: "
        f"{last_error}"
    )


# ============================================================
# PROGRAM LOADING
# ============================================================


def load_program(
    cpu,
    program: bytes,
    start_address: int,
) -> None:
    """
    Load machine code into CPU memory.
    """

    methods = (
        "load_program",
        "load_code",
        "load_memory",
        "load",
    )

    # --------------------------------------------------------
    # Preferred API
    # --------------------------------------------------------

    for method_name in methods:

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

        # Try:
        #
        # load_program(program, start_address)

        try:

            method(
                program,
                start_address,
            )

            return

        except TypeError:

            pass

        # Try:
        #
        # load_program(program)

        try:

            method(
                program
            )

            set_program_counter(
                cpu,
                start_address,
            )

            return

        except TypeError:

            pass

    # --------------------------------------------------------
    # Direct memory fallback
    # --------------------------------------------------------

    memory = getattr(
        cpu,
        "memory",
        None,
    )

    if memory is not None:

        for index, byte in enumerate(
            program
        ):

            address = (
                start_address
                + index
            )

            if address > MAX_BYTE:

                raise ValueError(
                    "Program exceeds "
                    "8-bit address space."
                )

            try:

                memory[address] = byte

            except (
                TypeError,
                IndexError,
            ):

                try:

                    memory.write(
                        address,
                        byte,
                    )

                except AttributeError:

                    break

            else:

                continue

    else:

        raise RuntimeError(
            "CPU does not provide "
            "a supported program-loading API."
        )

    set_program_counter(
        cpu,
        start_address,
    )


# ============================================================
# PROGRAM COUNTER
# ============================================================


def set_program_counter(
    cpu,
    address: int,
) -> None:
    """
    Set CPU program counter.
    """

    for method_name in (
        "set_program_counter",
        "set_pc",
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

        if callable(
            method
        ):

            try:

                method(
                    address
                )

                return

            except TypeError:

                pass

    for attribute_name in (
        "program_counter",
        "pc",
    ):

        if not hasattr(
            cpu,
            attribute_name,
        ):

            continue

        try:

            setattr(
                cpu,
                attribute_name,
                address,
            )

            return

        except AttributeError:

            continue

    # If CPU does not expose PC control,
    # assume its default PC is 0x00.
    if address != 0:

        raise RuntimeError(
            "Unable to set CPU Program Counter."
        )


# ============================================================
# CPU EXECUTION
# ============================================================


def run_cpu(
    cpu,
    max_cycles: int,
    debug: bool = False,
):
    """
    Run CPU until HALT or cycle limit.
    """

    if max_cycles <= 0:

        raise ValueError(
            "max_cycles must be greater than zero."
        )

    # --------------------------------------------------------
    # Debug mode
    # --------------------------------------------------------

    if debug:

        for method_name in (
            "debug_run",
            "run_debug",
        ):

            if hasattr(
                cpu,
                method_name,
            ):

                method = getattr(
                    cpu,
                    method_name,
                )

                if callable(
                    method
                ):

                    try:

                        return method(
                            max_cycles
                        )

                    except TypeError:

                        try:

                            return method()

                        except TypeError:

                            pass

    # --------------------------------------------------------
    # Standard run
    # --------------------------------------------------------

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

        # Try max_cycles argument.

        try:

            return method(
                max_cycles=max_cycles
            )

        except TypeError:

            pass

        # Try positional cycle limit.

        try:

            return method(
                max_cycles
            )

        except TypeError:

            pass

        # Try no arguments.

        try:

            return method()

        except TypeError:

            continue

    # --------------------------------------------------------
    # Step fallback
    # --------------------------------------------------------

    for step_name in (
        "step",
        "clock",
        "cycle",
    ):

        if not hasattr(
            cpu,
            step_name,
        ):

            continue

        step = getattr(
            cpu,
            step_name,
        )

        if not callable(
            step
        ):

            continue

        for cycle in range(
            max_cycles
        ):

            if is_cpu_halted(
                cpu
            ):

                return cycle

            step()

        raise RuntimeError(
            "CPU did not halt within "
            f"{max_cycles} cycles."
        )

    raise RuntimeError(
        "CPU does not expose "
        "a supported execution API."
    )


# ============================================================
# HALT STATE
# ============================================================


def is_cpu_halted(
    cpu,
) -> bool:
    """
    Check whether CPU is halted.
    """

    for name in (
        "halted",
        "is_halted",
    ):

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

                return bool(
                    value()
                )

            except TypeError:

                continue

        return bool(
            value
        )

    return False


# ============================================================
# MEMORY DUMP
# ============================================================


def get_memory(
    cpu,
):
    """
    Return CPU memory object.
    """

    for name in (
        "memory",
        "ram",
    ):

        if hasattr(
            cpu,
            name,
        ):

            return getattr(
                cpu,
                name,
            )

    return None


def dump_memory(
    cpu,
    start_address: int = 0x00,
    end_address: int = 0xFF,
) -> None:
    """
    Print memory in hexadecimal format.
    """

    memory = get_memory(
        cpu
    )

    if memory is None:

        print(
            "Memory dump unavailable."
        )

        return

    print()
    print(
        "Memory Dump"
    )
    print(
        "------------"
    )

    for base in range(
        start_address,
        end_address + 1,
        16,
    ):

        values = []

        for offset in range(
            16
        ):

            address = (
                base
                + offset
            )

            if address > end_address:

                break

            try:

                if hasattr(
                    memory,
                    "read",
                ):

                    value = memory.read(
                        address
                    )

                else:

                    value = memory[
                        address
                    ]

            except (
                IndexError,
                TypeError,
            ):

                break

            values.append(
                f"{value:02X}"
            )

        if values:

            print(
                f"{base:02X}: "
                + " ".join(
                    values
                )
            )


# ============================================================
# CPU STATE
# ============================================================


def print_cpu_state(
    cpu,
) -> None:
    """
    Print basic CPU state.
    """

    print()
    print(
        "CPU State"
    )
    print(
        "---------"
    )

    # Program Counter

    pc = None

    for name in (
        "program_counter",
        "pc",
    ):

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

                value = value()

            except TypeError:

                continue

        pc = value

        break

    if pc is not None:

        print(
            f"PC: 0x{pc:02X}"
        )

    # Halt state

    print(
        f"HALTED: "
        f"{is_cpu_halted(cpu)}"
    )


# ============================================================
# MAIN
# ============================================================


def main(
    argv=None,
) -> int:
    """
    Main simulator CLI entry point.
    """

    parser = create_argument_parser()

    args = parser.parse_args(
        argv
    )

    # --------------------------------------------------------
    # Validate cycle count
    # --------------------------------------------------------

    if args.max_cycles <= 0:

        parser.error(
            "--max-cycles must be greater than zero."
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
    # Create CPU
    # --------------------------------------------------------

    try:

        cpu = create_cpu()

    except RuntimeError as exc:

        print(
            f"Error: {exc}",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------------------------
    # Load program
    # --------------------------------------------------------

    try:

        load_program(
            cpu,
            program,
            args.start,
        )

    except (
        RuntimeError,
        ValueError,
    ) as exc:

        print(
            f"Error loading program: {exc}",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------------------------
    # Execute
    # --------------------------------------------------------

    print(
        "MiniCPU Simulator"
    )

    print(
        "-----------------"
    )

    print(
        f"Program: {args.program}"
    )

    print(
        f"Start address: "
        f"0x{args.start:02X}"
    )

    print(
        f"Program size: "
        f"{len(program)} byte(s)"
    )

    print()

    try:

        run_cpu(
            cpu,
            args.max_cycles,
            args.debug,
        )

    except Exception as exc:

        print(
            f"Simulation failed: {exc}",
            file=sys.stderr,
        )

        return 1

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    print_cpu_state(
        cpu
    )

    # --------------------------------------------------------
    # Memory dump
    # --------------------------------------------------------

    if args.dump_memory:

        dump_memory(
            cpu
        )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    if is_cpu_halted(
        cpu
    ):

        print()
        print(
            "Simulation completed: CPU halted."
        )

    else:

        print()
        print(
            "Simulation completed."
        )

    return 0


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":

    sys.exit(
        main()
    )
