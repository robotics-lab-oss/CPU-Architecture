"""
instruction_set.py

MiniCPU 8-bit CPU Architecture
Instruction Set Definition

CPU:
    - 8-bit data
    - 8-bit address space
    - 16 instructions
    - 1-byte and 2-byte instructions

This module defines:
    - Instruction metadata
    - Operand types
    - Instruction validation
    - Instruction size
    - Operand requirements

The opcode values are imported from opcode.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from opcode import (
    OPCODES,
    ONE_BYTE_INSTRUCTIONS,
    TWO_BYTE_INSTRUCTIONS,
    get_instruction_size,
    normalize_instruction,
)


# ============================================================
# CPU LIMITS
# ============================================================

WORD_BITS = 8

BYTE_MIN = 0x00
BYTE_MAX = 0xFF

ADDRESS_MIN = 0x00
ADDRESS_MAX = 0xFF

REGISTER_COUNT = 16


# ============================================================
# OPERAND TYPES
# ============================================================

class OperandType(str, Enum):
    """
    Supported operand categories.
    """

    NONE = "none"

    REGISTER = "register"

    IMMEDIATE = "immediate"

    ADDRESS = "address"

    LABEL = "label"

    SYMBOL = "symbol"


# ============================================================
# INSTRUCTION CATEGORIES
# ============================================================

class InstructionCategory(str, Enum):
    """
    Instruction categories used by the assembler
    and future CPU emulator.
    """

    SYSTEM = "system"

    IO = "io"

    MEMORY = "memory"

    ARITHMETIC = "arithmetic"

    LOGIC = "logic"

    CONTROL_FLOW = "control_flow"

    COMPARE = "compare"


# ============================================================
# INSTRUCTION DEFINITION
# ============================================================

@dataclass(frozen=True)
class InstructionDefinition:
    """
    Complete definition of one CPU instruction.
    """

    name: str

    opcode: int

    size: int

    category: InstructionCategory

    operand_count: int

    operand_types: Tuple[
        OperandType,
        ...
    ]

    description: str = ""

    def requires_operand(self) -> bool:
        """
        Return True if instruction has operands.
        """

        return self.operand_count > 0

    def is_one_byte(self) -> bool:
        """
        Return True for 1-byte instructions.
        """

        return self.size == 1

    def is_two_byte(self) -> bool:
        """
        Return True for 2-byte instructions.
        """

        return self.size == 2


# ============================================================
# INSTRUCTION SET
# ============================================================

INSTRUCTION_SET = {

    # --------------------------------------------------------
    # 1 BYTE INSTRUCTIONS
    # --------------------------------------------------------

    "NOP": InstructionDefinition(
        name="NOP",
        opcode=OPCODES["NOP"],
        size=1,
        category=InstructionCategory.SYSTEM,
        operand_count=0,
        operand_types=(),
        description=(
            "No operation."
        ),
    ),

    "OUT": InstructionDefinition(
        name="OUT",
        opcode=OPCODES["OUT"],
        size=1,
        category=InstructionCategory.IO,
        operand_count=0,
        operand_types=(),
        description=(
            "Output operation."
        ),
    ),

    "IN": InstructionDefinition(
        name="IN",
        opcode=OPCODES["IN"],
        size=1,
        category=InstructionCategory.IO,
        operand_count=0,
        operand_types=(),
        description=(
            "Input operation."
        ),
    ),

    "INC": InstructionDefinition(
        name="INC",
        opcode=OPCODES["INC"],
        size=1,
        category=InstructionCategory.ARITHMETIC,
        operand_count=0,
        operand_types=(),
        description=(
            "Increment operation."
        ),
    ),

    "DEC": InstructionDefinition(
        name="DEC",
        opcode=OPCODES["DEC"],
        size=1,
        category=InstructionCategory.ARITHMETIC,
        operand_count=0,
        operand_types=(),
        description=(
            "Decrement operation."
        ),
    ),

    "HALT": InstructionDefinition(
        name="HALT",
        opcode=OPCODES["HALT"],
        size=1,
        category=InstructionCategory.SYSTEM,
        operand_count=0,
        operand_types=(),
        description=(
            "Stop CPU execution."
        ),
    ),

    # --------------------------------------------------------
    # 2 BYTE INSTRUCTIONS
    # --------------------------------------------------------

    "LOAD": InstructionDefinition(
        name="LOAD",
        opcode=OPCODES["LOAD"],
        size=2,
        category=InstructionCategory.MEMORY,
        operand_count=1,
        operand_types=(
            OperandType.IMMEDIATE,
        ),
        description=(
            "Load an 8-bit value."
        ),
    ),

    "STORE": InstructionDefinition(
        name="STORE",
        opcode=OPCODES["STORE"],
        size=2,
        category=InstructionCategory.MEMORY,
        operand_count=1,
        operand_types=(
            OperandType.ADDRESS,
        ),
        description=(
            "Store data at an 8-bit address."
        ),
    ),

    "ADD": InstructionDefinition(
        name="ADD",
        opcode=OPCODES["ADD"],
        size=2,
        category=InstructionCategory.ARITHMETIC,
        operand_count=1,
        operand_types=(
            OperandType.IMMEDIATE,
        ),
        description=(
            "Add an 8-bit operand."
        ),
    ),

    "SUB": InstructionDefinition(
        name="SUB",
        opcode=OPCODES["SUB"],
        size=2,
        category=InstructionCategory.ARITHMETIC,
        operand_count=1,
        operand_types=(
            OperandType.IMMEDIATE,
        ),
        description=(
            "Subtract an 8-bit operand."
        ),
    ),

    "AND": InstructionDefinition(
        name="AND",
        opcode=OPCODES["AND"],
        size=2,
        category=InstructionCategory.LOGIC,
        operand_count=1,
        operand_types=(
            OperandType.IMMEDIATE,
        ),
        description=(
            "Bitwise AND operation."
        ),
    ),

    "OR": InstructionDefinition(
        name="OR",
        opcode=OPCODES["OR"],
        size=2,
        category=InstructionCategory.LOGIC,
        operand_count=1,
        operand_types=(
            OperandType.IMMEDIATE,
        ),
        description=(
            "Bitwise OR operation."
        ),
    ),

    "XOR": InstructionDefinition(
        name="XOR",
        opcode=OPCODES["XOR"],
        size=2,
        category=InstructionCategory.LOGIC,
        operand_count=1,
        operand_types=(
            OperandType.IMMEDIATE,
        ),
        description=(
            "Bitwise XOR operation."
        ),
    ),

    "JMP": InstructionDefinition(
        name="JMP",
        opcode=OPCODES["JMP"],
        size=2,
        category=InstructionCategory.CONTROL_FLOW,
        operand_count=1,
        operand_types=(
            OperandType.LABEL,
        ),
        description=(
            "Unconditional jump."
        ),
    ),

    "JZ": InstructionDefinition(
        name="JZ",
        opcode=OPCODES["JZ"],
        size=2,
        category=InstructionCategory.CONTROL_FLOW,
        operand_count=1,
        operand_types=(
            OperandType.LABEL,
        ),
        description=(
            "Jump when zero flag is set."
        ),
    ),

    "CMP": InstructionDefinition(
        name="CMP",
        opcode=OPCODES["CMP"],
        size=2,
        category=InstructionCategory.COMPARE,
        operand_count=1,
        operand_types=(
            OperandType.IMMEDIATE,
        ),
        description=(
            "Compare with an 8-bit operand."
        ),
    ),
}


# ============================================================
# VALIDATION
# ============================================================

def validate_instruction_set() -> None:
    """
    Validate the complete instruction set.
    """

    # Exactly 16 instructions
    if len(INSTRUCTION_SET) != 16:
        raise ValueError(
            "MiniCPU must have exactly "
            f"16 instructions. Found: "
            f"{len(INSTRUCTION_SET)}"
        )

    # Every opcode must exist
    for name, definition in (
        INSTRUCTION_SET.items()
    ):

        if name not in OPCODES:
            raise ValueError(
                f"Missing opcode for "
                f"instruction: {name}"
            )

        if definition.opcode != OPCODES[name]:
            raise ValueError(
                f"Opcode mismatch for "
                f"{name}"
            )

        # Instruction size
        if definition.size not in (1, 2):
            raise ValueError(
                f"Invalid instruction size "
                f"for {name}: "
                f"{definition.size}"
            )

        # Operand count
        if (
            definition.operand_count
            != len(definition.operand_types)
        ):
            raise ValueError(
                f"Operand count mismatch "
                f"for {name}"
            )

        # Opcode must be 8-bit
        if not (
            BYTE_MIN
            <= definition.opcode
            <= BYTE_MAX
        ):
            raise ValueError(
                f"Opcode out of 8-bit range "
                f"for {name}"
            )

        # Size must match opcode.py
        opcode_size = (
            get_instruction_size(name)
        )

        if definition.size != opcode_size:
            raise ValueError(
                f"Instruction size mismatch "
                f"for {name}: "
                f"instruction_set.py="
                f"{definition.size}, "
                f"opcode.py="
                f"{opcode_size}"
            )

    # Check 1-byte instructions
    for name in ONE_BYTE_INSTRUCTIONS:

        if name not in INSTRUCTION_SET:
            raise ValueError(
                f"1-byte instruction "
                f"{name} is missing"
            )

        if (
            INSTRUCTION_SET[name].size
            != 1
        ):
            raise ValueError(
                f"{name} is marked as "
                f"1-byte but size is "
                f"{INSTRUCTION_SET[name].size}"
            )

    # Check 2-byte instructions
    for name in TWO_BYTE_INSTRUCTIONS:

        if name not in INSTRUCTION_SET:
            raise ValueError(
                f"2-byte instruction "
                f"{name} is missing"
            )

        if (
            INSTRUCTION_SET[name].size
            != 2
        ):
            raise ValueError(
                f"{name} is marked as "
                f"2-byte but size is "
                f"{INSTRUCTION_SET[name].size}"
            )


# ============================================================
# LOOKUP FUNCTIONS
# ============================================================

def is_valid_instruction(
    instruction: str,
) -> bool:
    """
    Check whether an instruction exists.
    """

    try:
        name = normalize_instruction(
            instruction
        )
    except (
        TypeError,
        AttributeError,
    ):
        return False

    return name in INSTRUCTION_SET


def get_instruction(
    instruction: str,
) -> InstructionDefinition:
    """
    Get complete instruction definition.
    """

    name = normalize_instruction(
        instruction
    )

    if name not in INSTRUCTION_SET:
        raise ValueError(
            f"Unknown instruction: {name}"
        )

    return INSTRUCTION_SET[name]


def get_opcode(
    instruction: str,
) -> int:
    """
    Get opcode value.
    """

    return get_instruction(
        instruction
    ).opcode


def get_instruction_size_from_set(
    instruction: str,
) -> int:
    """
    Get instruction size.
    """

    return get_instruction(
        instruction
    ).size


def get_operand_count(
    instruction: str,
) -> int:
    """
    Get number of operands.
    """

    return get_instruction(
        instruction
    ).operand_count


def get_operand_types(
    instruction: str,
) -> Tuple[
    OperandType,
    ...
]:
    """
    Get allowed operand types.
    """

    return get_instruction(
        instruction
    ).operand_types


def requires_operand(
    instruction: str,
) -> bool:
    """
    Return True if instruction
    requires an operand.
    """

    return (
        get_instruction(
            instruction
        ).operand_count > 0
    )


def is_one_byte_instruction(
    instruction: str,
) -> bool:
    """
    Return True for 1-byte instruction.
    """

    return (
        get_instruction(
            instruction
        ).size == 1
    )


def is_two_byte_instruction(
    instruction: str,
) -> bool:
    """
    Return True for 2-byte instruction.
    """

    return (
        get_instruction(
            instruction
        ).size == 2
    )


# ============================================================
# OPERAND VALIDATION
# ============================================================

def validate_operand_count(
    instruction: str,
    operands: list,
) -> None:
    """
    Validate number of operands.
    """

    definition = get_instruction(
        instruction
    )

    actual_count = len(operands)

    if (
        actual_count
        != definition.operand_count
    ):
        raise ValueError(
            f"{definition.name} expects "
            f"{definition.operand_count} "
            f"operand(s), got "
            f"{actual_count}"
        )


def validate_byte_value(
    value: int,
    name: str = "value",
) -> None:
    """
    Validate an 8-bit value.
    """

    if not isinstance(value, int):
        raise TypeError(
            f"{name} must be an integer"
        )

    if not (
        BYTE_MIN
        <= value
        <= BYTE_MAX
    ):
        raise ValueError(
            f"{name} must be between "
            f"0x00 and 0xFF"
        )


def validate_address(
    address: int,
) -> None:
    """
    Validate an 8-bit memory address.
    """

    if not isinstance(
        address,
        int,
    ):
        raise TypeError(
            "Address must be an integer"
        )

    if not (
        ADDRESS_MIN
        <= address
        <= ADDRESS_MAX
    ):
        raise ValueError(
            "Address must be between "
            "0x00 and 0xFF"
        )


# ============================================================
# INSTRUCTION SUMMARY
# ============================================================

def get_instruction_summary() -> list:
    """
    Return all instruction definitions
    as a list of dictionaries.
    """

    summary = []

    for name, definition in (
        INSTRUCTION_SET.items()
    ):

        summary.append(
            {
                "name": definition.name,
                "opcode": definition.opcode,
                "size": definition.size,
                "category": (
                    definition.category.value
                ),
                "operand_count": (
                    definition.operand_count
                ),
                "operand_types": [
                    operand.value
                    for operand in (
                        definition.operand_types
                    )
                ],
                "description": (
                    definition.description
                ),
            }
        )

    return summary


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "WORD_BITS",
    "BYTE_MIN",
    "BYTE_MAX",
    "ADDRESS_MIN",
    "ADDRESS_MAX",
    "REGISTER_COUNT",
    "OperandType",
    "InstructionCategory",
    "InstructionDefinition",
    "INSTRUCTION_SET",
    "validate_instruction_set",
    "is_valid_instruction",
    "get_instruction",
    "get_opcode",
    "get_instruction_size_from_set",
    "get_operand_count",
    "get_operand_types",
    "requires_operand",
    "is_one_byte_instruction",
    "is_two_byte_instruction",
    "validate_operand_count",
    "validate_byte_value",
    "validate_address",
    "get_instruction_summary",
]


# ============================================================
# VALIDATE ON IMPORT
# ============================================================

validate_instruction_set()


# ============================================================
# DEBUG / TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Instruction Set"
    )

    print(
        "=============================="
    )

    print(
        f"Instruction count: "
        f"{len(INSTRUCTION_SET)}"
    )

    print()

    for definition in (
        INSTRUCTION_SET.values()
    ):

        operands = ", ".join(
            operand.value
            for operand in (
                definition.operand_types
            )
        )

        print(
            f"{definition.name:<6} "
            f"Opcode=0x"
            f"{definition.opcode:02X} "
            f"Size={definition.size} "
            f"OperandCount="
            f"{definition.operand_count} "
            f"Types=[{operands}]"
  )
