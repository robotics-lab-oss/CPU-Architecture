"""
instruction_executor.py

MiniCPU 8-bit CPU Architecture
Instruction Executor

Responsibilities:
    - Execute decoded instructions
    - Register operations
    - ALU operations
    - Memory operations
    - Branch operations
    - Input / Output
    - Compare operations
    - Halt control

Instruction Set:

    0x00  NOP
    0x10  LOAD
    0x20  STORE
    0x30  ADD
    0x40  SUB
    0x50  AND
    0x60  OR
    0x70  XOR
    0x80  JMP
    0x90  JZ
    0xA0  OUT
    0xB0  IN
    0xC0  INC
    0xD0  DEC
    0xE0  CMP
    0xF0  HALT

Instruction format:

    1-byte:
        [ OPCODE ]

    2-byte:
        [ OPCODE ][ OPERAND ]

Architecture:
    - 8-bit data
    - 8-bit address
    - 16 instructions
    - 256-byte address space
"""

from __future__ import annotations

from opcode import (
    OPCODES,
)

from .instruction_decoder import (
    InstructionDecoder,
)


class InstructionExecutor:
    """
    Execute decoded MiniCPU instructions.

    Expected CPU components:

        registers
        alu
        flags
        memory
        program_counter
        stack
        bus
        control_unit

    The executor is designed to work with the
    previously created CPU modules.
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    MIN_BYTE = 0x00
    MAX_BYTE = 0xFF

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        registers,
        alu,
        flags,
        memory,
        program_counter,
        bus,
        control_unit,
        stack=None,
        input_device=None,
        output_device=None,
    ):
        """
        Initialize Instruction Executor.

        Args:
            registers:
                CPU register file.

            alu:
                Arithmetic Logic Unit.

            flags:
                CPU flags.

            memory:
                CPU memory.

            program_counter:
                Program Counter.

            bus:
                CPU bus.

            control_unit:
                CPU Control Unit.

            stack:
                Optional stack.

            input_device:
                Optional input callback.

            output_device:
                Optional output callback.
        """

        self.registers = registers

        self.alu = alu

        self.flags = flags

        self.memory = memory

        self.program_counter = (
            program_counter
        )

        self.bus = bus

        self.control_unit = (
            control_unit
        )

        self.stack = stack

        self.input_device = (
            input_device
        )

        self.output_device = (
            output_device
        )

        self.decoder = (
            InstructionDecoder()
        )

        self.last_result = 0x00

        self.last_output = None

        self.last_input = None

        self.executed_instructions = 0

    # ========================================================
    # BYTE VALIDATION
    # ========================================================

    @staticmethod
    def validate_byte(
        value: int,
        name: str = "Value",
    ) -> int:
        """
        Validate an 8-bit value.
        """

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if not (
            0x00
            <= value
            <= 0xFF
        ):
            raise ValueError(
                f"{name} must be in "
                f"8-bit range."
            )

        return value

    # ========================================================
    # REGISTER HELPERS
    # ========================================================

    def _get_accumulator(
        self,
    ) -> int:
        """
        Read accumulator register.

        Supported register APIs:

            get_accumulator()
            get("A")
            A attribute
        """

        if hasattr(
            self.registers,
            "get_accumulator",
        ):
            return self.registers.get_accumulator()

        if hasattr(
            self.registers,
            "get",
        ):
            try:
                return self.registers.get(
                    "A"
                )
            except (
                KeyError,
                ValueError,
            ):
                pass

        if hasattr(
            self.registers,
            "A",
        ):
            return self.registers.A

        if hasattr(
            self.registers,
            "accumulator",
        ):
            return self.registers.accumulator

        raise AttributeError(
            "Registers does not provide "
            "an accumulator."
        )

    # --------------------------------------------------------

    def _set_accumulator(
        self,
        value: int,
    ) -> None:
        """
        Write accumulator register.
        """

        value = self.validate_byte(
            value,
            "Accumulator",
        )

        if hasattr(
            self.registers,
            "set_accumulator",
        ):
            self.registers.set_accumulator(
                value
            )
            return

        if hasattr(
            self.registers,
            "set",
        ):
            try:
                self.registers.set(
                    "A",
                    value,
                )
                return
            except (
                KeyError,
                ValueError,
            ):
                pass

        if hasattr(
            self.registers,
            "A",
        ):
            self.registers.A = value
            return

        if hasattr(
            self.registers,
            "accumulator",
        ):
            self.registers.accumulator = value
            return

        raise AttributeError(
            "Registers does not provide "
            "an accumulator."
        )

    # ========================================================
    # MEMORY HELPERS
    # ========================================================

    def _read_memory(
        self,
        address: int,
    ) -> int:
        """
        Read one byte from memory.
        """

        address = self.validate_byte(
            address,
            "Memory address",
        )

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

    # --------------------------------------------------------

    def _write_memory(
        self,
        address: int,
        value: int,
    ) -> None:
        """
        Write one byte to memory.
        """

        address = self.validate_byte(
            address,
            "Memory address",
        )

        value = self.validate_byte(
            value
        )

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
    # PROGRAM COUNTER HELPERS
    # ========================================================

    def _get_pc(
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
            "a readable value."
        )

    # --------------------------------------------------------

    def _set_pc(
        self,
        address: int,
    ) -> None:
        """
        Set Program Counter.
        """

        address = self.validate_byte(
            address,
            "Program Counter",
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
            self.program_counter.value = address
            return

        if hasattr(
            self.program_counter,
            "pc",
        ):
            self.program_counter.pc = address
            return

        raise AttributeError(
            "ProgramCounter does not provide "
            "a set/load operation."
        )

    # ========================================================
    # FLAG HELPERS
    # ========================================================

    def _set_zero_flag(
        self,
        value: int,
    ) -> None:
        """
        Update Zero flag.
        """

        value = self.validate_byte(
            value
        )

        if hasattr(
            self.flags,
            "update",
        ):
            try:
                self.flags.update(
                    value
                )
                return
            except TypeError:
                pass

        if hasattr(
            self.flags,
            "set_zero",
        ):
            self.flags.set_zero(
                value == 0
            )
            return

        if hasattr(
            self.flags,
            "zero",
        ):
            self.flags.zero = (
                value == 0
            )

    # --------------------------------------------------------

    def _set_carry_flag(
        self,
        value: bool,
    ) -> None:
        """
        Update Carry flag.
        """

        if hasattr(
            self.flags,
            "set_carry",
        ):
            self.flags.set_carry(
                bool(value)
            )
            return

        if hasattr(
            self.flags,
            "carry",
        ):
            self.flags.carry = bool(
                value
            )

    # --------------------------------------------------------

    def _get_zero_flag(
        self,
    ) -> bool:
        """
        Return Zero flag.
        """

        if hasattr(
            self.flags,
            "get_zero",
        ):
            return bool(
                self.flags.get_zero()
            )

        if hasattr(
            self.flags,
            "zero",
        ):
            return bool(
                self.flags.zero
            )

        if hasattr(
            self.flags,
            "Z",
        ):
            return bool(
                self.flags.Z
            )

        return False

    # ========================================================
    # ALU HELPERS
    # ========================================================

    def _alu_add(
        self,
        left: int,
        right: int,
    ) -> int:
        """
        Perform 8-bit addition.
        """

        if hasattr(
            self.alu,
            "add",
        ):
            result = self.alu.add(
                left,
                right,
            )

            if isinstance(
                result,
                tuple,
            ):
                return result[0]

            return result

        return (
            left + right
        ) & 0xFF

    # --------------------------------------------------------

    def _alu_sub(
        self,
        left: int,
        right: int,
    ) -> int:
        """
        Perform 8-bit subtraction.
        """

        if hasattr(
            self.alu,
            "subtract",
        ):
            result = self.alu.subtract(
                left,
                right,
            )

            if isinstance(
                result,
                tuple,
            ):
                return result[0]

            return result

        if hasattr(
            self.alu,
            "sub",
        ):
            result = self.alu.sub(
                left,
                right,
            )

            if isinstance(
                result,
                tuple,
            ):
                return result[0]

            return result

        return (
            left - right
        ) & 0xFF

    # ========================================================
    # EXECUTE
    # ========================================================

    def execute(
        self,
        instruction: dict,
    ) -> int | None:
        """
        Execute one decoded instruction.

        Returns:
            Instruction result where applicable.
        """

        if not isinstance(
            instruction,
            dict,
        ):
            raise TypeError(
                "Instruction must be "
                "a dictionary."
            )

        if not self.decoder.validate_instruction(
            instruction
        ):
            raise ValueError(
                "Invalid decoded instruction."
            )

        name = instruction[
            "name"
        ]

        operand = instruction[
            "operand"
        ]

        self.control_unit.begin_execute()

        result = (
            self._dispatch(
                name,
                operand,
            )
        )

        self.last_result = (
            0x00
            if result is None
            else result
        )

        self.executed_instructions += 1

        if name != "HALT":

            self.control_unit.complete_cycle()

        return result

    # ========================================================
    # DISPATCH
    # ========================================================

    def _dispatch(
        self,
        name: str,
        operand: int | None,
    ) -> int | None:
        """
        Dispatch instruction to its
        execution method.
        """

        handlers = {
            "NOP": self.execute_nop,
            "LOAD": self.execute_load,
            "STORE": self.execute_store,
            "ADD": self.execute_add,
            "SUB": self.execute_sub,
            "AND": self.execute_and,
            "OR": self.execute_or,
            "XOR": self.execute_xor,
            "JMP": self.execute_jmp,
            "JZ": self.execute_jz,
            "OUT": self.execute_out,
            "IN": self.execute_in,
            "INC": self.execute_inc,
            "DEC": self.execute_dec,
            "CMP": self.execute_cmp,
            "HALT": self.execute_halt,
        }

        if name not in handlers:
            raise ValueError(
                f"Unsupported instruction: "
                f"{name}"
            )

        return handlers[name](
            operand
        )

    # ========================================================
    # NOP
    # ========================================================

    def execute_nop(
        self,
        operand=None,
    ) -> None:
        """
        NOP

        No operation.
        """

        return None

    # ========================================================
    # LOAD
    # ========================================================

    def execute_load(
        self,
        operand: int,
    ) -> int:
        """
        LOAD address

        Load value from memory address
        into accumulator.

        Example:

            LOAD 0x20

        A = MEM[0x20]
        """

        operand = self.validate_byte(
            operand,
            "LOAD address",
        )

        value = self._read_memory(
            operand
        )

        self._set_accumulator(
            value
        )

        self._set_zero_flag(
            value
        )

        return value

    # ========================================================
    # STORE
    # ========================================================

    def execute_store(
        self,
        operand: int,
    ) -> None:
        """
        STORE address

        Store accumulator into memory.

        Example:

            STORE 0x20

        MEM[0x20] = A
        """

        operand = self.validate_byte(
            operand,
            "STORE address",
        )

        value = self._get_accumulator()

        self._write_memory(
            operand,
            value,
        )

        return None

    # ========================================================
    # ADD
    # ========================================================

    def execute_add(
        self,
        operand: int,
    ) -> int:
        """
        ADD address

        A = A + MEM[address]
        """

        operand = self.validate_byte(
            operand,
            "ADD address",
        )

        value = self._read_memory(
            operand
        )

        accumulator = (
            self._get_accumulator()
        )

        result = self._alu_add(
            accumulator,
            value,
        )

        result &= 0xFF

        self._set_accumulator(
            result
        )

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # SUB
    # ========================================================

    def execute_sub(
        self,
        operand: int,
    ) -> int:
        """
        SUB address

        A = A - MEM[address]
        """

        operand = self.validate_byte(
            operand,
            "SUB address",
        )

        value = self._read_memory(
            operand
        )

        accumulator = (
            self._get_accumulator()
        )

        result = self._alu_sub(
            accumulator,
            value,
        )

        result &= 0xFF

        self._set_accumulator(
            result
        )

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # AND
    # ========================================================

    def execute_and(
        self,
        operand: int,
    ) -> int:
        """
        AND address

        A = A & MEM[address]
        """

        value = self._read_memory(
            self.validate_byte(
                operand
            )
        )

        result = (
            self._get_accumulator()
            & value
        )

        self._set_accumulator(
            result
        )

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # OR
    # ========================================================

    def execute_or(
        self,
        operand: int,
    ) -> int:
        """
        OR address

        A = A | MEM[address]
        """

        value = self._read_memory(
            self.validate_byte(
                operand
            )
        )

        result = (
            self._get_accumulator()
            | value
        )

        self._set_accumulator(
            result
        )

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # XOR
    # ========================================================

    def execute_xor(
        self,
        operand: int,
    ) -> int:
        """
        XOR address

        A = A ^ MEM[address]
        """

        value = self._read_memory(
            self.validate_byte(
                operand
            )
        )

        result = (
            self._get_accumulator()
            ^ value
        )

        self._set_accumulator(
            result
        )

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # JMP
    # ========================================================

    def execute_jmp(
        self,
        operand: int,
    ) -> None:
        """
        JMP address

        PC = address
        """

        operand = self.validate_byte(
            operand,
            "JMP address",
        )

        self._set_pc(
            operand
        )

        return None

    # ========================================================
    # JZ
    # ========================================================

    def execute_jz(
        self,
        operand: int,
    ) -> None:
        """
        JZ address

        Jump if Zero flag is set.
        """

        operand = self.validate_byte(
            operand,
            "JZ address",
        )

        if self._get_zero_flag():

            self._set_pc(
                operand
            )

        return None

    # ========================================================
    # OUT
    # ========================================================

    def execute_out(
        self,
        operand=None,
    ) -> int:
        """
        OUT

        Output accumulator value.

        If an output callback is provided,
        it receives the accumulator value.
        """

        value = self._get_accumulator()

        self.last_output = value

        if callable(
            self.output_device
        ):
            self.output_device(
                value
            )

        else:
            print(
                f"OUT: 0x{value:02X}"
            )

        return value

    # ========================================================
    # IN
    # ========================================================

    def execute_in(
        self,
        operand=None,
    ) -> int:
        """
        IN

        Read one byte from input device
        into accumulator.

        If no input callback is provided,
        input() is used.
        """

        if callable(
            self.input_device
        ):

            value = (
                self.input_device()
            )

        else:

            raw = input(
                "IN> "
            )

            value = int(
                raw,
                0,
            )

        value = self.validate_byte(
            value,
            "Input value",
        )

        self.last_input = value

        self._set_accumulator(
            value
        )

        self._set_zero_flag(
            value
        )

        return value

    # ========================================================
    # INC
    # ========================================================

    def execute_inc(
        self,
        operand=None,
    ) -> int:
        """
        INC

        A = A + 1
        """

        value = (
            self._get_accumulator()
        )

        result = (
            value + 1
        ) & 0xFF

        self._set_accumulator(
            result
        )

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # DEC
    # ========================================================

    def execute_dec(
        self,
        operand=None,
    ) -> int:
        """
        DEC

        A = A - 1
        """

        value = (
            self._get_accumulator()
        )

        result = (
            value - 1
        ) & 0xFF

        self._set_accumulator(
            result
        )

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # CMP
    # ========================================================

    def execute_cmp(
        self,
        operand: int,
    ) -> int:
        """
        CMP address

        Compare accumulator with memory.

        A - MEM[address]

        Only flags are affected.
        Accumulator is unchanged.
        """

        operand = self.validate_byte(
            operand,
            "CMP address",
        )

        value = self._read_memory(
            operand
        )

        accumulator = (
            self._get_accumulator()
        )

        result = self._alu_sub(
            accumulator,
            value,
        )

        result &= 0xFF

        self._set_zero_flag(
            result
        )

        return result

    # ========================================================
    # HALT
    # ========================================================

    def execute_halt(
        self,
        operand=None,
    ) -> None:
        """
        HALT

        Stop CPU execution.
        """

        self.control_unit.halt()

        return None

    # ========================================================
    # EXECUTE RAW BYTES
    # ========================================================

    def execute_bytes(
        self,
        data: bytes | bytearray,
    ) -> int | None:
        """
        Decode and execute one instruction
        from raw machine-code bytes.
        """

        instruction = (
            self.decoder.decode_bytes(
                data
            )
        )

        return self.execute(
            instruction
        )

    # ========================================================
    # EXECUTE OPCODE
    # ========================================================

    def execute_opcode(
        self,
        opcode: int,
        operand: int | None = None,
    ) -> int | None:
        """
        Decode and execute opcode directly.
        """

        instruction = (
            self.decoder.decode(
                opcode,
                operand,
            )
        )

        return self.execute(
            instruction
        )

    # ========================================================
    # GET LAST RESULT
    # ========================================================

    def get_last_result(
        self,
    ) -> int:
        """
        Return result of last operation.
        """

        return self.last_result

    # ========================================================
    # GET EXECUTION COUNT
    # ========================================================

    def get_execution_count(
        self,
    ) -> int:
        """
        Return number of executed instructions.
        """

        return (
            self.executed_instructions
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset executor state.
        """

        self.last_result = 0x00

        self.last_output = None

        self.last_input = None

        self.executed_instructions = 0

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> dict:
        """
        Return executor state.
        """

        return {
            "last_result": (
                self.last_result
            ),
            "last_output": (
                self.last_output
            ),
            "last_input": (
                self.last_input
            ),
            "executed_instructions": (
                self.executed_instructions
            ),
        }

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print executor state.
        """

        print(
            "======= INSTRUCTION EXECUTOR ======="
        )

        print(
            f"Last Result : "
            f"0x{self.last_result:02X}"
        )

        if self.last_output is None:

            print(
                "Last Output : None"
            )

        else:

            print(
                f"Last Output : "
                f"0x{self.last_output:02X}"
            )

        if self.last_input is None:

            print(
                "Last Input  : None"
            )

        else:

            print(
                f"Last Input  : "
                f"0x{self.last_input:02X}"
            )

        print(
            f"Executed    : "
            f"{self.executed_instructions}"
        )

        print(
            "====================================="
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable executor state.
        """

        return (
            f"InstructionExecutor("
            f"executed="
            f"{self.executed_instructions}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "InstructionExecutor",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit "
        "Instruction Executor"
    )

    print()

    print(
        "Instruction Executor module "
        "loaded successfully."
    )

    print()

    print(
        "Supported Instructions:"
    )

    for name, opcode in OPCODES.items():

        print(
            f"  {name:<5} "
            f"0x{opcode:02X}"
        )
