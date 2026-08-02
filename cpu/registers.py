"""
registers.py

MiniCPU 8-bit CPU Architecture
CPU Register File

Architecture:
    - 8-bit data width
    - 8-bit register values
    - Register values: 0x00 - 0xFF

Registers:
    A   : Accumulator
    B   : General-purpose register
    C   : General-purpose register
    D   : General-purpose register

    IR  : Instruction Register
    MAR : Memory Address Register
    MDR : Memory Data Register
"""

from __future__ import annotations


class Registers:
    """
    MiniCPU 8-bit register file.

    General-purpose registers:

        A
        B
        C
        D

    Special-purpose registers:

        IR
        MAR
        MDR
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    WIDTH = 8

    MIN_VALUE = 0x00
    MAX_VALUE = 0xFF

    REGISTER_NAMES = (
        "A",
        "B",
        "C",
        "D",
        "IR",
        "MAR",
        "MDR",
    )

    GENERAL_PURPOSE_REGISTERS = (
        "A",
        "B",
        "C",
        "D",
    )

    SPECIAL_REGISTERS = (
        "IR",
        "MAR",
        "MDR",
    )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):
        """
        Initialize all registers to zero.
        """

        self.reset()

    # ========================================================
    # RESET
    # ========================================================

    def reset(self):
        """
        Reset all registers to 0x00.
        """

        self.A = 0x00
        self.B = 0x00
        self.C = 0x00
        self.D = 0x00

        self.IR = 0x00
        self.MAR = 0x00
        self.MDR = 0x00

    # ========================================================
    # VALIDATE REGISTER NAME
    # ========================================================

    @classmethod
    def normalize_name(
        cls,
        name: str,
    ) -> str:
        """
        Normalize a register name.

        Example:

            "a"   -> "A"
            " A " -> "A"
            "ir"  -> "IR"
        """

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Register name must be a string."
            )

        name = name.strip().upper()

        if name not in cls.REGISTER_NAMES:
            raise ValueError(
                f"Unknown register: {name}"
            )

        return name

    # ========================================================
    # VALIDATE VALUE
    # ========================================================

    @classmethod
    def validate_value(
        cls,
        value: int,
    ) -> int:
        """
        Validate an 8-bit register value.

        Valid range:

            0x00 - 0xFF
        """

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "Register value must be an integer."
            )

        if not (
            cls.MIN_VALUE
            <= value
            <= cls.MAX_VALUE
        ):
            raise ValueError(
                f"Register value must be between "
                f"0x{cls.MIN_VALUE:02X} and "
                f"0x{cls.MAX_VALUE:02X}. "
                f"Received: {value}"
            )

        return value

    # ========================================================
    # GET REGISTER
    # ========================================================

    def get(
        self,
        name: str,
    ) -> int:
        """
        Read a register value.

        Example:

            registers.get("A")
        """

        name = self.normalize_name(
            name
        )

        return getattr(
            self,
            name,
        )

    # ========================================================
    # SET REGISTER
    # ========================================================

    def set(
        self,
        name: str,
        value: int,
    ) -> None:
        """
        Write an 8-bit value to a register.

        Example:

            registers.set("A", 0x42)
        """

        name = self.normalize_name(
            name
        )

        value = self.validate_value(
            value
        )

        setattr(
            self,
            name,
            value,
        )

    # ========================================================
    # CLEAR REGISTER
    # ========================================================

    def clear(
        self,
        name: str,
    ) -> None:
        """
        Set one register to zero.
        """

        self.set(
            name,
            0x00,
        )

    # ========================================================
    # INCREMENT REGISTER
    # ========================================================

    def increment(
        self,
        name: str,
        amount: int = 1,
    ) -> int:
        """
        Increment an 8-bit register.

        Overflow wraps around.

        Example:

            0xFF + 1 = 0x00
        """

        name = self.normalize_name(
            name
        )

        if not isinstance(
            amount,
            int,
        ):
            raise TypeError(
                "Increment amount must be "
                "an integer."
            )

        current = self.get(
            name
        )

        value = (
            current
            + amount
        ) & self.MAX_VALUE

        self.set(
            name,
            value,
        )

        return value

    # ========================================================
    # DECREMENT REGISTER
    # ========================================================

    def decrement(
        self,
        name: str,
        amount: int = 1,
    ) -> int:
        """
        Decrement an 8-bit register.

        Underflow wraps around.

        Example:

            0x00 - 1 = 0xFF
        """

        name = self.normalize_name(
            name
        )

        if not isinstance(
            amount,
            int,
        ):
            raise TypeError(
                "Decrement amount must be "
                "an integer."
            )

        current = self.get(
            name
        )

        value = (
            current
            - amount
        ) & self.MAX_VALUE

        self.set(
            name,
            value,
        )

        return value

    # ========================================================
    # GENERAL PURPOSE REGISTERS
    # ========================================================

    def get_general_purpose(
        self,
    ) -> dict[str, int]:
        """
        Return all general-purpose registers.
        """

        return {
            name: self.get(name)
            for name
            in self.GENERAL_PURPOSE_REGISTERS
        }

    # ========================================================
    # SPECIAL REGISTERS
    # ========================================================

    def get_special_registers(
        self,
    ) -> dict[str, int]:
        """
        Return all special-purpose registers.
        """

        return {
            name: self.get(name)
            for name
            in self.SPECIAL_REGISTERS
        }

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> dict[str, int]:
        """
        Return a complete copy of
        the current register state.
        """

        return {
            name: self.get(name)
            for name
            in self.REGISTER_NAMES
        }

    # ========================================================
    # LOAD SNAPSHOT
    # ========================================================

    def load_snapshot(
        self,
        state: dict[str, int],
    ) -> None:
        """
        Restore register values from
        a snapshot dictionary.
        """

        if not isinstance(
            state,
            dict,
        ):
            raise TypeError(
                "Register state must be a dictionary."
            )

        for name in self.REGISTER_NAMES:

            if name in state:

                self.set(
                    name,
                    state[name],
                )

    # ========================================================
    # COPY REGISTER
    # ========================================================

    def copy(
        self,
        source: str,
        destination: str,
    ) -> int:
        """
        Copy one register value into another.

        Example:

            registers.copy("A", "B")
        """

        value = self.get(
            source
        )

        self.set(
            destination,
            value,
        )

        return value

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print register state.
        """

        print(
            "========== REGISTERS =========="
        )

        for name in self.REGISTER_NAMES:

            value = self.get(
                name
            )

            print(
                f"{name:<4} = "
                f"0x{value:02X} "
                f"({value:3d})"
            )

        print(
            "==============================="
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return a readable register state.
        """

        values = []

        for name in self.REGISTER_NAMES:

            value = self.get(
                name
            )

            values.append(
                f"{name}=0x{value:02X}"
            )

        return (
            f"Registers("
            f"{', '.join(values)}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Registers",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    registers = Registers()

    print(
        "MiniCPU 8-bit Register File"
    )

    print(
        f"Register width: "
        f"{Registers.WIDTH}-bit"
    )

    print()

    registers.set(
        "A",
        0x42,
    )

    registers.set(
        "B",
        0x10,
    )

    print(
        f"A = "
        f"0x{registers.get('A'):02X}"
    )

    print(
        f"B = "
        f"0x{registers.get('B'):02X}"
    )

    registers.increment(
        "A"
    )

    print(
        f"A after INC = "
        f"0x{registers.get('A'):02X}"
    )

    registers.copy(
        "A",
        "C",
    )

    print(
        f"C after COPY = "
        f"0x{registers.get('C'):02X}"
    )

    registers.dump()
