"""
opcode.py

MiniCPU 8-bit CPU Architecture
16-Instruction Opcode Definition

Instruction format:
    1-byte instructions:
        Opcode byte only

    2-byte instructions:
        Opcode byte + 8-bit operand

Opcode layout:
    Upper 4 bits = instruction opcode
    Lower 4 bits = reserved for register/mode extensions

Example:
    LOAD = 0x10
    STORE = 0x20
"""

# ============================================================
# OPCODES
# ============================================================

OPCODES = {

    # --------------------------------------------------------
    # 1 Byte Instructions
    # --------------------------------------------------------

    "NOP":   0x00,
    "OUT":   0xA0,
    "IN":    0xB0,
    "INC":   0xC0,
    "DEC":   0xD0,
    "HALT":  0xF0,

    # --------------------------------------------------------
    # 2 Byte Instructions
    # --------------------------------------------------------

    "LOAD":  0x10,
    "STORE": 0x20,
    "ADD":   0x30,
    "SUB":   0x40,
    "AND":   0x50,
    "OR":    0x60,
    "XOR":   0x70,
    "JMP":   0x80,
    "JZ":    0x90,
    "CMP":   0xE0,
}


# ============================================================
# INSTRUCTION GROUPS
# ============================================================

ONE_BYTE_INSTRUCTIONS = {
    "NOP",
    "OUT",
    "IN",
    "INC",
    "DEC",
    "HALT",
}


TWO_BYTE_INSTRUCTIONS = {
    "LOAD",
    "STORE",
    "ADD",
    "SUB",
    "AND",
    "OR",
    "XOR",
    "JMP",
    "JZ",
    "CMP",
}


# ============================================================
# OPERAND INSTRUCTIONS
#
# These instructions require a second byte.
# This is kept for compatibility with symbol_table.py.
# ============================================================

OPERAND_INSTRUCTIONS = TWO_BYTE_INSTRUCTIONS


# ============================================================
# INSTRUCTION SIZES
# ============================================================

INSTRUCTION_SIZES = {
    instruction: 1
    for instruction in ONE_BYTE_INSTRUCTIONS
}

INSTRUCTION_SIZES.update({
    instruction: 2
    for instruction in TWO_BYTE_INSTRUCTIONS
})


# ============================================================
# INSTRUCTION COUNT
# ============================================================

INSTRUCTION_COUNT = len(OPCODES)


# ============================================================
# VALIDATION
# ============================================================

def normalize_instruction(instruction: str) -> str:
    """
    Convert instruction name to uppercase.

    Example:
        "load" -> "LOAD"
        "Load" -> "LOAD"
    """

    if not isinstance(instruction, str):
        raise TypeError(
            "Instruction must be a string"
        )

    return instruction.strip().upper()


def is_valid_instruction(instruction: str) -> bool:
    """
    Return True if instruction exists.
    """

    instruction = normalize_instruction(
        instruction
    )

    return instruction in OPCODES


def get_opcode(instruction: str) -> int:
    """
    Return numeric opcode for an instruction.

    Example:
        get_opcode("LOAD") -> 0x10
    """

    instruction = normalize_instruction(
        instruction
    )

    if instruction not in OPCODES:
        raise ValueError(
            f"Unknown instruction: {instruction}"
        )

    return OPCODES[instruction]


def get_instruction_size(
    instruction: str,
) -> int:
    """
    Return instruction size in bytes.

    1-byte instruction:
        returns 1

    2-byte instruction:
        returns 2
    """

    instruction = normalize_instruction(
        instruction
    )

    if instruction not in INSTRUCTION_SIZES:
        raise ValueError(
            f"Unknown instruction: {instruction}"
        )

    return INSTRUCTION_SIZES[instruction]


def requires_operand(
    instruction: str,
) -> bool:
    """
    Return True if instruction requires
    a second operand byte.
    """

    instruction = normalize_instruction(
        instruction
    )

    return instruction in OPERAND_INSTRUCTIONS


def get_instruction_info(
    instruction: str,
) -> dict:
    """
    Return complete metadata for an instruction.
    """

    instruction = normalize_instruction(
        instruction
    )

    if instruction not in OPCODES:
        raise ValueError(
            f"Unknown instruction: {instruction}"
        )

    return {
        "name": instruction,
        "opcode": OPCODES[instruction],
        "size": INSTRUCTION_SIZES[instruction],
        "requires_operand": (
            instruction
            in OPERAND_INSTRUCTIONS
        ),
    }


# ============================================================
# OPCODE VALIDATION
# ============================================================

def validate_opcodes() -> None:
    """
    Validate the complete 16-instruction ISA.
    """

    if len(OPCODES) != 16:
        raise ValueError(
            f"CPU must have exactly 16 instructions. "
            f"Found: {len(OPCODES)}"
        )

    for name, opcode in OPCODES.items():

        if not isinstance(opcode, int):
            raise TypeError(
                f"Opcode for {name} must be integer"
            )

        if not 0 <= opcode <= 0xFF:
            raise ValueError(
                f"Opcode for {name} is outside "
                f"8-bit range: {opcode}"
            )

    for instruction in ONE_BYTE_INSTRUCTIONS:

        if instruction not in OPCODES:
            raise ValueError(
                f"Missing opcode for "
                f"1-byte instruction: "
                f"{instruction}"
            )

    for instruction in TWO_BYTE_INSTRUCTIONS:

        if instruction not in OPCODES:
            raise ValueError(
                f"Missing opcode for "
                f"2-byte instruction: "
                f"{instruction}"
            )

    if (
        ONE_BYTE_INSTRUCTIONS
        & TWO_BYTE_INSTRUCTIONS
    ):
        raise ValueError(
            "An instruction cannot be both "
            "1-byte and 2-byte"
        )


# ============================================================
# RUN VALIDATION WHEN MODULE LOADS
# ============================================================

validate_opcodes()


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "OPCODES",
    "ONE_BYTE_INSTRUCTIONS",
    "TWO_BYTE_INSTRUCTIONS",
    "OPERAND_INSTRUCTIONS",
    "INSTRUCTION_SIZES",
    "INSTRUCTION_COUNT",
    "normalize_instruction",
    "is_valid_instruction",
    "get_opcode",
    "get_instruction_size",
    "requires_operand",
    "get_instruction_info",
    "validate_opcodes",
]


# ============================================================
# TEST / DEBUG
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Instruction Set"
    )

    print(
        f"Instruction count: "
        f"{INSTRUCTION_COUNT}"
    )

    print()

    for instruction in OPCODES:

        info = get_instruction_info(
            instruction
        )

        print(
            f"{info['name']:<6} "
            f"Opcode=0x"
            f"{info['opcode']:02X} "
            f"Size={info['size']} "
            f"Byte(s) "
            f"Operand="
            f"{info['requires_operand']}"
  )
