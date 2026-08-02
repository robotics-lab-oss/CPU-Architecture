"""
flags.py

MiniCPU 8-bit CPU Architecture
CPU Status Flags

Flags:

    Z - Zero
    C - Carry
    N - Negative
    V - Overflow

These flags are updated by the ALU and used
by conditional instructions such as JZ.
"""

from __future__ import annotations


class Flags:
    """
    Central CPU status flag register.

    Flags:

        Z (Zero)
            Set when the result is zero.

        C (Carry)
            Set when an arithmetic operation
            produces a carry.

        N (Negative)
            Set when bit 7 of the result is 1.

        V (Overflow)
            Set when signed arithmetic overflows.
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    ZERO = "Z"
    CARRY = "C"
    NEGATIVE = "N"
    OVERFLOW = "V"

    FLAG_NAMES = (
        ZERO,
        CARRY,
        NEGATIVE,
        OVERFLOW,
    )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):
        """
        Initialize all flags to False.
        """

        self.reset()

    # ========================================================
    # RESET
    # ========================================================

    def reset(self) -> None:
        """
        Clear all CPU flags.
        """

        self.Z = False
        self.C = False
        self.N = False
        self.V = False

    # ========================================================
    # NORMALIZE FLAG NAME
    # ========================================================

    @classmethod
    def normalize_name(
        cls,
        name: str,
    ) -> str:
        """
        Normalize a flag name.

        Examples:

            "z" -> "Z"
            "c" -> "C"
            "N" -> "N"
        """

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Flag name must be a string."
            )

        name = name.strip().upper()

        if name not in cls.FLAG_NAMES:
            raise ValueError(
                f"Unknown CPU flag: {name}"
            )

        return name

    # ========================================================
    # GET FLAG
    # ========================================================

    def get(
        self,
        name: str,
    ) -> bool:
        """
        Read a flag.

        Example:

            flags.get("Z")
        """

        name = self.normalize_name(
            name
        )

        return bool(
            getattr(
                self,
                name,
            )
        )

    # ========================================================
    # SET FLAG
    # ========================================================

    def set(
        self,
        name: str,
        value: bool,
    ) -> None:
        """
        Set a flag.

        Example:

            flags.set("Z", True)
        """

        name = self.normalize_name(
            name
        )

        if not isinstance(
            value,
            bool,
        ):
            raise TypeError(
                "Flag value must be boolean."
            )

        setattr(
            self,
            name,
            value,
        )

    # ========================================================
    # SET ZERO
    # ========================================================

    def set_zero(
        self,
        value: bool,
    ) -> None:
        """
        Set Zero flag.
        """

        self.Z = bool(
            value
        )

    # ========================================================
    # SET CARRY
    # ========================================================

    def set_carry(
        self,
        value: bool,
    ) -> None:
        """
        Set Carry flag.
        """

        self.C = bool(
            value
        )

    # ========================================================
    # SET NEGATIVE
    # ========================================================

    def set_negative(
        self,
        value: bool,
    ) -> None:
        """
        Set Negative flag.
        """

        self.N = bool(
            value
        )

    # ========================================================
    # SET OVERFLOW
    # ========================================================

    def set_overflow(
        self,
        value: bool,
    ) -> None:
        """
        Set Overflow flag.
        """

        self.V = bool(
            value
        )

    # ========================================================
    # UPDATE FROM RESULT
    # ========================================================

    def update_from_result(
        self,
        result: int,
        *,
        carry: bool = False,
        overflow: bool = False,
    ) -> None:
        """
        Update flags from an 8-bit ALU result.

        Args:

            result:
                8-bit operation result.

            carry:
                Carry flag value.

            overflow:
                Overflow flag value.
        """

        if not isinstance(
            result,
            int,
        ):
            raise TypeError(
                "Result must be an integer."
            )

        if not 0 <= result <= 0xFF:
            raise ValueError(
                "Result must be in 8-bit range."
            )

        self.Z = (
            result == 0
        )

        self.N = bool(
            result & 0x80
        )

        self.C = bool(
            carry
        )

        self.V = bool(
            overflow
        )

    # ========================================================
    # UPDATE FROM ALU
    # ========================================================

    def update_from_alu(
        self,
        alu,
    ) -> None:
        """
        Copy flags from an ALU instance.

        Expected ALU attributes:

            result
            zero
            carry
            negative
            overflow
        """

        self.Z = bool(
            alu.zero
        )

        self.C = bool(
            alu.carry
        )

        self.N = bool(
            alu.negative
        )

        self.V = bool(
            alu.overflow
        )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(
        self,
        name: str,
    ) -> None:
        """
        Clear one flag.
        """

        self.set(
            name,
            False,
        )

    # ========================================================
    # SET
    # ========================================================

    def set_all(
        self,
        *,
        zero: bool = False,
        carry: bool = False,
        negative: bool = False,
        overflow: bool = False,
    ) -> None:
        """
        Set all flags at once.
        """

        self.Z = bool(
            zero
        )

        self.C = bool(
            carry
        )

        self.N = bool(
            negative
        )

        self.V = bool(
            overflow
        )

    # ========================================================
    # GET ALL FLAGS
    # ========================================================

    def get_all(
        self,
    ) -> dict[str, bool]:
        """
        Return all flags.
        """

        return {
            "Z": self.Z,
            "C": self.C,
            "N": self.N,
            "V": self.V,
        }

    # ========================================================
    # STATUS BYTE
    # ========================================================

    def to_byte(
        self,
    ) -> int:
        """
        Convert flags to an 8-bit status byte.

        Layout:

            Bit 7 : Z
            Bit 6 : C
            Bit 5 : N
            Bit 4 : V
            Bit 3-0 : Reserved

        Example:

            Z = True
            C = False
            N = False
            V = False

            Result = 0x80
        """

        value = 0x00

        if self.Z:
            value |= 0x80

        if self.C:
            value |= 0x40

        if self.N:
            value |= 0x20

        if self.V:
            value |= 0x10

        return value

    # ========================================================
    # LOAD STATUS BYTE
    # ========================================================

    def from_byte(
        self,
        value: int,
    ) -> None:
        """
        Load flags from an 8-bit status byte.
        """

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "Status value must be an integer."
            )

        if not 0 <= value <= 0xFF:
            raise ValueError(
                "Status value must be 8-bit."
            )

        self.Z = bool(
            value & 0x80
        )

        self.C = bool(
            value & 0x40
        )

        self.N = bool(
            value & 0x20
        )

        self.V = bool(
            value & 0x10
        )

    # ========================================================
    # CONDITION: ZERO
    # ========================================================

    def is_zero(
        self,
    ) -> bool:
        """
        Return True if Zero flag is set.
        """

        return self.Z

    # ========================================================
    # CONDITION: CARRY
    # ========================================================

    def is_carry(
        self,
    ) -> bool:
        """
        Return True if Carry flag is set.
        """

        return self.C

    # ========================================================
    # CONDITION: NEGATIVE
    # ========================================================

    def is_negative(
        self,
    ) -> bool:
        """
        Return True if Negative flag is set.
        """

        return self.N

    # ========================================================
    # CONDITION: OVERFLOW
    # ========================================================

    def is_overflow(
        self,
    ) -> bool:
        """
        Return True if Overflow flag is set.
        """

        return self.V

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> dict[str, bool]:
        """
        Return a copy of the current flags.
        """

        return self.get_all()

    # ========================================================
    # LOAD SNAPSHOT
    # ========================================================

    def load_snapshot(
        self,
        state: dict[str, bool],
    ) -> None:
        """
        Restore flags from a dictionary.
        """

        if not isinstance(
            state,
            dict,
        ):
            raise TypeError(
                "Flag state must be a dictionary."
            )

        self.set_all(
            zero=state.get(
                "Z",
                False,
            ),
            carry=state.get(
                "C",
                False,
            ),
            negative=state.get(
                "N",
                False,
            ),
            overflow=state.get(
                "V",
                False,
            ),
        )

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print CPU flag state.
        """

        print(
            "=========== FLAGS ============"
        )

        print(
            f"Z (Zero)     : {self.Z}"
        )

        print(
            f"C (Carry)    : {self.C}"
        )

        print(
            f"N (Negative) : {self.N}"
        )

        print(
            f"V (Overflow) : {self.V}"
        )

        print(
            f"Status Byte  : "
            f"0x{self.to_byte():02X}"
        )

        print(
            "=============================="
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable flag state.
        """

        return (
            f"Flags("
            f"Z={self.Z}, "
            f"C={self.C}, "
            f"N={self.N}, "
            f"V={self.V}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Flags",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    flags = Flags()

    print(
        "MiniCPU 8-bit CPU Flags"
    )

    print()

    flags.update_from_result(
        0x00,
        carry=False,
        overflow=False,
    )

    flags.dump()

    print()

    flags.update_from_result(
        0x80,
        carry=True,
        overflow=False,
    )

    flags.dump()

    print()

    status = flags.to_byte()

    print(
        f"Status Byte: "
        f"0x{status:02X}"
    )

    flags.reset()

    flags.from_byte(
        status
    )

    print(
        "Restored:"
    )

    flags.dump()
