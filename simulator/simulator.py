"""
simulator.py

MiniCPU 8-bit CPU Architecture
Main Simulator

Responsibilities:
    - Initialize CPU components
    - Load machine-code programs
    - Reset CPU
    - Run CPU
    - Single-step execution
    - Halt handling
    - CPU state inspection
    - Simulator state management

Architecture:
    - 8-bit data
    - 8-bit address
    - 256-byte memory
    - 16 instructions
"""

from __future__ import annotations

from typing import Optional


class Simulator:
    """
    Main MiniCPU simulator controller.

    The Simulator connects the CPU components:

        Memory
           │
           ▼
         Bus
           │
           ▼
    Control Unit
           │
           ▼
    Instruction Decoder
           │
           ▼
    Instruction Executor

    The simulator provides a high-level interface
    for loading and executing MiniCPU programs.
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    MEMORY_SIZE = 256

    MIN_ADDRESS = 0x00
    MAX_ADDRESS = 0xFF

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        cpu=None,
        memory=None,
        program_counter=None,
        registers=None,
        alu=None,
        flags=None,
        bus=None,
        stack=None,
        control_unit=None,
        instruction_decoder=None,
        instruction_executor=None,
    ):
        """
        Initialize MiniCPU Simulator.

        The simulator can receive an already-created CPU
        or individual CPU components.

        Preferred usage:

            Simulator(cpu=cpu)

        Advanced usage:

            Simulator(
                memory=memory,
                registers=registers,
                ...
            )
        """

        self.cpu = cpu

        self.memory = memory

        self.program_counter = (
            program_counter
        )

        self.registers = registers

        self.alu = alu

        self.flags = flags

        self.bus = bus

        self.stack = stack

        self.control_unit = (
            control_unit
        )

        self.instruction_decoder = (
            instruction_decoder
        )

        self.instruction_executor = (
            instruction_executor
        )

        self.loaded = False

        self.program_start = 0x00

        self.program_size = 0

        self.program = b""

        self.running = False

    # ========================================================
    # CPU ATTACHMENT
    # ========================================================

    def attach_cpu(
        self,
        cpu,
    ) -> None:
        """
        Attach an existing CPU instance.

        The CPU object is expected to expose
        its core components.

        This method intentionally does not assume
        a single CPU implementation, allowing the
        simulator to work with different CPU classes.
        """

        if cpu is None:
            raise ValueError(
                "CPU cannot be None."
            )

        self.cpu = cpu

        # Try to discover CPU components.

        self.memory = getattr(
            cpu,
            "memory",
            self.memory,
        )

        self.program_counter = getattr(
            cpu,
            "program_counter",
            self.program_counter,
        )

        self.registers = getattr(
            cpu,
            "registers",
            self.registers,
        )

        self.alu = getattr(
            cpu,
            "alu",
            self.alu,
        )

        self.flags = getattr(
            cpu,
            "flags",
            self.flags,
        )

        self.bus = getattr(
            cpu,
            "bus",
            self.bus,
        )

        self.stack = getattr(
            cpu,
            "stack",
            self.stack,
        )

        self.control_unit = getattr(
            cpu,
            "control_unit",
            self.control_unit,
        )

        self.instruction_decoder = getattr(
            cpu,
            "instruction_decoder",
            self.instruction_decoder,
        )

        self.instruction_executor = getattr(
            cpu,
            "instruction_executor",
            self.instruction_executor,
        )

    # ========================================================
    # COMPONENT VALIDATION
    # ========================================================

    def validate_components(
        self,
    ) -> None:
        """
        Validate that required simulator
        components are available.

        Raises:
            RuntimeError if a required component
            is missing.
        """

        missing = []

        if self.cpu is None:
            missing.append(
                "cpu"
            )

        if self.memory is None:
            missing.append(
                "memory"
            )

        if self.program_counter is None:
            missing.append(
                "program_counter"
            )

        if self.control_unit is None:
            missing.append(
                "control_unit"
            )

        if self.instruction_executor is None:
            missing.append(
                "instruction_executor"
            )

        if missing:

            raise RuntimeError(
                "Simulator is missing "
                "required components: "
                + ", ".join(
                    missing
                )
            )

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    @staticmethod
    def validate_address(
        address: int,
    ) -> int:
        """
        Validate an 8-bit memory address.
        """

        if not isinstance(
            address,
            int,
        ):
            raise TypeError(
                "Address must be an integer."
            )

        if not (
            0x00
            <= address
            <= 0xFF
        ):
            raise ValueError(
                "Address must be in "
                "8-bit range."
            )

        return address

    # ========================================================
    # LOAD PROGRAM
    # ========================================================

    def load_program(
        self,
        program: bytes | bytearray,
        start_address: int = 0x00,
    ) -> None:
        """
        Load a machine-code program into memory.

        Args:
            program:
                Program bytes.

            start_address:
                Memory address where program starts.

        Example:

            program = bytes([
                0x10,
                0x20,
                0xF0,
            ])

            simulator.load_program(
                program,
                0x00,
            )
        """

        self.validate_components()

        start_address = (
            self.validate_address(
                start_address
            )
        )

        if not isinstance(
            program,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Program must be bytes "
                "or bytearray."
            )

        if len(program) == 0:

            raise ValueError(
                "Program cannot be empty."
            )

        if (
            start_address
            + len(program)
            > self.MEMORY_SIZE
        ):

            raise ValueError(
                "Program does not fit "
                "inside 256-byte memory."
            )

        # Prefer bus block loading.

        if (
            self.bus is not None
            and hasattr(
                self.bus,
                "write_block",
            )
        ):

            self.bus.write_block(
                start_address,
                bytes(program),
            )

        elif hasattr(
            self.memory,
            "write_block",
        ):

            self.memory.write_block(
                start_address,
                bytes(program),
            )

        else:

            for offset, value in enumerate(
                program
            ):

                self.memory.write(
                    start_address
                    + offset,
                    value,
                )

        self.program = bytes(
            program
        )

        self.program_start = (
            start_address
        )

        self.program_size = len(
            program
        )

        self.loaded = True

        self.running = False

        # Set PC to program start.

        self.set_program_counter(
            start_address
        )

    # ========================================================
    # LOAD HEX
    # ========================================================

    def load_hex(
        self,
        hex_string: str,
        start_address: int = 0x00,
    ) -> None:
        """
        Load hexadecimal machine code.

        Example:

            "10 20 F0"

        or:

            "1020F0"
        """

        if not isinstance(
            hex_string,
            str,
        ):
            raise TypeError(
                "hex_string must be a string."
            )

        cleaned = (
            hex_string
            .replace(
                " ",
                "",
            )
            .replace(
                "\n",
                "",
            )
            .replace(
                "\t",
                "",
            )
            .replace(
                "_",
                "",
            )
        )

        if len(cleaned) % 2 != 0:

            raise ValueError(
                "Hex string must contain "
                "an even number of digits."
            )

        try:

            program = bytes.fromhex(
                cleaned
            )

        except ValueError as exc:

            raise ValueError(
                "Invalid hexadecimal program."
            ) from exc

        self.load_program(
            program,
            start_address,
        )

    # ========================================================
    # SET PROGRAM COUNTER
    # ========================================================

    def set_program_counter(
        self,
        address: int,
    ) -> None:
        """
        Set Program Counter.
        """

        address = (
            self.validate_address(
                address
            )
        )

        if hasattr(
            self.program_counter,
            "set",
        ):

            self.program_counter.set(
                address
            )

            return

        if hasattr(
            self.program_counter,
            "load",
        ):

            self.program_counter.load(
                address
            )

            return

        if hasattr(
            self.program_counter,
            "value",
        ):

            self.program_counter.value = (
                address
            )

            return

        if hasattr(
            self.program_counter,
            "pc",
        ):

            self.program_counter.pc = (
                address
            )

            return

        raise AttributeError(
            "ProgramCounter does not provide "
            "set(), load(), value or pc."
        )

    # ========================================================
    # GET PROGRAM COUNTER
    # ========================================================

    def get_program_counter(
        self,
    ) -> int:
        """
        Return current Program Counter.
        """

        if hasattr(
            self.program_counter,
            "get",
        ):

            return self.program_counter.get()

        if hasattr(
            self.program_counter,
            "value",
        ):

            return self.program_counter.value

        if hasattr(
            self.program_counter,
            "pc",
        ):

            return self.program_counter.pc

        raise AttributeError(
            "ProgramCounter does not provide "
            "get(), value or pc."
        )

    # ========================================================
    # FETCH
    # ========================================================

    def fetch(
        self,
    ) -> dict:
        """
        Fetch the next instruction.

        Uses the Control Unit when available.
        """

        self.validate_components()

        if hasattr(
            self.control_unit,
            "fetch_instruction",
        ):

            return (
                self.control_unit
                .fetch_instruction()
            )

        if hasattr(
            self.control_unit,
            "step_fetch",
        ):

            return (
                self.control_unit
                .step_fetch()
            )

        raise AttributeError(
            "ControlUnit does not provide "
            "instruction fetch operation."
        )

    # ========================================================
    # STEP
    # ========================================================

    def step(
        self,
    ) -> int | None:
        """
        Execute exactly one instruction.

        Workflow:

            FETCH
              ↓
            DECODE
              ↓
            EXECUTE
        """

        self.validate_components()

        if not self.loaded:

            raise RuntimeError(
                "No program is loaded."
            )

        if self.is_halted():

            self.running = False

            return None

        instruction = self.fetch()

        result = (
            self.instruction_executor
            .execute(
                instruction
            )
        )

        if self.is_halted():

            self.running = False

        return result

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        max_steps: Optional[int] = None,
    ) -> int:
        """
        Run the loaded program.

        Args:
            max_steps:
                Maximum number of instructions
                to execute.

                None means no explicit limit.

        Returns:
            Number of executed instructions.
        """

        self.validate_components()

        if not self.loaded:

            raise RuntimeError(
                "No program is loaded."
            )

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
                "max_steps must be "
                "a non-negative integer "
                "or None."
            )

        self.running = True

        executed = 0

        while self.running:

            if self.is_halted():

                self.running = False

                break

            if (
                max_steps is not None
                and executed
                >= max_steps
            ):

                break

            self.step()

            executed += 1

        return executed

    # ========================================================
    # STOP
    # ========================================================

    def stop(
        self,
    ) -> None:
        """
        Stop simulator execution.

        This does not necessarily halt
        the CPU permanently.
        """

        self.running = False

    # ========================================================
    # HALT
    # ========================================================

    def halt(
        self,
    ) -> None:
        """
        Halt the CPU.
        """

        if self.control_unit is not None:

            if hasattr(
                self.control_unit,
                "halt",
            ):

                self.control_unit.halt()

        self.running = False

    # ========================================================
    # RESUME
    # ========================================================

    def resume(
        self,
    ) -> None:
        """
        Resume a halted CPU.
        """

        if self.control_unit is None:

            raise RuntimeError(
                "ControlUnit is not available."
            )

        if hasattr(
            self.control_unit,
            "resume",
        ):

            self.control_unit.resume()

        self.running = True

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        clear_memory: bool = False,
    ) -> None:
        """
        Reset simulator and CPU state.

        Args:
            clear_memory:
                If True, clear all memory.
        """

        self.running = False

        if self.cpu is not None:

            if hasattr(
                self.cpu,
                "reset",
            ):

                self.cpu.reset()

        if self.control_unit is not None:

            if hasattr(
                self.control_unit,
                "reset",
            ):

                self.control_unit.reset()

        if self.program_counter is not None:

            if hasattr(
                self.program_counter,
                "reset",
            ):

                self.program_counter.reset()

            else:

                self.set_program_counter(
                    self.program_start
                )

        if self.registers is not None:

            if hasattr(
                self.registers,
                "reset",
            ):

                self.registers.reset()

        if self.flags is not None:

            if hasattr(
                self.flags,
                "reset",
            ):

                self.flags.reset()

        if self.stack is not None:

            if hasattr(
                self.stack,
                "reset",
            ):

                self.stack.reset()

        if self.bus is not None:

            if hasattr(
                self.bus,
                "reset",
            ):

                self.bus.reset()

        if self.instruction_executor is not None:

            if hasattr(
                self.instruction_executor,
                "reset",
            ):

                self.instruction_executor.reset()

        if clear_memory:

            if self.memory is not None:

                if hasattr(
                    self.memory,
                    "clear",
                ):

                    self.memory.clear()

                else:

                    for address in range(
                        self.MEMORY_SIZE
                    ):

                        self.memory.write(
                            address,
                            0x00,
                        )

            self.loaded = False

            self.program = b""

            self.program_size = 0

    # ========================================================
    # STATUS
    # ========================================================

    def is_halted(
        self,
    ) -> bool:
        """
        Return True if CPU is halted.
        """

        if self.control_unit is None:

            return False

        if hasattr(
            self.control_unit,
            "is_halted",
        ):

            return (
                self.control_unit
                .is_halted()
            )

        return bool(
            getattr(
                self.control_unit,
                "halted",
                False,
            )
        )

    # ========================================================
    # IS RUNNING
    # ========================================================

    def is_running(
        self,
    ) -> bool:
        """
        Return True if simulator is running.
        """

        return self.running

    # ========================================================
    # PROGRAM STATUS
    # ========================================================

    def get_program_info(
        self,
    ) -> dict:
        """
        Return information about loaded program.
        """

        return {
            "loaded": self.loaded,
            "start_address": (
                self.program_start
            ),
            "size": (
                self.program_size
            ),
            "end_address": (
                (
                    self.program_start
                    + self.program_size
                    - 1
                )
                if self.program_size > 0
                else None
            ),
        }

    # ========================================================
    # CPU STATE
    # ========================================================

    def get_state(
        self,
    ) -> dict:
        """
        Return complete simulator state.

        Components that provide snapshot()
        are automatically included.
        """

        state = {
            "loaded": self.loaded,
            "running": self.running,
            "program_start": (
                self.program_start
            ),
            "program_size": (
                self.program_size
            ),
            "program_counter": (
                self.get_program_counter()
                if self.program_counter
                is not None
                else None
            ),
        }

        components = {
            "registers": self.registers,
            "flags": self.flags,
            "memory": self.memory,
            "stack": self.stack,
            "bus": self.bus,
            "control_unit": (
                self.control_unit
            ),
            "instruction_executor": (
                self.instruction_executor
            ),
        }

        for name, component in (
            components.items()
        ):

            if component is not None:

                if hasattr(
                    component,
                    "snapshot",
                ):

                    state[name] = (
                        component.snapshot()
                    )

        return state

    # ========================================================
    # MEMORY READ
    # ========================================================

    def read_memory(
        self,
        address: int,
    ) -> int:
        """
        Read one byte from memory.
        """

        address = (
            self.validate_address(
                address
            )
        )

        if self.bus is not None:

            if hasattr(
                self.bus,
                "read",
            ):

                return self.bus.read(
                    address
                )

        return self.memory.read(
            address
        )

    # ========================================================
    # MEMORY WRITE
    # ========================================================

    def write_memory(
        self,
        address: int,
        value: int,
    ) -> None:
        """
        Write one byte to memory.
        """

        address = (
            self.validate_address(
                address
            )
        )

        if not isinstance(
            value,
            int,
        ):

            raise TypeError(
                "Memory value must "
                "be an integer."
            )

        if not (
            0x00
            <= value
            <= 0xFF
        ):

            raise ValueError(
                "Memory value must "
                "be 8-bit."
            )

        if self.bus is not None:

            if hasattr(
                self.bus,
                "write",
            ):

                self.bus.write(
                    address,
                    value,
                )

                return

        self.memory.write(
            address,
            value,
        )

    # ========================================================
    # MEMORY DUMP
    # ========================================================

    def memory_dump(
        self,
        start_address: int = 0x00,
        length: int = 16,
    ) -> bytes:
        """
        Return a section of memory.
        """

        start_address = (
            self.validate_address(
                start_address
            )
        )

        if not isinstance(
            length,
            int,
        ):

            raise TypeError(
                "length must be an integer."
            )

        if length < 0:

            raise ValueError(
                "length cannot be negative."
            )

        if (
            start_address
            + length
            > self.MEMORY_SIZE
        ):

            raise ValueError(
                "Memory dump exceeds "
                "address space."
            )

        if hasattr(
            self.memory,
            "read_block",
        ):

            return self.memory.read_block(
                start_address,
                length,
            )

        return bytes(
            self.memory.read(
                start_address + offset
            )
            for offset in range(
                length
            )
        )

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump_state(
        self,
    ) -> None:
        """
        Print simulator state.
        """

        print(
            "========== MINICPU SIMULATOR =========="
        )

        print(
            f"Program Loaded : "
            f"{self.loaded}"
        )

        print(
            f"Running        : "
            f"{self.running}"
        )

        print(
            f"CPU Halted     : "
            f"{self.is_halted()}"
        )

        print(
            f"Program Start  : "
            f"0x{self.program_start:02X}"
        )

        print(
            f"Program Size   : "
            f"{self.program_size}"
        )

        print(
            f"Program Counter: "
            f"0x{self.get_program_counter():02X}"
        )

        print(
            "========================================"
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable simulator state.
        """

        return (
            f"Simulator("
            f"loaded={self.loaded}, "
            f"running={self.running}, "
            f"halted={self.is_halted()}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Simulator",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Simulator"
    )

    print()

    print(
        "Simulator module loaded."
    )

    print(
        "Use Simulator(cpu=cpu) "
        "to attach a CPU instance."
    )
