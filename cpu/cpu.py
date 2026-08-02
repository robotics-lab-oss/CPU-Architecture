"""
cpu.py

MiniCPU 8-bit CPU Architecture
Main CPU Core

CPU:
    - 8-bit data width
    - 8-bit address width
    - 256 bytes address space
    - 16 instructions
    - 1-byte and 2-byte instructions

Execution cycle:

    FETCH
      ↓
    DECODE
      ↓
    EXECUTE
      ↓
    UPDATE PC
      ↓
    FETCH
"""

from __future__ import annotations

from typing import Optional


class CPU:
    """
    Main MiniCPU 8-bit CPU.

    The CPU coordinates:

        Registers
        ALU
        Control Unit
        Instruction Decoder
        Instruction Executor
        Flags
        Memory
        Bus
        Program Counter
        Stack
    """

    # ========================================================
    # CPU CONSTANTS
    # ========================================================

    DATA_WIDTH = 8
    ADDRESS_WIDTH = 8

    MAX_VALUE = 0xFF
    MEMORY_SIZE = 0x100

    RESET_ADDRESS = 0x00

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        memory_size: int = MEMORY_SIZE,
    ):
        """
        Initialize the CPU.

        Args:
            memory_size:
                Total memory size.

        Default:
            256 bytes
        """

        if not isinstance(
            memory_size,
            int,
        ):
            raise TypeError(
                "memory_size must be an integer"
            )

        if memory_size <= 0:
            raise ValueError(
                "memory_size must be greater than 0"
            )

        if memory_size > self.MEMORY_SIZE:
            raise ValueError(
                "MiniCPU uses an 8-bit address space. "
                "Maximum memory size is 256 bytes."
            )

        self.memory_size = memory_size

        # ----------------------------------------------------
        # CPU STATE
        # ----------------------------------------------------

        self.running = False

        self.halted = False

        self.cycles = 0

        self.last_opcode: Optional[int] = None

        self.last_instruction: Optional[str] = None

        # ----------------------------------------------------
        # COMPONENTS
        # ----------------------------------------------------

        self._create_components()

    # ========================================================
    # COMPONENT CREATION
    # ========================================================

    def _create_components(self):
        """
        Create CPU components.

        Imports are intentionally local so that the CPU
        package can be developed module by module.
        """

        from .registers import Registers
        from .alu import ALU
        from .control_unit import ControlUnit
        from .instruction_decoder import (
            InstructionDecoder,
        )
        from .instruction_executor import (
            InstructionExecutor,
        )
        from .flags import Flags
        from .memory import Memory
        from .bus import Bus
        from .program_counter import (
            ProgramCounter,
        )
        from .stack import Stack

        # ----------------------------------------------------
        # REGISTERS
        # ----------------------------------------------------

        self.registers = Registers()

        # ----------------------------------------------------
        # FLAGS
        # ----------------------------------------------------

        self.flags = Flags()

        # ----------------------------------------------------
        # ALU
        # ----------------------------------------------------

        self.alu = ALU()

        # ----------------------------------------------------
        # MEMORY
        # ----------------------------------------------------

        self.memory = Memory(
            self.memory_size
        )

        # ----------------------------------------------------
        # BUS
        # ----------------------------------------------------

        self.bus = Bus(
            self.memory
        )

        # ----------------------------------------------------
        # PROGRAM COUNTER
        # ----------------------------------------------------

        self.program_counter = (
            ProgramCounter(
                self.RESET_ADDRESS
            )
        )

        # ----------------------------------------------------
        # STACK
        # ----------------------------------------------------

        self.stack = Stack()

        # ----------------------------------------------------
        # CONTROL UNIT
        # ----------------------------------------------------

        self.control_unit = (
            ControlUnit()
        )

        # ----------------------------------------------------
        # INSTRUCTION DECODER
        # ----------------------------------------------------

        self.instruction_decoder = (
            InstructionDecoder()
        )

        # ----------------------------------------------------
        # INSTRUCTION EXECUTOR
        # ----------------------------------------------------

        self.instruction_executor = (
            InstructionExecutor(
                registers=self.registers,
                alu=self.alu,
                flags=self.flags,
                memory=self.memory,
                stack=self.stack,
                program_counter=(
                    self.program_counter
                ),
            )
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Reset CPU to initial state.
        """

        self.running = False

        self.halted = False

        self.cycles = 0

        self.last_opcode = None

        self.last_instruction = None

        # Reset registers
        if hasattr(
            self.registers,
            "reset",
        ):
            self.registers.reset()

        # Reset flags
        if hasattr(
            self.flags,
            "reset",
        ):
            self.flags.reset()

        # Reset program counter
        if hasattr(
            self.program_counter,
            "reset",
        ):
            self.program_counter.reset(
                self.RESET_ADDRESS
            )

        # Reset stack
        if hasattr(
            self.stack,
            "reset",
        ):
            self.stack.reset()

        # Reset memory
        if hasattr(
            self.memory,
            "reset",
        ):
            self.memory.reset()

    # ========================================================
    # LOAD PROGRAM
    # ========================================================

    def load_program(
        self,
        program: bytes,
        start_address: int = RESET_ADDRESS,
    ):
        """
        Load binary program into memory.

        Args:
            program:
                Program machine code.

            start_address:
                Memory address where program
                execution begins.
        """

        if not isinstance(
            program,
            (bytes, bytearray),
        ):
            raise TypeError(
                "program must be bytes "
                "or bytearray"
            )

        self._validate_address(
            start_address
        )

        end_address = (
            start_address
            + len(program)
        )

        if end_address > self.memory_size:
            raise ValueError(
                "Program does not fit in memory."
            )

        # Write program bytes
        for offset, byte in enumerate(
            program
        ):
            address = (
                start_address
                + offset
            )

            self.memory.write(
                address,
                byte,
            )

        # Set PC
        self.program_counter.set(
            start_address
        )

        self.halted = False

        self.running = False

    # ========================================================
    # FETCH
    # ========================================================

    def fetch(self) -> int:
        """
        Fetch opcode from memory.

        Returns:
            8-bit opcode.
        """

        address = (
            self.program_counter.get()
        )

        self._validate_address(
            address
        )

        opcode = self.memory.read(
            address
        )

        self.last_opcode = opcode

        return opcode

    # ========================================================
    # FETCH OPERAND
    # ========================================================

    def fetch_operand(self) -> int:
        """
        Fetch the second byte of a
        2-byte instruction.

        The PC is advanced after reading
        the operand.
        """

        address = (
            self.program_counter.get()
        )

        self._validate_address(
            address
        )

        operand = self.memory.read(
            address
        )

        self.program_counter.increment()

        return operand

    # ========================================================
    # DECODE
    # ========================================================

    def decode(
        self,
        opcode: int,
    ):
        """
        Decode an opcode.

        The actual decoder implementation
        is delegated to instruction_decoder.py.
        """

        if not isinstance(
            opcode,
            int,
        ):
            raise TypeError(
                "opcode must be an integer"
            )

        if not 0 <= opcode <= 0xFF:
            raise ValueError(
                "opcode must be in 8-bit range"
            )

        return (
            self.instruction_decoder.decode(
                opcode
            )
        )

    # ========================================================
    # EXECUTE ONE INSTRUCTION
    # ========================================================

    def step(self):
        """
        Execute exactly one CPU instruction.

        Cycle:

            FETCH
              ↓
            DECODE
              ↓
            OPERAND FETCH
              ↓
            EXECUTE
        """

        if self.halted:
            return None

        # ----------------------------------------------------
        # FETCH
        # ----------------------------------------------------

        opcode = self.fetch()

        # Advance past opcode
        self.program_counter.increment()

        # ----------------------------------------------------
        # DECODE
        # ----------------------------------------------------

        decoded = self.decode(
            opcode
        )

        # ----------------------------------------------------
        # DETERMINE OPERAND
        # ----------------------------------------------------

        operand = None

        instruction_size = getattr(
            decoded,
            "size",
            None,
        )

        if instruction_size == 2:

            operand = (
                self.fetch_operand()
            )

        # ----------------------------------------------------
        # EXECUTE
        # ----------------------------------------------------

        result = (
            self.instruction_executor.execute(
                decoded,
                operand,
            )
        )

        # ----------------------------------------------------
        # UPDATE STATE
        # ----------------------------------------------------

        self.cycles += 1

        self.last_instruction = getattr(
            decoded,
            "name",
            None,
        )

        # ----------------------------------------------------
        # HALT DETECTION
        # ----------------------------------------------------

        if getattr(
            self.control_unit,
            "halted",
            False,
        ):
            self.halted = True

        return result

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
        max_cycles: Optional[int] = None,
    ):
        """
        Run CPU until HALT.

        Args:
            max_cycles:
                Optional safety limit.

        Returns:
            Number of executed cycles.
        """

        self.running = True

        executed = 0

        while (
            self.running
            and not self.halted
        ):

            if (
                max_cycles is not None
                and executed >= max_cycles
            ):
                break

            self.step()

            executed += 1

        self.running = False

        return executed

    # ========================================================
    # HALT
    # ========================================================

    def halt(self):
        """
        Stop CPU execution.
        """

        self.halted = True

        self.running = False

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    def _validate_address(
        self,
        address: int,
    ):
        """
        Validate 8-bit memory address.
        """

        if not isinstance(
            address,
            int,
        ):
            raise TypeError(
                "Address must be an integer"
            )

        if not (
            0 <= address < self.memory_size
        ):
            raise ValueError(
                f"Invalid memory address: "
                f"0x{address:02X}"
            )

    # ========================================================
    # CPU STATE
    # ========================================================

    def get_state(self) -> dict:
        """
        Return current CPU state.
        """

        return {
            "running": self.running,
            "halted": self.halted,
            "cycles": self.cycles,
            "last_opcode": (
                self.last_opcode
            ),
            "last_instruction": (
                self.last_instruction
            ),
            "program_counter": (
                self.program_counter.get()
            ),
        }

    # ========================================================
    # DEBUG
    # ========================================================

    def dump_state(self):
        """
        Print CPU state.
        """

        state = self.get_state()

        print(
            "========== CPU STATE =========="
        )

        print(
            f"Running          : "
            f"{state['running']}"
        )

        print(
            f"Halted           : "
            f"{state['halted']}"
        )

        print(
            f"Cycles           : "
            f"{state['cycles']}"
        )

        print(
            f"Last Opcode      : "
            f"{state['last_opcode']}"
        )

        print(
            f"Last Instruction : "
            f"{state['last_instruction']}"
        )

        print(
            f"Program Counter  : "
            f"0x"
            f"{state['program_counter']:02X}"
        )

        print(
            "==============================="
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "CPU",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit CPU"
    )

    print(
        "Data Width    : 8-bit"
    )

    print(
        "Address Width : 8-bit"
    )

    print(
        "Memory        : 256 bytes"
    )

    print(
        "Instructions  : 16"
    )
