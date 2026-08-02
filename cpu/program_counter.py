"""
program_counter.py

MiniCPU 8-bit CPU Architecture
Program Counter (PC)

The Program Counter stores the address of the
next instruction to be fetched.

Architecture:
    - 8-bit address width
    - Address range: 0x00 - 0xFF
    - Wrap-around on increment/decrement
"""


from __future__ import annotations


class ProgramCounter:
    """
    8-bit Program Counter.

    The PC points to the memory address of the
    next instruction.

    Example:

        PC = 0x00

        Fetch instruction
            ↓

        PC increments
            ↓

        PC = 0x01
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    WIDTH = 8

    MIN_ADDRESS = 0x00
    MAX_ADDRESS = 0xFF

    ADDRESS_SPACE = 0x100

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        address: int = 0x00,
    ):
        """
        Initialize Program Counter.

        Args:
            address:
                Initial program counter address.
        """

        self.value = self.validate_address(
            address
        )

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    @classmethod
    def validate_address(
        cls,
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
                "Program counter address "
                "must be an integer."
            )

        if not (
            cls.MIN_ADDRESS
            <= address
            <= cls.MAX_ADDRESS
        ):
            raise ValueError(
                f"Program counter address must "
                f"be between "
                f"0x{cls.MIN_ADDRESS:02X} and "
                f"0x{cls.MAX_ADDRESS:02X}."
            )

        return address

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
    ) -> int:
        """
        Return current program counter value.
        """

        return self.value

    # ========================================================
    # SET
    # ========================================================

    def set(
        self,
        address: int,
    ) -> None:
        """
        Set Program Counter to an address.
        """

        self.value = (
            self.validate_address(
                address
            )
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        address: int = 0x00,
    ) -> None:
        """
        Reset Program Counter.

        Default:

            0x00
        """

        self.set(
            address
        )

    # ========================================================
    # INCREMENT
    # ========================================================

    def increment(
        self,
        amount: int = 1,
    ) -> int:
        """
        Increment Program Counter.

        The value wraps around at 0xFF.

        Example:

            0xFF + 1 = 0x00
        """

        if not isinstance(
            amount,
            int,
        ):
            raise TypeError(
                "Increment amount must "
                "be an integer."
            )

        self.value = (
            self.value
            + amount
        ) & self.MAX_ADDRESS

        return self.value

    # ========================================================
    # DECREMENT
    # ========================================================

    def decrement(
        self,
        amount: int = 1,
    ) -> int:
        """
        Decrement Program Counter.

        The value wraps around at 0x00.

        Example:

            0x00 - 1 = 0xFF
        """

        if not isinstance(
            amount,
            int,
        ):
            raise TypeError(
                "Decrement amount must "
                "be an integer."
            )

        self.value = (
            self.value
            - amount
        ) & self.MAX_ADDRESS

        return self.value

    # ========================================================
    # ADD OFFSET
    # ========================================================

    def add_offset(
        self,
        offset: int,
    ) -> int:
        """
        Add a signed or unsigned offset.

        Example:

            PC = 0x10
            offset = 0x05

            PC = 0x15
        """

        if not isinstance(
            offset,
            int,
        ):
            raise TypeError(
                "Offset must be an integer."
            )

        self.value = (
            self.value
            + offset
        ) & self.MAX_ADDRESS

        return self.value

    # ========================================================
    # JUMP
    # ========================================================

    def jump(
        self,
        address: int,
    ) -> int:
        """
        Jump directly to an address.

        This is equivalent to setting PC.
        """

        self.set(
            address
        )

        return self.value

    # ========================================================
    # RELATIVE JUMP
    # ========================================================

    def relative_jump(
        self,
        offset: int,
    ) -> int:
        """
        Perform a relative jump.

        Example:

            PC = 0x20
            offset = +5

            PC = 0x25
        """

        return self.add_offset(
            offset
        )

    # ========================================================
    # CURRENT ADDRESS
    # ========================================================

    @property
    def address(
        self,
    ) -> int:
        """
        Return current PC address.
        """

        return self.value

    # ========================================================
    # CHECK ADDRESS
    # ========================================================

    def is_at(
        self,
        address: int,
    ) -> bool:
        """
        Return True if PC points to address.
        """

        address = (
            self.validate_address(
                address
            )
        )

        return (
            self.value
            == address
        )

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> int:
        """
        Return current PC value.

        Useful for saving CPU state.
        """

        return self.value

    # ========================================================
    # LOAD SNAPSHOT
    # ========================================================

    def load_snapshot(
        self,
        value: int,
    ) -> None:
        """
        Restore Program Counter state.
        """

        self.set(
            value
        )

    # ========================================================
    # DEBUG
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print Program Counter state.
        """

        print(
            "======= PROGRAM COUNTER ======="
        )

        print(
            f"PC: "
            f"0x{self.value:02X}"
        )

        print(
            f"Decimal: "
            f"{self.value}"
        )

        print(
            "==============================="
        )

    # ========================================================
    # INTEGER CONVERSION
    # ========================================================

    def __int__(
        self,
    ) -> int:
        """
        Convert Program Counter to integer.
        """

        return self.value

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable PC state.
        """

        return (
            f"ProgramCounter("
            f"0x{self.value:02X}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "ProgramCounter",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    pc = ProgramCounter()

    print(
        "MiniCPU 8-bit Program Counter"
    )

    print()

    print(
        f"Initial PC: "
        f"0x{pc.get():02X}"
    )

    pc.increment()

    print(
        f"After INC: "
        f"0x{pc.get():02X}"
    )

    pc.set(
        0x10
    )

    print(
        f"After SET: "
        f"0x{pc.get():02X}"
    )

    pc.increment(
        5
    )

    print(
        f"After INC 5: "
        f"0x{pc.get():02X}"
    )

    pc.relative_jump(
        -2
    )

    print(
        f"After Relative Jump -2: "
        f"0x{pc.get():02X}"
    )

    pc.jump(
        0xFF
    )

    print(
        f"Before Wrap: "
        f"0x{pc.get():02X}"
    )

    pc.increment()

    print(
        f"After Wrap: "
        f"0x{pc.get():02X}"
    )

    pc.dump()
