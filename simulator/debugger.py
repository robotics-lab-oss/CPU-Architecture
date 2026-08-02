"""
debugger.py

MiniCPU 8-bit CPU Architecture
Debugger

Responsibilities:
    - Start / stop execution
    - Single-step execution
    - Continue execution
    - Breakpoint handling
    - Execution trace integration
    - CPU state inspection
    - Memory inspection
    - Register inspection
    - Debugger callbacks

The Debugger works with:

    Simulator
        |
        +── Runner
        |
        +── BreakpointManager
        |
        +── Trace

Typical workflow:

    debugger = Debugger(
        simulator,
        runner,
        breakpoints,
        trace,
    )

    debugger.step()
    debugger.continue_run()
    debugger.add_breakpoint(0x10)
"""

from __future__ import annotations

from typing import Callable, Optional


class Debugger:
    """
    High-level debugger for MiniCPU.

    The debugger coordinates program execution
    and inspection without directly implementing
    CPU instructions.
    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        simulator,
        runner=None,
        breakpoints=None,
        trace=None,
        on_break=None,
    ):
        """
        Initialize debugger.

        Args:
            simulator:
                MiniCPU Simulator instance.

            runner:
                Optional Runner instance.

            breakpoints:
                Optional BreakpointManager.

            trace:
                Optional Trace instance.

            on_break:
                Optional callback called when
                execution stops at a breakpoint.
        """

        if simulator is None:
            raise ValueError(
                "Simulator cannot be None."
            )

        self.simulator = simulator

        self.runner = runner

        self.breakpoints = breakpoints

        self.trace = trace

        self.on_break = on_break

        # ----------------------------------------------------
        # Debugger state
        # ----------------------------------------------------

        self.active = False

        self.paused = False

        self.last_breakpoint = None

        self.last_instruction = None

        self.last_result = None

        self.step_count = 0

    # ========================================================
    # ATTACH RUNNER
    # ========================================================

    def attach_runner(
        self,
        runner,
    ) -> None:
        """
        Attach a Runner instance.
        """

        if runner is None:
            raise ValueError(
                "Runner cannot be None."
            )

        self.runner = runner

    # ========================================================
    # ATTACH BREAKPOINT MANAGER
    # ========================================================

    def attach_breakpoints(
        self,
        breakpoints,
    ) -> None:
        """
        Attach BreakpointManager.
        """

        self.breakpoints = breakpoints

    # ========================================================
    # ATTACH TRACE
    # ========================================================

    def attach_trace(
        self,
        trace,
    ) -> None:
        """
        Attach Trace instance.
        """

        self.trace = trace

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(
        self,
    ) -> None:
        """
        Validate debugger dependencies.
        """

        if self.simulator is None:
            raise RuntimeError(
                "Debugger has no simulator."
            )

        if self.runner is None:
            raise RuntimeError(
                "Debugger has no runner."
            )

    # ========================================================
    # START DEBUGGING
    # ========================================================

    def start(
        self,
    ) -> None:
        """
        Start debugger session.
        """

        self.validate()

        self.active = True

        self.paused = False

        self.last_breakpoint = None

    # ========================================================
    # STOP DEBUGGING
    # ========================================================

    def stop(
        self,
    ) -> None:
        """
        Stop debugger session.
        """

        self.active = False

        self.paused = False

        if self.runner is not None:

            self.runner.stop()

    # ========================================================
    # STEP
    # ========================================================

    def step(
        self,
    ):
        """
        Execute exactly one instruction.

        Breakpoints are checked before execution.
        """

        self.validate()

        self.active = True

        self.paused = False

        current_pc = (
            self.simulator
            .get_program_counter()
        )

        # ----------------------------------------------------
        # Check breakpoint before execution
        # ----------------------------------------------------

        if self._has_breakpoint(
            current_pc
        ):

            self.last_breakpoint = (
                current_pc
            )

            self.paused = True

            self._notify_break(
                current_pc
            )

            return None

        # ----------------------------------------------------
        # Execute instruction
        # ----------------------------------------------------

        result = (
            self.runner.step()
        )

        self.last_result = result

        self.step_count += 1

        self.last_instruction = (
            self._get_last_instruction()
        )

        # ----------------------------------------------------
        # Record trace
        # ----------------------------------------------------

        self._record_trace()

        # ----------------------------------------------------
        # Check HALT
        # ----------------------------------------------------

        if self.simulator.is_halted():

            self.paused = True

        return result

    # ========================================================
    # CONTINUE
    # ========================================================

    def continue_run(
        self,
        max_steps: Optional[int] = None,
    ) -> int:
        """
        Continue execution until:

            - HALT
            - breakpoint
            - max_steps
            - stop
        """

        self.validate()

        self.active = True

        self.paused = False

        executed = 0

        while True:

            # ----------------------------------------------
            # HALT
            # ----------------------------------------------

            if self.simulator.is_halted():

                self.paused = True

                break

            # ----------------------------------------------
            # STEP LIMIT
            # ----------------------------------------------

            if (
                max_steps is not None
                and executed >= max_steps
            ):

                break

            # ----------------------------------------------
            # CURRENT PC
            # ----------------------------------------------

            pc = (
                self.simulator
                .get_program_counter()
            )

            # ----------------------------------------------
            # BREAKPOINT
            #
            # Ignore breakpoint at the very first
            # position only if it was reached by
            # a previous stop.
            # ----------------------------------------------

            if (
                self._has_breakpoint(pc)
                and executed > 0
            ):

                self.last_breakpoint = pc

                self.paused = True

                self.runner.stop()

                self._notify_break(
                    pc
                )

                break

            # ----------------------------------------------
            # EXECUTE
            # ----------------------------------------------

            self.runner.step()

            executed += 1

            self.step_count += 1

            self.last_result = (
                self.runner.last_result
            )

            self.last_instruction = (
                self._get_last_instruction()
            )

            # ----------------------------------------------
            # TRACE
            # ----------------------------------------------

            self._record_trace()

            # ----------------------------------------------
            # HALT AFTER EXECUTION
            # ----------------------------------------------

            if self.simulator.is_halted():

                self.paused = True

                break

        return executed

    # ========================================================
    # CONTINUE FROM BREAKPOINT
    # ========================================================

    def continue_from_breakpoint(
        self,
        max_steps: Optional[int] = None,
    ) -> int:
        """
        Continue execution after hitting a breakpoint.

        First instruction at current PC is executed,
        then normal breakpoint checking resumes.
        """

        self.validate()

        self.paused = False

        executed = 0

        # ----------------------------------------------------
        # Execute current instruction first
        # ----------------------------------------------------

        if not self.simulator.is_halted():

            self.runner.step()

            executed += 1

            self.step_count += 1

            self.last_result = (
                self.runner.last_result
            )

            self.last_instruction = (
                self._get_last_instruction()
            )

            self._record_trace()

        # ----------------------------------------------------
        # Continue normally
        # ----------------------------------------------------

        remaining = None

        if max_steps is not None:

            remaining = max(
                0,
                max_steps - executed,
            )

        if (
            remaining is None
            or remaining > 0
        ):

            executed += (
                self.continue_run(
                    max_steps=remaining
                )
            )

        return executed

    # ========================================================
    # BREAKPOINT HELPERS
    # ========================================================

    def _has_breakpoint(
        self,
        address: int,
    ) -> bool:
        """
        Return True if address has an active breakpoint.
        """

        if self.breakpoints is None:

            return False

        if hasattr(
            self.breakpoints,
            "has_breakpoint",
        ):

            return bool(
                self.breakpoints
                .has_breakpoint(
                    address
                )
            )

        if hasattr(
            self.breakpoints,
            "contains",
        ):

            return bool(
                self.breakpoints.contains(
                    address
                )
            )

        if hasattr(
            self.breakpoints,
            "is_breakpoint",
        ):

            return bool(
                self.breakpoints
                .is_breakpoint(
                    address
                )
            )

        return False

    # ========================================================
    # ADD BREAKPOINT
    # ========================================================

    def add_breakpoint(
        self,
        address: int,
        temporary: bool = False,
    ):
        """
        Add a breakpoint.

        Supports different BreakpointManager APIs.
        """

        if self.breakpoints is None:

            raise RuntimeError(
                "BreakpointManager is not attached."
            )

        if hasattr(
            self.breakpoints,
            "add_breakpoint",
        ):

            return (
                self.breakpoints
                .add_breakpoint(
                    address,
                    temporary=temporary,
                )
            )

        if hasattr(
            self.breakpoints,
            "add",
        ):

            return (
                self.breakpoints.add(
                    address
                )
            )

        raise AttributeError(
            "BreakpointManager does not "
            "provide breakpoint add operation."
        )

    # ========================================================
    # REMOVE BREAKPOINT
    # ========================================================

    def remove_breakpoint(
        self,
        address: int,
    ) -> bool:
        """
        Remove a breakpoint.
        """

        if self.breakpoints is None:

            return False

        if hasattr(
            self.breakpoints,
            "remove_breakpoint",
        ):

            return bool(
                self.breakpoints
                .remove_breakpoint(
                    address
                )
            )

        if hasattr(
            self.breakpoints,
            "remove",
        ):

            return bool(
                self.breakpoints.remove(
                    address
                )
            )

        return False

    # ========================================================
    # CLEAR BREAKPOINTS
    # ========================================================

    def clear_breakpoints(
        self,
    ) -> None:
        """
        Remove all breakpoints.
        """

        if self.breakpoints is None:

            return

        if hasattr(
            self.breakpoints,
            "clear",
        ):

            self.breakpoints.clear()

        elif hasattr(
            self.breakpoints,
            "clear_all",
        ):

            self.breakpoints.clear_all()

    # ========================================================
    # BREAK CALLBACK
    # ========================================================

    def _notify_break(
        self,
        address: int,
    ) -> None:
        """
        Notify debugger breakpoint callback.
        """

        if callable(
            self.on_break
        ):

            self.on_break(
                self,
                address,
            )

    # ========================================================
    # TRACE
    # ========================================================

    def _record_trace(
        self,
    ) -> None:
        """
        Record current execution state.

        The Trace class can expose different
        APIs, so supported methods are checked
        dynamically.
        """

        if self.trace is None:

            return

        state = (
            self.get_state()
        )

        if hasattr(
            self.trace,
            "record",
        ):

            try:

                self.trace.record(
                    state
                )

            except TypeError:

                self.trace.record(
                    pc=state[
                        "program_counter"
                    ],
                    state=state,
                )

            return

        if hasattr(
            self.trace,
            "add",
        ):

            self.trace.add(
                state
            )

    # ========================================================
    # LAST INSTRUCTION
    # ========================================================

    def _get_last_instruction(
        self,
    ):
        """
        Try to retrieve the last decoded instruction.
        """

        executor = getattr(
            self.simulator,
            "instruction_executor",
            None,
        )

        if executor is not None:

            if hasattr(
                executor,
                "last_instruction",
            ):

                return (
                    executor
                    .last_instruction
                )

        return None

    # ========================================================
    # GET STATE
    # ========================================================

    def get_state(
        self,
    ) -> dict:
        """
        Return current debugger state.
        """

        state = {
            "active": self.active,
            "paused": self.paused,
            "step_count": (
                self.step_count
            ),
            "last_breakpoint": (
                self.last_breakpoint
            ),
            "last_instruction": (
                self.last_instruction
            ),
            "last_result": (
                self.last_result
            ),
            "program_counter": (
                self.simulator
                .get_program_counter()
            ),
        }

        # ----------------------------------------------------
        # Add simulator state
        # ----------------------------------------------------

        if hasattr(
            self.simulator,
            "get_state",
        ):

            state[
                "simulator"
            ] = (
                self.simulator
                .get_state()
            )

        # ----------------------------------------------------
        # Add runner state
        # ----------------------------------------------------

        if self.runner is not None:

            if hasattr(
                self.runner,
                "get_statistics",
            ):

                state[
                    "runner"
                ] = (
                    self.runner
                    .get_statistics()
                )

        return state

    # ========================================================
    # REGISTER INSPECTION
    # ========================================================

    def get_registers(
        self,
    ):
        """
        Return CPU register state.
        """

        registers = (
            getattr(
                self.simulator,
                "registers",
                None,
            )
        )

        if registers is None:

            return None

        if hasattr(
            registers,
            "snapshot",
        ):

            return (
                registers
                .snapshot()
            )

        if hasattr(
            registers,
            "dump",
        ):

            return (
                registers
                .dump()
            )

        if hasattr(
            registers,
            "registers",
        ):

            return dict(
                registers.registers
            )

        return None

    # ========================================================
    # FLAG INSPECTION
    # ========================================================

    def get_flags(
        self,
    ):
        """
        Return CPU flags.
        """

        flags = (
            getattr(
                self.simulator,
                "flags",
                None,
            )
        )

        if flags is None:

            return None

        if hasattr(
            flags,
            "snapshot",
        ):

            return (
                flags
                .snapshot()
            )

        if hasattr(
            flags,
            "get_all",
        ):

            return (
                flags
                .get_all()
            )

        return None

    # ========================================================
    # MEMORY INSPECTION
    # ========================================================

    def read_memory(
        self,
        address: int,
    ) -> int:
        """
        Read a single memory location.
        """

        return (
            self.simulator
            .read_memory(
                address
            )
        )

    # --------------------------------------------------------

    def memory_dump(
        self,
        start_address: int = 0x00,
        length: int = 16,
    ):
        """
        Read a memory range.
        """

        return (
            self.simulator
            .memory_dump(
                start_address,
                length,
            )
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        reset_cpu: bool = True,
    ) -> None:
        """
        Reset debugger state.

        Args:
            reset_cpu:
                Also reset simulator.
        """

        self.active = False

        self.paused = False

        self.last_breakpoint = None

        self.last_instruction = None

        self.last_result = None

        self.step_count = 0

        if self.runner is not None:

            self.runner.reset(
                reset_cpu=False
            )

        if reset_cpu:

            self.simulator.reset()

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print debugger state.
        """

        state = (
            self.get_state()
        )

        print(
            "============== MINICPU DEBUGGER =============="
        )

        print(
            f"Active          : "
            f"{state['active']}"
        )

        print(
            f"Paused          : "
            f"{state['paused']}"
        )

        print(
            f"Program Counter : "
            f"0x"
            f"{state['program_counter']:02X}"
        )

        print(
            f"Step Count      : "
            f"{state['step_count']}"
        )

        print(
            f"Last Breakpoint : "
            f"{state['last_breakpoint']}"
        )

        print(
            f"Last Result     : "
            f"{state['last_result']}"
        )

        print(
            "==============================================="
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable debugger state.
        """

        return (
            f"Debugger("
            f"active={self.active}, "
            f"paused={self.paused}, "
            f"steps={self.step_count}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Debugger",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Debugger"
    )

    print()

    print(
        "Debugger module loaded successfully."
    )

    print()

    print(
        "Supported operations:"
    )

    print(
        "  debugger.start()"
    )

    print(
        "  debugger.step()"
    )

    print(
        "  debugger.continue_run()"
    )

    print(
        "  debugger.add_breakpoint(0x10)"
    )

    print(
        "  debugger.remove_breakpoint(0x10)"
    )

    print(
        "  debugger.get_state()"
    )

    print(
        "  debugger.dump()"
    )
