"""
runner.py

MiniCPU 8-bit CPU Architecture
Program Runner

Responsibilities:
    - Run loaded programs
    - Execute single instructions
    - Execute limited number of steps
    - Pause and resume execution
    - Stop execution
    - Detect HALT
    - Track execution statistics
    - Provide execution callbacks

The Runner works on top of:

    simulator.simulator.Simulator

Execution flow:

    Runner
       |
       v
    Simulator
       |
       v
      CPU
       |
       +--> Fetch
       +--> Decode
       +--> Execute
"""

from __future__ import annotations

from typing import Callable, Optional


class Runner:
    """
    High-level execution controller for MiniCPU.

    Example:

        runner = Runner(simulator)

        runner.run()

    Single-step:

        runner.step()

    Limited execution:

        runner.run(max_steps=100)
    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        simulator,
        on_step: Optional[
            Callable
        ] = None,
        on_halt: Optional[
            Callable
        ] = None,
        on_error: Optional[
            Callable
        ] = None,
    ):
        """
        Initialize Runner.

        Args:
            simulator:
                Instance of simulator.Simulator.

            on_step:
                Optional callback called after
                each executed instruction.

            on_halt:
                Optional callback called when
                CPU reaches HALT.

            on_error:
                Optional callback called when
                execution raises an exception.
        """

        if simulator is None:

            raise ValueError(
                "Simulator cannot be None."
            )

        self.simulator = simulator

        self.on_step = on_step

        self.on_halt = on_halt

        self.on_error = on_error

        # ----------------------------------------------------
        # Runtime state
        # ----------------------------------------------------

        self.running = False

        self.paused = False

        self.stopped = False

        self.halted = False

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        self.total_steps = 0

        self.session_steps = 0

        self.last_result = None

        self.last_error = None

        # ----------------------------------------------------
        # Limits
        # ----------------------------------------------------

        self.max_steps = None

    # ========================================================
    # VALIDATION
    # ========================================================

    def validate(
        self,
    ) -> None:
        """
        Validate runner state before execution.
        """

        if self.simulator is None:

            raise RuntimeError(
                "Runner has no simulator."
            )

        if not self.simulator.loaded:

            raise RuntimeError(
                "No program is loaded "
                "in the simulator."
            )

    # ========================================================
    # STEP
    # ========================================================

    def step(
        self,
    ):
        """
        Execute exactly one instruction.

        Returns:
            Result returned by Simulator.step().
        """

        self.validate()

        if self.is_halted():

            self.halted = True

            return None

        if self.stopped:

            return None

        try:

            result = (
                self.simulator.step()
            )

            self.last_result = result

            self.total_steps += 1

            self.session_steps += 1

            # Check HALT after execution.

            if self.simulator.is_halted():

                self.halted = True

                self.running = False

                if callable(
                    self.on_halt
                ):

                    self.on_halt(
                        self
                    )

            # Step callback.

            if callable(
                self.on_step
            ):

                self.on_step(
                    self,
                    result,
                )

            return result

        except Exception as exc:

            self.last_error = exc

            self.running = False

            if callable(
                self.on_error
            ):

                self.on_error(
                    self,
                    exc,
                )

            raise

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        max_steps: Optional[
            int
        ] = None,
    ) -> int:
        """
        Run program until:

            - HALT
            - stop()
            - pause()
            - max_steps reached

        Args:
            max_steps:
                Maximum instructions to execute.

                None means unlimited.

        Returns:
            Number of instructions executed
            during this run session.
        """

        self.validate()

        if (
            max_steps is not None
            and (
                not isinstance(
                    max_steps,
                    int,
                )
                or max_steps < 0
            )
        ):

            raise ValueError(
                "max_steps must be a "
                "non-negative integer "
                "or None."
            )

        self.max_steps = max_steps

        self.running = True

        self.paused = False

        self.stopped = False

        self.halted = (
            self.simulator.is_halted()
        )

        self.session_steps = 0

        if self.halted:

            self.running = False

            if callable(
                self.on_halt
            ):

                self.on_halt(
                    self
                )

            return 0

        executed = 0

        while self.running:

            # ----------------------------------------------
            # HALT CHECK
            # ----------------------------------------------

            if self.simulator.is_halted():

                self.halted = True

                self.running = False

                break

            # ----------------------------------------------
            # PAUSE CHECK
            # ----------------------------------------------

            if self.paused:

                self.running = False

                break

            # ----------------------------------------------
            # STOP CHECK
            # ----------------------------------------------

            if self.stopped:

                self.running = False

                break

            # ----------------------------------------------
            # STEP LIMIT
            # ----------------------------------------------

            if (
                max_steps is not None
                and executed
                >= max_steps
            ):

                break

            # ----------------------------------------------
            # EXECUTE
            # ----------------------------------------------

            self.step()

            executed += 1

        self.running = False

        return executed

    # ========================================================
    # RUN FOREVER
    # ========================================================

    def run_forever(
        self,
    ) -> int:
        """
        Run program without an explicit
        instruction limit.

        Execution ends when:

            - HALT
            - pause
            - stop
            - exception
        """

        return self.run(
            max_steps=None
        )

    # ========================================================
    # PAUSE
    # ========================================================

    def pause(
        self,
    ) -> None:
        """
        Pause execution.

        The current instruction finishes first.
        """

        self.paused = True

        self.running = False

    # ========================================================
    # RESUME
    # ========================================================

    def resume(
        self,
        max_steps: Optional[
            int
        ] = None,
    ) -> int:
        """
        Resume execution after pause.

        If CPU is halted, resume will not
        execute until CPU is reset or otherwise
        released from HALT state.
        """

        if self.is_halted():

            return 0

        self.paused = False

        self.stopped = False

        return self.run(
            max_steps=max_steps
        )

    # ========================================================
    # STOP
    # ========================================================

    def stop(
        self,
    ) -> None:
        """
        Stop execution.

        This does not reset the CPU.
        """

        self.stopped = True

        self.running = False

    # ========================================================
    # RESET RUNNER
    # ========================================================

    def reset(
        self,
        reset_cpu: bool = False,
    ) -> None:
        """
        Reset runner state.

        Args:
            reset_cpu:
                If True, also reset the simulator.
        """

        self.running = False

        self.paused = False

        self.stopped = False

        self.halted = False

        self.session_steps = 0

        self.last_result = None

        self.last_error = None

        if reset_cpu:

            self.simulator.reset()

    # ========================================================
    # CPU RESET AND RUN
    # ========================================================

    def restart(
        self,
        max_steps: Optional[
            int
        ] = None,
    ) -> int:
        """
        Reset CPU and execute program
        from the beginning.
        """

        self.reset(
            reset_cpu=True
        )

        return self.run(
            max_steps=max_steps
        )

    # ========================================================
    # STATUS
    # ========================================================

    def is_running(
        self,
    ) -> bool:
        """
        Return True if runner is executing.
        """

        return self.running

    # --------------------------------------------------------

    def is_paused(
        self,
    ) -> bool:
        """
        Return True if runner is paused.
        """

        return self.paused

    # --------------------------------------------------------

    def is_stopped(
        self,
    ) -> bool:
        """
        Return True if runner was stopped.
        """

        return self.stopped

    # --------------------------------------------------------

    def is_halted(
        self,
    ) -> bool:
        """
        Return True if CPU is halted.
        """

        return (
            self.halted
            or self.simulator.is_halted()
        )

    # ========================================================
    # STATISTICS
    # ========================================================

    def get_statistics(
        self,
    ) -> dict:
        """
        Return execution statistics.
        """

        return {
            "running": self.running,
            "paused": self.paused,
            "stopped": self.stopped,
            "halted": self.is_halted(),
            "total_steps": (
                self.total_steps
            ),
            "session_steps": (
                self.session_steps
            ),
            "last_result": (
                self.last_result
            ),
            "last_error": (
                str(self.last_error)
                if self.last_error
                else None
            ),
            "max_steps": (
                self.max_steps
            ),
        }

    # ========================================================
    # CURRENT STATE
    # ========================================================

    def get_state(
        self,
    ) -> dict:
        """
        Return combined Runner and
        Simulator state.
        """

        return {
            "runner": self.get_statistics(),
            "simulator": (
                self.simulator.get_state()
            ),
        }

    # ========================================================
    # PROGRAM COUNTER
    # ========================================================

    def get_program_counter(
        self,
    ) -> int:
        """
        Return current PC.
        """

        return (
            self.simulator
            .get_program_counter()
        )

    # ========================================================
    # MEMORY
    # ========================================================

    def read_memory(
        self,
        address: int,
    ) -> int:
        """
        Read memory through Simulator.
        """

        return (
            self.simulator
            .read_memory(
                address
            )
        )

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print runner state.
        """

        print(
            "============= CPU RUNNER ============="
        )

        print(
            f"Running       : "
            f"{self.running}"
        )

        print(
            f"Paused        : "
            f"{self.paused}"
        )

        print(
            f"Stopped       : "
            f"{self.stopped}"
        )

        print(
            f"Halted        : "
            f"{self.is_halted()}"
        )

        print(
            f"Total Steps   : "
            f"{self.total_steps}"
        )

        print(
            f"Session Steps : "
            f"{self.session_steps}"
        )

        print(
            f"Program Counter: "
            f"0x"
            f"{self.get_program_counter():02X}"
        )

        print(
            "======================================="
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable Runner state.
        """

        return (
            f"Runner("
            f"running={self.running}, "
            f"paused={self.paused}, "
            f"halted={self.is_halted()}, "
            f"steps={self.total_steps}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Runner",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Program Runner"
    )

    print()

    print(
        "Runner module loaded successfully."
    )

    print()

    print(
        "Execution methods:"
    )

    print(
        "  runner.step()"
    )

    print(
        "  runner.run()"
    )

    print(
        "  runner.run(max_steps=100)"
    )

    print(
        "  runner.pause()"
    )

    print(
        "  runner.resume()"
    )

    print(
        "  runner.stop()"
    )
