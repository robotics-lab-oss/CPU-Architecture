"""
instruction_decoder.py

MiniCPU 8-bit CPU Architecture
Instruction Decoder

Responsibilities:
    - Decode 8-bit opcode
    - Identify instruction name
    - Identify instruction size
    - Identify operand requirement
    - Validate operand
    - Create decoded instruction metadata

Instruction format:

    1-byte instruction:
        [ OPCODE ]

    2-byte instruction:
        [ OPCODE ][ OPERAND ]

Architecture:
    - 8-bit opcode
    - 8-bit operand
    - 16 instructions
"""

from __future__ import annotations

from opcode import (
    OPCODES,
    ONE_BYTE_INSTRUCTIONS,
    TWO_BYTE_INSTRUCTIONS,
    INSTRUCTION_SIZES,
    normalize_instruction,
    get_opcode,
    get_instruction_size,
    requires_operand,
)


class InstructionDecoder:
    """
    Decode MiniCPU machine instructions.

    Example:

        LOAD 0x42

    Machine code:

        0x10 0x42

    Decoded result:

        {
            "name": "LOAD",
            "opcode": 0x10,
            "operand": 0x42,
            "size": 2,
            "requires_operand": True
        }
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
        opcode_table=None,
    ):
        """
        Initialize Instruction Decoder.

        Args:
            opcode_table:
                Optional custom opcode table.

        Default:
            Uses OPCODES from opcode.py.
        """

        if opcode_table is None:
            opcode_table = OPCODES

        if not isinstance(
            opcode_table,
            dict,
        ):
            raise TypeError(
                "opcode_table must be a dictionary."
            )

        self.opcode_table = dict(
            opcode_table
        )

        self._reverse_table = {
            opcode: name
            for name, opcode
            in self.opcode_table.items()
        }

    # ========================================================
    # BYTE VALIDATION
    # ========================================================

    @classmethod
    def validate_byte(
        cls,
        value: int,
        name: str = "Byte",
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
            cls.MIN_BYTE
            <= value
            <= cls.MAX_BYTE
        ):
            raise ValueError(
                f"{name} must be between "
                f"0x00 and 0xFF."
            )

        return value

    # ========================================================
    # DECODE OPCODE
    # ========================================================

    def decode_opcode(
        self,
        opcode: int,
    ) -> str:
        """
        Convert numeric opcode to instruction name.

        Example:

            0x10 -> "LOAD"
        """

        opcode = self.validate_byte(
            opcode,
            "Opcode",
        )

        if opcode not in self._reverse_table:
            raise ValueError(
                f"Unknown opcode: "
                f"0x{opcode:02X}"
            )

        return self._reverse_table[
            opcode
        ]

    # ========================================================
    # GET OPCODE
    # ========================================================

    def get_opcode(
        self,
        instruction: str,
    ) -> int:
        """
        Convert instruction name to opcode.

        Example:

            "LOAD" -> 0x10
        """

        instruction = normalize_instruction(
            instruction
        )

        if instruction not in self.opcode_table:
            raise ValueError(
                f"Unknown instruction: "
                f"{instruction}"
            )

        return self.opcode_table[
            instruction
        ]

    # ========================================================
    # GET INSTRUCTION SIZE
    # ========================================================

    def get_size(
        self,
        instruction: str,
    ) -> int:
        """
        Return instruction size.

        Returns:

            1
                Opcode only

            2
                Opcode + operand
        """

        instruction = normalize_instruction(
            instruction
        )

        if instruction not in INSTRUCTION_SIZES:
            raise ValueError(
                f"Unknown instruction: "
                f"{instruction}"
            )

        return INSTRUCTION_SIZES[
            instruction
        ]

    # ========================================================
    # REQUIRES OPERAND
    # ========================================================

    def requires_operand(
        self,
        instruction: str,
    ) -> bool:
        """
        Return True if instruction requires
        a second byte.
        """

        instruction = normalize_instruction(
            instruction
        )

        return (
            instruction
            in TWO_BYTE_INSTRUCTIONS
        )

    # ========================================================
    # DECODE
    # ========================================================

    def decode(
        self,
        opcode: int,
        operand: int | None = None,
    ) -> dict:
        """
        Decode one instruction.

        Example:

            decode(0x10, 0x42)

        Returns:

            {
                "name": "LOAD",
                "opcode": 0x10,
                "operand": 0x42,
                "size": 2,
                "requires_operand": True
            }
        """

        opcode = self.validate_byte(
            opcode,
            "Opcode",
        )

        name = self.decode_opcode(
            opcode
        )

        size = self.get_size(
            name
        )

        needs_operand = (
            self.requires_operand(
                name
            )
        )

        if needs_operand:

            if operand is None:
                raise ValueError(
                    f"Instruction "
                    f"{name} requires "
                    f"an operand."
                )

            operand = self.validate_byte(
                operand,
                "Operand",
            )

        else:

            if operand is not None:
                raise ValueError(
                    f"Instruction "
                    f"{name} does not "
                    f"accept an operand."
                )

        return {
            "name": name,
            "opcode": opcode,
            "operand": operand,
            "size": size,
            "requires_operand": (
                needs_operand
            ),
        }

    # ========================================================
    # DECODE BYTES
    # ========================================================

    def decode_bytes(
        self,
        data: bytes | bytearray,
    ) -> dict:
        """
        Decode an instruction from raw bytes.

        Example:

            bytes([0x10, 0x42])

        Decodes to:

            LOAD 0x42
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Instruction data must be "
                "bytes or bytearray."
            )

        if len(data) == 0:
            raise ValueError(
                "Instruction data cannot be empty."
            )

        opcode = data[0]

        name = self.decode_opcode(
            opcode
        )

        size = self.get_size(
            name
        )

        if len(data) < size:
            raise ValueError(
                f"Incomplete instruction "
                f"{name}. "
                f"Expected {size} byte(s), "
                f"got {len(data)}."
            )

        if size == 1:

            return self.decode(
                opcode
            )

        operand = data[1]

        return self.decode(
            opcode,
            operand,
        )

    # ========================================================
    # DECODE MEMORY
    # ========================================================

    def decode_from_memory(
        self,
        memory,
        address: int,
    ) -> dict:
        """
        Decode one complete instruction
        directly from memory.

        The memory object must provide:

            read(address)
        """

        if memory is None:
            raise ValueError(
                "Memory instance is required."
            )

        if not hasattr(
            memory,
            "read",
        ):
            raise TypeError(
                "Memory must provide "
                "a read() method."
            )

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
                "Address must be 8-bit."
            )

        opcode = memory.read(
            address
        )

        name = self.decode_opcode(
            opcode
        )

        size = self.get_size(
            name
        )

        if size == 1:

            return self.decode(
                opcode
            )

        operand_address = (
            (address + 1)
            & 0xFF
        )

        operand = memory.read(
            operand_address
        )

        return self.decode(
            opcode,
            operand,
        )

    # ========================================================
    # DECODE STREAM
    # ========================================================

    def decode_stream(
        self,
        data: bytes | bytearray,
    ) -> list[dict]:
        """
        Decode a complete machine-code stream.

        Example:

            [
                0x10, 0x42,
                0xC0,
                0xF0
            ]

        Returns:

            LOAD 0x42
            INC
            HALT
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        instructions = []

        offset = 0

        while offset < len(data):

            opcode = data[
                offset
            ]

            name = self.decode_opcode(
                opcode
            )

            size = self.get_size(
                name
            )

            if (
                offset + size
                > len(data)
            ):
                raise ValueError(
                    f"Incomplete instruction "
                    f"at byte offset "
                    f"{offset}."
                )

            if size == 1:

                decoded = self.decode(
                    opcode
                )

            else:

                operand = data[
                    offset + 1
                ]

                decoded = self.decode(
                    opcode,
                    operand,
                )

            decoded[
                "offset"
            ] = offset

            instructions.append(
                decoded
            )

            offset += size

        return instructions

    # ========================================================
    # VALIDATE INSTRUCTION
    # ========================================================

    def validate_instruction(
        self,
        instruction: dict,
    ) -> bool:
        """
        Validate decoded instruction metadata.
        """

        if not isinstance(
            instruction,
            dict,
        ):
            return False

        required_keys = {
            "name",
            "opcode",
            "operand",
            "size",
            "requires_operand",
        }

        if not required_keys.issubset(
            instruction.keys()
        ):
            return False

        try:

            name = normalize_instruction(
                instruction["name"]
            )

            opcode = self.validate_byte(
                instruction["opcode"],
                "Opcode",
            )

            operand = instruction[
                "operand"
            ]

            size = instruction[
                "size"
            ]

            needs_operand = instruction[
                "requires_operand"
            ]

        except (
            TypeError,
            ValueError,
        ):

            return False

        if name not in self.opcode_table:
            return False

        if self.opcode_table[
            name
        ] != opcode:
            return False

        expected_size = (
            self.get_size(
                name
            )
        )

        if size != expected_size:
            return False

        expected_operand = (
            self.requires_operand(
                name
            )
        )

        if (
            needs_operand
            != expected_operand
        ):
            return False

        if needs_operand:

            if operand is None:
                return False

            if not (
                isinstance(
                    operand,
                    int,
                )
                and 0 <= operand <= 0xFF
            ):
                return False

        else:

            if operand is not None:
                return False

        return True

    # ========================================================
    # LIST INSTRUCTIONS
    # ========================================================

    def list_instructions(
        self,
    ) -> list[dict]:
        """
        Return all instruction metadata.

        Sorted by opcode.
        """

        result = []

        for opcode, name in sorted(
            self._reverse_table.items()
        ):

            result.append(
                self.decode(
                    opcode,
                    0x00
                    if name
                    in TWO_BYTE_INSTRUCTIONS
                    else None,
                )
            )

        return result

    # ========================================================
    # DISASSEMBLE ONE
    # ========================================================

    def disassemble(
        self,
        instruction: dict,
    ) -> str:
        """
        Convert decoded instruction
        into readable assembly text.

        Examples:

            LOAD 0x42
            INC
            HALT
        """

        if not self.validate_instruction(
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

        if operand is None:

            return name

        return (
            f"{name} "
            f"0x{operand:02X}"
        )

    # ========================================================
    # DISASSEMBLE PROGRAM
    # ========================================================

    def disassemble_program(
        self,
        data: bytes | bytearray,
    ) -> list[str]:
        """
        Disassemble complete machine code.

        Returns a list of assembly lines.
        """

        instructions = (
            self.decode_stream(
                data
            )
        )

        return [
            self.disassemble(
                instruction
            )
            for instruction
            in instructions
        ]

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump_instruction(
        self,
        instruction: dict,
    ) -> None:
        """
        Print decoded instruction.
        """

        if not self.validate_instruction(
            instruction
        ):
            raise ValueError(
                "Invalid instruction."
            )

        print(
            "======== DECODED INSTRUCTION ========"
        )

        print(
            f"Name             : "
            f"{instruction['name']}"
        )

        print(
            f"Opcode           : "
            f"0x{instruction['opcode']:02X}"
        )

        if instruction[
            "operand"
        ] is None:

            print(
                "Operand          : None"
            )

        else:

            print(
                f"Operand          : "
                f"0x{instruction['operand']:02X}"
            )

        print(
            f"Size             : "
            f"{instruction['size']} byte(s)"
        )

        print(
            f"Requires Operand : "
            f"{instruction['requires_operand']}"
        )

        print(
            f"Assembly         : "
            f"{self.disassemble(instruction)}"
        )

        print(
            "======================================"
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable decoder information.
        """

        return (
            f"InstructionDecoder("
            f"instructions="
            f"{len(self.opcode_table)}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "InstructionDecoder",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    decoder = (
        InstructionDecoder()
    )

    print(
        "MiniCPU 8-bit "
        "Instruction Decoder"
    )

    print()

    # LOAD 0x42
    instruction = decoder.decode(
        0x10,
        0x42,
    )

    decoder.dump_instruction(
        instruction
    )

    print()

    # INC
    instruction = decoder.decode(
        0xC0
    )

    decoder.dump_instruction(
        instruction
    )

    print()

    # HALT
    instruction = decoder.decode(
        0xF0
    )

    decoder.dump_instruction(
        instruction
    )

    print()

    # Decode complete program
    program = bytes(
        [
            0x10,
            0x42,
            0xC0,
            0xF0,
        ]
    )

    print(
        "Disassembly:"
    )

    for line in decoder.disassemble_program(
        program
    ):
        print(
            f"  {line}"
        )
