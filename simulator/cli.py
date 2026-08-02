"""
cli.py

MiniCPU 8-bit CPU Architecture
Simulator Command Line Interface

Features:
    - Load binary program
    - Load HEX program
    - Run program
    - Step execution
    - Continue execution
    - Reset CPU
    - Add / remove breakpoints
    - Show registers
    - Show flags
    - Show memory
    - Show trace
    - Inspect CPU state
    - Interactive debugger shell

Expected simulator interface:

    simulator.load_program(...)
    simulator.run(...)
    simulator.step(...)
    simulator.reset(...)
    simulator.get_state(...)
    simulator.get_program_counter(...)
    simulator.is_halted(...)

The CLI is intentionally designed to be flexible
with the MiniCPU simulator implementation.
"""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path
from typing import Optional


class SimulatorCLI:
    """
    Interactive command-line interface for MiniCPU.

    Example:

        cli = SimulatorCLI(simulator)

        cli.run()

    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        simulator,
        runner=None,
        debugger=None,
        breakpoints=None,
        trace=None,
        memory_view=None,
    ):
        """
        Initialize CLI.

        Args:
            simulator:
                MiniCPU Simulator instance.

            runner:
                Optional Runner.

            debugger:
                Optional Debugger.

            breakpoints:
                Optional BreakpointManager.

            trace:
                Optional Trace.

            memory_view:
                Optional MemoryView.
        """

        if simulator is None:
            raise ValueError(
                "Simulator cannot be None."
            )

        self.simulator = simulator

        self.runner = runner

        self.debugger = debugger

        self.breakpoints = breakpoints

        self.trace = trace

        self.memory_view = memory_view

        self.running = True

    # ========================================================
    # START CLI
    # ========================================================

    def run(
        self,
    ) -> None:
        """
        Start interactive CLI.
        """

        self.running = True

        self._print_banner()

        while self.running:

            try:

                command = input(
                    "minicpu> "
                )

            except EOFError:

                print()

                break

            except KeyboardInterrupt:

                print()

                continue

            command = command.strip()

            if not command:

                continue

            try:

                self.execute_command(
                    command
                )

            except Exception as exc:

                print(
                    f"Error: {exc}"
                )

    # ========================================================
    # BANNER
    # ========================================================

    def _print_banner(
        self,
    ) -> None:
        """
        Print CLI banner.
        """

        print()
        print(
            "=============================================="
        )
        print(
            "        MiniCPU 8-bit Simulator"
        )
        print(
            "=============================================="
        )
        print(
            "Type 'help' for available commands."
        )
        print()

    # ========================================================
    # COMMAND EXECUTION
    # ========================================================

    def execute_command(
        self,
        command_line: str,
    ):
        """
        Parse and execute a command.
        """

        try:

            parts = shlex.split(
                command_line
            )

        except ValueError as exc:

            raise ValueError(
                f"Invalid command: {exc}"
            )

        if not parts:

            return None

        command = (
            parts[0]
            .lower()
        )

        args = parts[1:]

        commands = {

            "help":
                self.command_help,

            "?":
                self.command_help,

            "load":
                self.command_load,

            "run":
                self.command_run,

            "continue":
                self.command_continue,

            "c":
                self.command_continue,

            "step":
                self.command_step,

            "s":
                self.command_step,

            "next":
                self.command_step,

            "reset":
                self.command_reset,

            "restart":
                self.command_reset,

            "break":
                self.command_break,

            "b":
                self.command_break,

            "delete":
                self.command_delete_breakpoint,

            "clear":
                self.command_clear_breakpoints,

            "breakpoints":
                self.command_breakpoints,

            "bp":
                self.command_breakpoints,

            "registers":
                self.command_registers,

            "regs":
                self.command_registers,

            "flags":
                self.command_flags,

            "memory":
                self.command_memory,

            "mem":
                self.command_memory,

            "trace":
                self.command_trace,

            "state":
                self.command_state,

            "pc":
                self.command_pc,

            "quit":
                self.command_quit,

            "exit":
                self.command_quit,
        }

        handler = commands.get(
            command
        )

        if handler is None:

            print(
                f"Unknown command: "
                f"{command}"
            )

            print(
                "Type 'help' for help."
            )

            return None

        return handler(
            args
        )

    # ========================================================
    # HELP
    # ========================================================

    def command_help(
        self,
        args=None,
    ) -> None:
        """
        Show available commands.
        """

        print()
        print(
            "MiniCPU Debugger Commands"
        )
        print(
            "-------------------------"
        )

        print(
            "help"
        )
        print(
            "    Show this help."
        )

        print(
            "load <file>"
        )
        print(
            "    Load binary or HEX program."
        )

        print(
            "run"
        )
        print(
            "    Start program execution."
        )

        print(
            "continue"
        )
        print(
            "    Continue execution."
        )

        print(
            "step"
        )
        print(
            "    Execute one instruction."
        )

        print(
            "reset"
        )
        print(
            "    Reset CPU and simulator."
        )

        print(
            "break <address>"
        )
        print(
            "    Add breakpoint."
        )

        print(
            "break <address> temporary"
        )
        print(
            "    Add temporary breakpoint."
        )

        print(
            "delete <address>"
        )
        print(
            "    Remove breakpoint."
        )

        print(
            "clear"
        )
        print(
            "    Clear all breakpoints."
        )

        print(
            "breakpoints"
        )
        print(
            "    Show all breakpoints."
        )

        print(
            "registers"
        )
        print(
            "    Show CPU registers."
        )

        print(
            "flags"
        )
        print(
            "    Show CPU flags."
        )

        print(
            "memory <address> [length]"
        )
        print(
            "    Show memory."
        )

        print(
            "trace [count]"
        )
        print(
            "    Show execution trace."
        )

        print(
            "state"
        )
        print(
            "    Show complete CPU state."
        )

        print(
            "pc"
        )
        print(
            "    Show Program Counter."
        )

        print(
            "quit"
        )
        print(
            "    Exit simulator."
        )

        print()

    # ========================================================
    # LOAD
    # ========================================================

    def command_load(
        self,
        args,
    ) -> None:
        """
        Load program from file.
        """

        if len(args) != 1:

            print(
                "Usage: load <file>"
            )

            return

        path = Path(
            args[0]
        )

        if not path.exists():

            print(
                f"File not found: "
                f"{path}"
            )

            return

        suffix = (
            path.suffix
            .lower()
        )

        if suffix in (
            ".hex",
            ".ihx",
        ):

            self._load_hex(
                path
            )

        else:

            self._load_binary(
                path
            )

    # ========================================================
    # LOAD BINARY
    # ========================================================

    def _load_binary(
        self,
        path: Path,
    ) -> None:
        """
        Load raw binary program.
        """

        data = path.read_bytes()

        if len(data) > 256:

            raise ValueError(
                "Program is larger than "
                "8-bit address space."
            )

        if hasattr(
            self.simulator,
            "load_program",
        ):

            self.simulator.load_program(
                data
            )

        else:

            raise RuntimeError(
                "Simulator does not provide "
                "load_program()."
            )

        print(
            f"Loaded {len(data)} bytes "
            f"from {path}"
        )

    # ========================================================
    # LOAD HEX
    # ========================================================

    def _load_hex(
        self,
        path: Path,
    ) -> None:
        """
        Load simple HEX byte file.

        Supported formats:

            10 20 30 FF

        or:

            102030FF

        Lines beginning with '#' or ';'
        are treated as comments.
        """

        text = path.read_text(
            encoding="utf-8"
        )

        data = []

        for line in text.splitlines():

            line = line.strip()

            if not line:

                continue

            if line.startswith(
                "#"
            ):

                continue

            if line.startswith(
                ";"
            ):

                continue

            line = line.replace(
                "0x",
                "",
            )

            line = line.replace(
                "0X",
                "",
            )

            parts = line.split()

            if len(parts) == 1:

                compact = parts[0]

                if (
                    len(compact) % 2
                    != 0
                ):

                    raise ValueError(
                        "Invalid HEX line: "
                        f"{line}"
                    )

                parts = [
                    compact[index:index + 2]
                    for index
                    in range(
                        0,
                        len(compact),
                        2,
                    )
                ]

            for part in parts:

                try:

                    value = int(
                        part,
                        16,
                    )

                except ValueError as exc:

                    raise ValueError(
                        f"Invalid HEX byte: "
                        f"{part}"
                    ) from exc

                if not (
                    0
                    <= value
                    <= 0xFF
                ):

                    raise ValueError(
                        f"HEX byte out of range: "
                        f"{part}"
                    )

                data.append(
                    value
                )

        self.simulator.load_program(
            bytes(data)
        )

        print(
            f"Loaded {len(data)} bytes "
            f"from {path}"
        )

    # ========================================================
    # RUN
    # ========================================================

    def command_run(
        self,
        args,
    ) -> None:
        """
        Start program execution.
        """

        max_steps = (
            self._parse_optional_int(
                args,
                0,
            )
        )

        if self.debugger is not None:

            executed = (
                self.debugger
                .continue_run(
                    max_steps=max_steps
                )
            )

            print(
                f"Executed {executed} "
                f"instruction(s)."
            )

            return

        if hasattr(
            self.simulator,
            "run",
        ):

            if max_steps is None:

                self.simulator.run()

            else:

                self.simulator.run(
                    max_steps=max_steps
                )

            return

        if self.runner is not None:

            self.runner.run(
                max_steps=max_steps
            )

            return

        raise RuntimeError(
            "No execution interface available."
        )

    # ========================================================
    # CONTINUE
    # ========================================================

    def command_continue(
        self,
        args,
    ) -> None:
        """
        Continue execution.
        """

        max_steps = (
            self._parse_optional_int(
                args,
                0,
            )
        )

        if self.debugger is None:

            return self.command_run(
                args
            )

        executed = (
            self.debugger
            .continue_run(
                max_steps=max_steps
            )
        )

        print(
            f"Executed {executed} "
            f"instruction(s)."
        )

    # ========================================================
    # STEP
    # ========================================================

    def command_step(
        self,
        args,
    ) -> None:
        """
        Execute one instruction.
        """

        if self.debugger is not None:

            result = (
                self.debugger
                .step()
            )

        elif self.runner is not None:

            result = (
                self.runner.step()
            )

        elif hasattr(
            self.simulator,
            "step",
        ):

            result = (
                self.simulator.step()
            )

        else:

            raise RuntimeError(
                "No step execution interface."
            )

        print(
            f"Result: {result}"
        )

        self.command_pc(
            []
        )

    # ========================================================
    # RESET
    # ========================================================

    def command_reset(
        self,
        args,
    ) -> None:
        """
        Reset simulator.
        """

        if self.debugger is not None:

            self.debugger.reset()

        elif hasattr(
            self.simulator,
            "reset",
        ):

            self.simulator.reset()

        else:

            raise RuntimeError(
                "Simulator does not "
                "provide reset()."
            )

        print(
            "CPU reset."
        )

    # ========================================================
    # BREAKPOINT
    # ========================================================

    def command_break(
        self,
        args,
    ) -> None:
        """
        Add breakpoint.
        """

        if not args:

            print(
                "Usage: break <address> "
                "[temporary]"
            )

            return

        address = (
            self.parse_number(
                args[0]
            )
        )

        temporary = (
            len(args) > 1
            and args[1].lower()
            in (
                "temporary",
                "temp",
                "t",
            )
        )

        if self.debugger is not None:

            breakpoint = (
                self.debugger
                .add_breakpoint(
                    address,
                    temporary=temporary,
                )
            )

        elif self.breakpoints is not None:

            breakpoint = (
                self.breakpoints
                .add_breakpoint(
                    address,
                    temporary=temporary,
                )
            )

        else:

            raise RuntimeError(
                "Breakpoint manager "
                "is not available."
            )

        print(
            f"Breakpoint set at "
            f"0x{breakpoint.address:02X}"
        )

    # ========================================================
    # DELETE BREAKPOINT
    # ========================================================

    def command_delete_breakpoint(
        self,
        args,
    ) -> None:
        """
        Remove breakpoint.
        """

        if len(args) != 1:

            print(
                "Usage: delete <address>"
            )

            return

        address = (
            self.parse_number(
                args[0]
            )
        )

        if self.debugger is not None:

            removed = (
                self.debugger
                .remove_breakpoint(
                    address
                )
            )

        elif self.breakpoints is not None:

            removed = (
                self.breakpoints
                .remove_breakpoint(
                    address
                )
            )

        else:

            removed = False

        if removed:

            print(
                f"Breakpoint removed "
                f"from 0x{address:02X}"
            )

        else:

            print(
                "Breakpoint not found."
            )

    # ========================================================
    # CLEAR BREAKPOINTS
    # ========================================================

    def command_clear_breakpoints(
        self,
        args,
    ) -> None:
        """
        Remove all breakpoints.
        """

        if self.debugger is not None:

            self.debugger.clear_breakpoints()

        elif self.breakpoints is not None:

            self.breakpoints.clear()

        else:

            print(
                "Breakpoint manager "
                "is not available."
            )

            return

        print(
            "All breakpoints cleared."
        )

    # ========================================================
    # SHOW BREAKPOINTS
    # ========================================================

    def command_breakpoints(
        self,
        args,
    ) -> None:
        """
        Display breakpoints.
        """

        if self.breakpoints is None:

            print(
                "Breakpoint manager "
                "is not available."
            )

            return

        self.breakpoints.dump()

    # ========================================================
    # REGISTERS
    # ========================================================

    def command_registers(
        self,
        args,
    ) -> None:
        """
        Display registers.
        """

        if self.debugger is not None:

            registers = (
                self.debugger
                .get_registers()
            )

        else:

            registers = getattr(
                self.simulator,
                "registers",
                None,
            )

            if registers is not None:

                if hasattr(
                    registers,
                    "snapshot",
                ):

                    registers = (
                        registers
                        .snapshot()
                    )

                elif hasattr(
                    registers,
                    "dump",
                ):

                    registers.dump()

                    return

        if registers is None:

            print(
                "Register state unavailable."
            )

            return

        print(
            "========== REGISTERS =========="
        )

        if isinstance(
            registers,
            dict,
        ):

            for name, value in (
                registers.items()
            ):

                if isinstance(
                    value,
                    int,
                ):

                    print(
                        f"{name:<12} "
                        f"0x{value:02X} "
                        f"({value})"
                    )

                else:

                    print(
                        f"{name:<12} "
                        f"{value}"
                    )

        else:

            print(
                registers
            )

        print(
            "==============================="
        )

    # ========================================================
    # FLAGS
    # ========================================================

    def command_flags(
        self,
        args,
    ) -> None:
        """
        Display CPU flags.
        """

        if self.debugger is not None:

            flags = (
                self.debugger
                .get_flags()
            )

        else:

            flags = getattr(
                self.simulator,
                "flags",
                None,
            )

            if flags is not None:

                if hasattr(
                    flags,
                    "snapshot",
                ):

                    flags = (
                        flags
                        .snapshot()
                    )

                elif hasattr(
                    flags,
                    "get_all",
                ):

                    flags = (
                        flags
                        .get_all()
                    )

        if flags is None:

            print(
                "Flag state unavailable."
            )

            return

        print(
            "============= FLAGS ============="
        )

        if isinstance(
            flags,
            dict,
        ):

            for name, value in (
                flags.items()
            ):

                print(
                    f"{name:<12} "
                    f"{value}"
                )

        else:

            print(
                flags
            )

        print(
            "================================="
        )

    # ========================================================
    # MEMORY
    # ========================================================

    def command_memory(
        self,
        args,
    ) -> None:
        """
        Display memory.
        """

        if not args:

            print(
                "Usage: memory "
                "<address> [length]"
            )

            return

        address = (
            self.parse_number(
                args[0]
            )
        )

        length = 16

        if len(args) > 1:

            length = (
                self.parse_number(
                    args[1]
                )
            )

        if self.memory_view is None:

            print(
                "MemoryView is not available."
            )

            return

        self.memory_view.dump(
            address,
            length,
        )

    # ========================================================
    # TRACE
    # ========================================================

    def command_trace(
        self,
        args,
    ) -> None:
        """
        Display execution trace.
        """

        count = None

        if args:

            count = (
                self.parse_number(
                    args[0]
                )
            )

        if self.trace is None:

            print(
                "Trace is not available."
            )

            return

        self.trace.dump(
            limit=count
        )

    # ========================================================
    # STATE
    # ========================================================

    def command_state(
        self,
        args,
    ) -> None:
        """
        Display complete simulator state.
        """

        if self.debugger is not None:

            state = (
                self.debugger
                .get_state()
            )

        elif hasattr(
            self.simulator,
            "get_state",
        ):

            state = (
                self.simulator
                .get_state()
            )

        else:

            state = {}

        print(
            "============= CPU STATE ============="
        )

        self._print_value(
            state
        )

        print(
            "======================================"
        )

    # ========================================================
    # PROGRAM COUNTER
    # ========================================================

    def command_pc(
        self,
        args,
    ) -> None:
        """
        Display Program Counter.
        """

        if hasattr(
            self.simulator,
            "get_program_counter",
        ):

            pc = (
                self.simulator
                .get_program_counter()
            )

        else:

            pc = getattr(
                self.simulator,
                "program_counter",
                None,
            )

            if pc is not None:

                if hasattr(
                    pc,
                    "get",
                ):

                    pc = pc.get()

                elif hasattr(
                    pc,
                    "value",
                ):

                    pc = pc.value

        if pc is None:

            print(
                "Program Counter unavailable."
            )

            return

        print(
            f"PC = 0x{pc:02X} "
            f"({pc})"
        )

    # ========================================================
    # QUIT
    # ========================================================

    def command_quit(
        self,
        args,
    ) -> None:
        """
        Exit CLI.
        """

        self.running = False

        print(
            "Exiting MiniCPU simulator."
        )

    # ========================================================
    # NUMBER PARSER
    # ========================================================

    @staticmethod
    def parse_number(
        value: str,
    ) -> int:
        """
        Parse integer.

        Supported:

            10
            0x10
            0X10
            $10
            10h
        """

        value = (
            value
            .strip()
            .lower()
        )

        if value.startswith(
            "$"
        ):

            return int(
                value[1:],
                16,
            )

        if value.endswith(
            "h"
        ):

            return int(
                value[:-1],
                16,
            )

        return int(
            value,
            0,
        )

    # ========================================================
    # OPTIONAL INTEGER
    # ========================================================

    @classmethod
    def _parse_optional_int(
        cls,
        args,
        index: int,
    ) -> Optional[int]:
        """
        Parse optional integer argument.
        """

        if len(args) <= index:

            return None

        return cls.parse_number(
            args[index]
        )

    # ========================================================
    # PRINT VALUE
    # ========================================================

    def _print_value(
        self,
        value,
        indent: int = 0,
    ) -> None:
        """
        Recursively print dictionaries.
        """

        prefix = (
            " "
            * indent
        )

        if isinstance(
            value,
            dict,
        ):

            for key, item in (
                value.items()
            ):

                if isinstance(
                    item,
                    (
                        dict,
                        list,
                    ),
                ):

                    print(
                        f"{prefix}{key}:"
                    )

                    self._print_value(
                        item,
                        indent + 4,
                    )

                else:

                    print(
                        f"{prefix}"
                        f"{key}: "
                        f"{item}"
                    )

            return

        if isinstance(
            value,
            list,
        ):

            for item in value:

                self._print_value(
                    item,
                    indent + 4,
                )

            return

        print(
            f"{prefix}{value}"
        )


# ============================================================
# ARGUMENT PARSER
# ============================================================

def create_argument_parser():
    """
    Create command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        description=(
            "MiniCPU 8-bit Simulator"
        )
    )

    parser.add_argument(
        "program",
        nargs="?",
        help=(
            "Optional binary or HEX "
            "program file."
        ),
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help=(
            "Run program immediately."
        ),
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help=(
            "Maximum number of "
            "instructions to execute."
        ),
    )

    return parser


# ============================================================
# CLI FACTORY
# ============================================================

def create_cli(
    simulator,
    runner=None,
    debugger=None,
    breakpoints=None,
    trace=None,
    memory_view=None,
) -> SimulatorCLI:
    """
    Create configured SimulatorCLI.
    """

    return SimulatorCLI(
        simulator=simulator,
        runner=runner,
        debugger=debugger,
        breakpoints=breakpoints,
        trace=trace,
        memory_view=memory_view,
    )


# ============================================================
# MAIN
# ============================================================

def main(
    simulator=None,
    runner=None,
    debugger=None,
    breakpoints=None,
    trace=None,
    memory_view=None,
) -> int:
    """
    CLI entry point.

    If simulator is supplied, it is used directly.

    Otherwise this function attempts to import
    the simulator package.
    """

    if simulator is None:

        try:

            from .simulator import (
                Simulator,
            )

            simulator = Simulator()

        except ImportError as exc:

            print(
                "Unable to initialize "
                "MiniCPU Simulator:"
            )

            print(
                exc
            )

            return 1

    cli = create_cli(
        simulator=simulator,
        runner=runner,
        debugger=debugger,
        breakpoints=breakpoints,
        trace=trace,
        memory_view=memory_view,
    )

    parser = (
        create_argument_parser()
    )

    args = parser.parse_args()

    # --------------------------------------------------------
    # Load program
    # --------------------------------------------------------

    if args.program:

        cli.command_load(
            [
                args.program
            ]
        )

    # --------------------------------------------------------
    # Run directly
    # --------------------------------------------------------

    if args.run:

        run_args = []

        if args.steps is not None:

            run_args.append(
                str(
                    args.steps
                )
            )

        cli.command_run(
            run_args
        )

        return 0

    # --------------------------------------------------------
    # Interactive mode
    # --------------------------------------------------------

    cli.run()

    return 0


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "SimulatorCLI",
    "create_argument_parser",
    "create_cli",
    "main",
]


# ============================================================
# MODULE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
