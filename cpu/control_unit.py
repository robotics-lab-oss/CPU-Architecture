"""
control_unit.py

MiniCPU 8-bit CPU Architecture
Control Unit

Responsibilities:
    - CPU fetch cycle coordination
    - Instruction fetch
    - Opcode fetch
    - Operand fetch
    - Program Counter management
    - Halt control
    - CPU cycle counting
    - Reset control

Instruction format:

    1-byte instruction:
        [ OPCODE ]

    2-byte instruction:
        [ OPCODE ][ OPERAND ]

Architecture:
    - 8-bit opcode
    - 8-bit operand
    - 8-bit address space
    - 256 bytes memory
"""

from __future__ import annotations

from opcode import (
    get_instruction_size,
    requires_operand,
)


class ControlUnit:
    """
    MiniCPU Control Unit.

    The Control Unit coordinates the CPU's
    instruction fetch process.

    Main cycle:

        FETCH
          ↓
        DECODE
          ↓
        EXECUTE
          ↓
        FETCH

    The actual instruction execution is handled
    by instruction_executor.py.
    """

    # ========================================================
    # CPU STATES
    # ========================================================

    RESET = "RESET"

    FETCH = "FETCH"

    DECODE = "DECODE"

    EXECUTE = "EXECUTE"

    HALT = "HALT"

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        memory,
        program_counter,
        bus,
    ):
        """
        Initialize Control Unit.

        Args:
            memory:
                CPU Memory instance.

            program_counter:
                ProgramCounter instance.

            bus:
                CPU Bus instance.
        """

        if memory is None:
            raise ValueError(
                "ControlUnit requires memory."
            )

        if program_counter is None:
            raise ValueError(
                "ControlUnit requires "
                "program_counter."
            )

        if bus is None:
            raise ValueError(
                "ControlUnit requires bus."
            )

        self.memory = memory

        self.program_counter = (
            program_counter
        )

        self.bus = bus

        # Current CPU state
        self.state = self.RESET

        # Current opcode
        self.current_opcode = None

        # Current operand
        self.current_operand = None

        # Current instruction address
        self.current_instruction_address = 0x00

        # Current instruction size
        self.current_instruction_size = 0

        # CPU halted state
        self.halted = False

        # Number of executed CPU cycles
        self.cycles = 0

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset Control Unit state.
        """

        self.state = self.RESET

        self.current_opcode = None

        self.current_operand = None

        self.current_instruction_address = 0x00

        self.current_instruction_size = 0

        self.halted = False

        self.cycles = 0

    # ========================================================
    # FETCH OPCODE
    # ========================================================

    def fetch_opcode(
        self,
    ) -> int:
        """
        Fetch one opcode byte from memory.

        Steps:

            1. Read PC
            2. Read memory at PC
            3. Store opcode
            4. Increment PC
        """

        if self.halted:
            raise RuntimeError(
                "CPU is halted."
            )

        self.state = self.FETCH

        address = (
            self.program_counter.get()
        )

        self.current_instruction_address = (
            address
        )

        opcode = self.bus.read(
            address
        )

        self.current_opcode = opcode

        self.program_counter.increment()

        return opcode

    # ========================================================
    # FETCH OPERAND
    # ========================================================

    def fetch_operand(
        self,
    ) -> int:
        """
        Fetch one operand byte from memory.

        The operand is read from the address
        currently pointed to by PC.

        PC is automatically incremented.
        """

        if self.halted:
            raise RuntimeError(
                "CPU is halted."
            )

        address = (
            self.program_counter.get()
        )

        operand = self.bus.read(
            address
        )

        self.current_operand = operand

        self.program_counter.increment()

        return operand

    # ========================================================
    # FETCH INSTRUCTION
    # ========================================================

    def fetch_instruction(
        self,
    ) -> dict:
        """
        Fetch a complete instruction.

        Returns:

            {
                "address": 0x00,
                "opcode": 0x10,
                "operand": 0x42,
                "size": 2
            }

        For a 1-byte instruction:

            operand = None
            size = 1
        """

        if self.halted:
            raise RuntimeError(
                "CPU is halted."
            )

        self.state = self.FETCH

        self.current_operand = None

        opcode = self.fetch_opcode()

        self.state = self.DECODE

        try:

            if requires_operand_by_opcode(
                opcode
            ):

                operand = (
                    self.fetch_operand()
                )

                size = 2

            else:

                operand = None

                size = 1

        except Exception:

            self.current_operand = None

            raise

        self.current_instruction_size = (
            size
        )

        return {
            "address": (
                self.current_instruction_address
            ),
            "opcode": opcode,
            "operand": operand,
            "size": size,
        }

    # ========================================================
    # DECODE
    # ========================================================

    def decode(
        self,
        instruction,
    ) -> dict:
        """
        Prepare fetched instruction
        for execution.

        This method does not execute
        the instruction.

        The actual decoding logic belongs
        to instruction_decoder.py.
        """

        self.state = self.DECODE

        if not isinstance(
            instruction,
            dict,
        ):
            raise TypeError(
                "Instruction must be a dictionary."
            )

        if "opcode" not in instruction:
            raise ValueError(
                "Instruction is missing opcode."
            )

        opcode = instruction[
            "opcode"
        ]

        operand = instruction.get(
            "operand"
        )

        size = instruction.get(
            "size"
        )

        if size is None:

            size = (
                2
                if operand is not None
                else 1
            )

        self.current_opcode = opcode

        self.current_operand = operand

        self.current_instruction_size = (
            size
        )

        return {
            "opcode": opcode,
            "operand": operand,
            "size": size,
        }

    # ========================================================
    # EXECUTE STATE
    # ========================================================

    def begin_execute(
        self,
    ) -> None:
        """
        Set Control Unit state to EXECUTE.
        """

        if self.halted:
            raise RuntimeError(
                "CPU is halted."
            )

        self.state = self.EXECUTE

    # ========================================================
    # COMPLETE CYCLE
    # ========================================================

    def complete_cycle(
        self,
    ) -> None:
        """
        Complete one CPU instruction cycle.

        Increments cycle counter and
        returns CPU to FETCH state.
        """

        if self.halted:
            return

        self.cycles += 1

        self.state = self.FETCH

    # ========================================================
    # HALT
    # ========================================================

    def halt(
        self,
    ) -> None:
        """
        Halt CPU execution.
        """

        self.halted = True

        self.state = self.HALT

    # ========================================================
    # RESUME
    # ========================================================

    def resume(
        self,
    ) -> None:
        """
        Resume CPU execution.
        """

        self.halted = False

        self.state = self.FETCH

    # ========================================================
    # IS HALTED
    # ========================================================

    def is_halted(
        self,
    ) -> bool:
        """
        Return True if CPU is halted.
        """

        return self.halted

    # ========================================================
    # IS RUNNING
    # ========================================================

    def is_running(
        self,
    ) -> bool:
        """
        Return True if CPU is running.
        """

        return not self.halted

    # ========================================================
    # GET STATE
    # ========================================================

    def get_state(
        self,
    ) -> str:
        """
        Return current Control Unit state.
        """

        return self.state

    # ========================================================
    # GET CURRENT OPCODE
    # ========================================================

    def get_current_opcode(
        self,
    ) -> int | None:
        """
        Return currently fetched opcode.
        """

        return self.current_opcode

    # ========================================================
    # GET CURRENT OPERAND
    # ========================================================

    def get_current_operand(
        self,
    ) -> int | None:
        """
        Return currently fetched operand.
        """

        return self.current_operand

    # ========================================================
    # GET CURRENT INSTRUCTION ADDRESS
    # ========================================================

    def get_current_instruction_address(
        self,
    ) -> int:
        """
        Return address where current
        instruction started.
        """

        return (
            self.current_instruction_address
        )

    # ========================================================
    # GET INSTRUCTION SIZE
    # ========================================================

    def get_current_instruction_size(
        self,
    ) -> int:
        """
        Return size of current instruction.
        """

        return (
            self.current_instruction_size
        )

    # ========================================================
    # GET CYCLE COUNT
    # ========================================================

    def get_cycles(
        self,
    ) -> int:
        """
        Return executed cycle count.
        """

        return self.cycles

    # ========================================================
    # RUN ONE FETCH CYCLE
    # ========================================================

    def step_fetch(
        self,
    ) -> dict:
        """
        Perform one instruction fetch.

        This method only fetches the instruction.

        Execution is handled by
        instruction_executor.py.
        """

        instruction = (
            self.fetch_instruction()
        )

        self.begin_execute()

        return instruction

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> dict:
        """
        Return Control Unit state.
        """

        return {
            "state": self.state,

            "current_opcode": (
                self.current_opcode
            ),

            "current_operand": (
                self.current_operand
            ),

            "current_instruction_address": (
                self.current_instruction_address
            ),

            "current_instruction_size": (
                self.current_instruction_size
            ),

            "halted": self.halted,

            "cycles": self.cycles,
        }

    # ========================================================
    # LOAD SNAPSHOT
    # ========================================================

    def load_snapshot(
        self,
        state: dict,
    ) -> None:
        """
        Restore Control Unit state.
        """

        if not isinstance(
            state,
            dict,
        ):
            raise TypeError(
                "Control Unit state must "
                "be a dictionary."
            )

        self.state = state.get(
            "state",
            self.RESET,
        )

        self.current_opcode = (
            state.get(
                "current_opcode"
            )
        )

        self.current_operand = (
            state.get(
                "current_operand"
            )
        )

        self.current_instruction_address = (
            state.get(
                "current_instruction_address",
                0x00,
            )
        )

        self.current_instruction_size = (
            state.get(
                "current_instruction_size",
                0,
            )
        )

        self.halted = bool(
            state.get(
                "halted",
                False,
            )
        )

        self.cycles = int(
            state.get(
                "cycles",
                0,
            )
        )

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print Control Unit state.
        """

        print(
            "========= CONTROL UNIT ========="
        )

        print(
            f"State        : "
            f"{self.state}"
        )

        print(
            f"Halted       : "
            f"{self.halted}"
        )

        if self.current_opcode is None:

            print(
                "Opcode       : None"
            )

        else:

            print(
                f"Opcode       : "
                f"0x{self.current_opcode:02X}"
            )

        if self.current_operand is None:

            print(
                "Operand      : None"
            )

        else:

            print(
                f"Operand      : "
                f"0x{self.current_operand:02X}"
            )

        print(
            f"Instruction  : "
            f"0x{self.current_instruction_address:02X}"
        )

        print(
            f"Size         : "
            f"{self.current_instruction_size}"
        )

        print(
            f"Cycles       : "
            f"{self.cycles}"
        )

        print(
            "================================"
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable Control Unit state.
        """

        return (
            f"ControlUnit("
            f"state={self.state!r}, "
            f"halted={self.halted}, "
            f"cycles={self.cycles}"
            f")"
        )


# ============================================================
# OPCODE SIZE HELPER
# ============================================================

def requires_operand_by_opcode(
    opcode: int,
) -> bool:
    """
    Determine whether an opcode represents
    an operand instruction.

    IMPORTANT:

    The current MiniCPU opcode.py defines
    operand instructions by instruction name.

    Therefore, the Control Unit should normally
    receive decoded instruction metadata from
    instruction_decoder.py.

    This fallback implementation uses the
    architecture's opcode high nibble.

    0x10 - 0x90:
        Operand instructions

    0xA0 - 0xF0:
        1-byte instructions

    0x00:
        NOP
    """

    if not isinstance(
        opcode,
        int,
    ):
        raise TypeError(
            "Opcode must be an integer."
        )

    if not 0 <= opcode <= 0xFF:
        raise ValueError(
            "Opcode must be 8-bit."
        )

    # NOP
    if opcode == 0x00:
        return False

    # Operand instruction range
    if 0x10 <= opcode <= 0x90:
        return True

    # JZ = 0x90
    if opcode == 0x90:
        return True

    # 1-byte instruction range
    if opcode in {
        0xA0,  # OUT
        0xB0,  # IN
        0xC0,  # INC
        0xD0,  # DEC
        0xF0,  # HALT
    }:
        return False

    # CMP = 0xE0
    if opcode == 0xE0:
        return True

    raise ValueError(
        f"Unknown opcode: "
        f"0x{opcode:02X}"
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "ControlUnit",
    "requires_operand_by_opcode",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    from .memory import Memory
    from .program_counter import ProgramCounter
    from .bus import Bus

    memory = Memory()

    pc = ProgramCounter()

    bus = Bus(
        memory
    )

    control_unit = ControlUnit(
        memory,
        pc,
        bus,
    )

    print(
        "MiniCPU 8-bit Control Unit"
    )

    print()

    # Example:
    #
    # LOAD 0x42
    #
    # Opcode = 0x10
    # Operand = 0x42
    #
    memory.load(
        bytes(
            [
                0x10,
                0x42,
                0xF0,
            ]
        )
    )

    instruction = (
        control_unit.step_fetch()
    )

    print(
        "Fetched Instruction:"
    )

    print(
        instruction
    )

    print()

    control_unit.dump()

    print()

    print(
        f"Next PC: "
        f"0x{pc.get():02X}"
    )
