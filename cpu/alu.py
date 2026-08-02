"""
alu.py

MiniCPU 8-bit CPU Architecture
Arithmetic Logic Unit (ALU)

Supported operations:

    ADD
    SUB
    AND
    OR
    XOR
    CMP

The ALU works with 8-bit unsigned values.

Value range:

    0x00 - 0xFF

Overflow behavior:

    Results are masked to 8-bit.

Example:

    0xFF + 0x01 = 0x00
"""

from __future__ import annotations

from typing import Optional


class ALU:
    """
    8-bit Arithmetic Logic Unit.

    The ALU performs arithmetic and logical
    operations and calculates status flags.

    Flags:

        Zero (Z)
        Carry (C)
        Negative (N)
        Overflow (V)
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    WIDTH = 8

    MIN_VALUE = 0x00
    MAX_VALUE = 0xFF

    SIGN_BIT = 0x80

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):
        """
        Initialize ALU state.
        """

        self.result = 0x00

        self.zero = False

        self.carry = False

        self.negative = False

        self.overflow = False

    # ========================================================
    # VALIDATE VALUE
    # ========================================================

    @classmethod
    def validate_value(
        cls,
        value: int,
    ) -> int:
        """
        Validate an 8-bit value.
        """

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "ALU value must be an integer."
            )

        if not (
            cls.MIN_VALUE
            <= value
            <= cls.MAX_VALUE
        ):
            raise ValueError(
                f"ALU value must be between "
                f"0x{cls.MIN_VALUE:02X} and "
                f"0x{cls.MAX_VALUE:02X}."
            )

        return value

    # ========================================================
    # UPDATE FLAGS
    # ========================================================

    def _update_flags(
        self,
        result: int,
    ) -> None:
        """
        Update Zero and Negative flags.
        """

        self.result = (
            result
            & self.MAX_VALUE
        )

        self.zero = (
            self.result == 0
        )

        self.negative = bool(
            self.result
            & self.SIGN_BIT
        )

    # ========================================================
    # ADD
    # ========================================================

    def add(
        self,
        a: int,
        b: int,
    ) -> int:
        """
        Add two 8-bit values.

        Example:

            0x10 + 0x20 = 0x30

        Carry:

            0xFF + 0x01 = 0x00
            Carry = True
        """

        a = self.validate_value(
            a
        )

        b = self.validate_value(
            b
        )

        full_result = (
            a + b
        )

        result = (
            full_result
            & self.MAX_VALUE
        )

        self.carry = (
            full_result
            > self.MAX_VALUE
        )

        # Signed overflow:
        # Positive + Positive = Negative
        # Negative + Negative = Positive

        self.overflow = (
            ((a ^ result) & self.SIGN_BIT)
            != 0
            and
            ((b ^ result) & self.SIGN_BIT)
            != 0
        )

        self._update_flags(
            result
        )

        return self.result

    # ========================================================
    # SUBTRACT
    # ========================================================

    def subtract(
        self,
        a: int,
        b: int,
    ) -> int:
        """
        Subtract B from A.

        Example:

            0x20 - 0x10 = 0x10

        Borrow behavior:

            A < B
                carry = False
        """

        a = self.validate_value(
            a
        )

        b = self.validate_value(
            b
        )

        full_result = (
            a - b
        )

        result = (
            full_result
            & self.MAX_VALUE
        )

        self.carry = (
            a >= b
        )

        # Signed overflow:
        # Positive - Negative = Negative
        # Negative - Positive = Positive

        self.overflow = (
            ((a ^ b) & self.SIGN_BIT)
            != 0
            and
            ((a ^ result) & self.SIGN_BIT)
            != 0
        )

        self._update_flags(
            result
        )

        return self.result

    # ========================================================
    # AND
    # ========================================================

    def bitwise_and(
        self,
        a: int,
        b: int,
    ) -> int:
        """
        Perform bitwise AND.
        """

        a = self.validate_value(
            a
        )

        b = self.validate_value(
            b
        )

        result = (
            a & b
        )

        self.carry = False

        self.overflow = False

        self._update_flags(
            result
        )

        return self.result

    # ========================================================
    # OR
    # ========================================================

    def bitwise_or(
        self,
        a: int,
        b: int,
    ) -> int:
        """
        Perform bitwise OR.
        """

        a = self.validate_value(
            a
        )

        b = self.validate_value(
            b
        )

        result = (
            a | b
        )

        self.carry = False

        self.overflow = False

        self._update_flags(
            result
        )

        return self.result

    # ========================================================
    # XOR
    # ========================================================

    def bitwise_xor(
        self,
        a: int,
        b: int,
    ) -> int:
        """
        Perform bitwise XOR.
        """

        a = self.validate_value(
            a
        )

        b = self.validate_value(
            b
        )

        result = (
            a ^ b
        )

        self.carry = False

        self.overflow = False

        self._update_flags(
            result
        )

        return self.result

    # ========================================================
    # COMPARE
    # ========================================================

    def compare(
        self,
        a: int,
        b: int,
    ) -> int:
        """
        Compare A and B.

        This performs subtraction internally:

            A - B

        The result is returned and flags are updated.

        Typical usage:

            CMP A, B
            JZ address

        If A == B:

            Zero flag = True
        """

        return self.subtract(
            a,
            b,
        )

    # ========================================================
    # GENERIC EXECUTE
    # ========================================================

    def execute(
        self,
        operation: str,
        a: int,
        b: Optional[int] = None,
    ) -> int:
        """
        Execute an ALU operation.

        Supported:

            ADD
            SUB
            AND
            OR
            XOR
            CMP
        """

        if not isinstance(
            operation,
            str,
        ):
            raise TypeError(
                "ALU operation must be a string."
            )

        operation = (
            operation
            .strip()
            .upper()
        )

        if operation in {
            "ADD",
            "SUB",
            "AND",
            "OR",
            "XOR",
            "CMP",
        }:

            if b is None:
                raise ValueError(
                    f"{operation} requires "
                    f"two operands."
                )

        if operation == "ADD":

            return self.add(
                a,
                b,
            )

        if operation == "SUB":

            return self.subtract(
                a,
                b,
            )

        if operation == "AND":

            return self.bitwise_and(
                a,
                b,
            )

        if operation == "OR":

            return self.bitwise_or(
                a,
                b,
            )

        if operation == "XOR":

            return self.bitwise_xor(
                a,
                b,
            )

        if operation == "CMP":

            return self.compare(
                a,
                b,
            )

        raise ValueError(
            f"Unknown ALU operation: "
            f"{operation}"
        )

    # ========================================================
    # FLAGS
    # ========================================================

    def get_flags(
        self,
    ) -> dict[str, bool]:
        """
        Return current ALU flags.
        """

        return {
            "zero": self.zero,
            "carry": self.carry,
            "negative": self.negative,
            "overflow": self.overflow,
        }

    # ========================================================
    # RESET
    # ========================================================

    def reset(self) -> None:
        """
        Reset ALU state.
        """

        self.result = 0x00

        self.zero = False

        self.carry = False

        self.negative = False

        self.overflow = False

    # ========================================================
    # DEBUG
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print ALU state.
        """

        print(
            "============= ALU ============="
        )

        print(
            f"Result   : "
            f"0x{self.result:02X}"
        )

        print(
            f"Zero     : "
            f"{self.zero}"
        )

        print(
            f"Carry    : "
            f"{self.carry}"
        )

        print(
            f"Negative : "
            f"{self.negative}"
        )

        print(
            f"Overflow : "
            f"{self.overflow}"
        )

        print(
            "==============================="
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "ALU",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    alu = ALU()

    print(
        "MiniCPU 8-bit ALU"
    )

    print()

    result = alu.add(
        0x10,
        0x20,
    )

    print(
        f"ADD: "
        f"0x10 + 0x20 = "
        f"0x{result:02X}"
    )

    result = alu.subtract(
        0x20,
        0x10,
    )

    print(
        f"SUB: "
        f"0x20 - 0x10 = "
        f"0x{result:02X}"
    )

    result = alu.bitwise_and(
        0xF0,
        0x0F,
    )

    print(
        f"AND: "
        f"0xF0 & 0x0F = "
        f"0x{result:02X}"
    )

    result = alu.bitwise_or(
        0xF0,
        0x0F,
    )

    print(
        f"OR: "
        f"0xF0 | 0x0F = "
        f"0x{result:02X}"
    )

    result = alu.bitwise_xor(
        0xFF,
        0x0F,
    )

    print(
        f"XOR: "
        f"0xFF ^ 0x0F = "
        f"0x{result:02X}"
    )

    result = alu.compare(
        0x10,
        0x10,
    )

    print(
        f"CMP: "
        f"0x10 - 0x10 = "
        f"0x{result:02X}"
    )

    alu.dump() you 
