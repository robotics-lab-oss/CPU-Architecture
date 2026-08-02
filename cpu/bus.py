"""
bus.py

MiniCPU 8-bit CPU Architecture
CPU Bus

Architecture:
    - 8-bit data bus
    - 8-bit address bus
    - 256-byte address space

Responsibilities:
    - Address transfer
    - Data transfer
    - Memory read
    - Memory write
    - Program loading
"""

from __future__ import annotations


class Bus:
    """
    MiniCPU system bus.

    The bus connects CPU components with memory.

    Data Bus:
        8-bit

    Address Bus:
        8-bit
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    DATA_WIDTH = 8
    ADDRESS_WIDTH = 8

    MIN_VALUE = 0x00
    MAX_VALUE = 0xFF

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        memory,
    ):
        """
        Initialize system bus.

        Args:
            memory:
                Memory instance connected to the bus.
        """

        if memory is None:
            raise ValueError(
                "Bus requires a memory instance."
            )

        self.memory = memory

        # Current address bus value
        self.address = 0x00

        # Current data bus value
        self.data = 0x00

        # Bus activity state
        self.read_active = False
        self.write_active = False

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    @classmethod
    def validate_address(
        cls,
        address: int,
    ) -> int:
        """
        Validate an 8-bit address.
        """

        if not isinstance(
            address,
            int,
        ):
            raise TypeError(
                "Bus address must be an integer."
            )

        if not (
            cls.MIN_VALUE
            <= address
            <= cls.MAX_VALUE
        ):
            raise ValueError(
                "Bus address must be "
                "8-bit."
            )

        return address

    # ========================================================
    # DATA VALIDATION
    # ========================================================

    @classmethod
    def validate_data(
        cls,
        data: int,
    ) -> int:
        """
        Validate an 8-bit data value.
        """

        if not isinstance(
            data,
            int,
        ):
            raise TypeError(
                "Bus data must be an integer."
            )

        if not (
            cls.MIN_VALUE
            <= data
            <= cls.MAX_VALUE
        ):
            raise ValueError(
                "Bus data must be "
                "8-bit."
            )

        return data

    # ========================================================
    # SET ADDRESS
    # ========================================================

    def set_address(
        self,
        address: int,
    ) -> None:
        """
        Put an address on the address bus.
        """

        self.address = (
            self.validate_address(
                address
            )
        )

    # ========================================================
    # GET ADDRESS
    # ========================================================

    def get_address(
        self,
    ) -> int:
        """
        Return current address bus value.
        """

        return self.address

    # ========================================================
    # SET DATA
    # ========================================================

    def set_data(
        self,
        data: int,
    ) -> None:
        """
        Put data on the data bus.
        """

        self.data = (
            self.validate_data(
                data
            )
        )

    # ========================================================
    # GET DATA
    # ========================================================

    def get_data(
        self,
    ) -> int:
        """
        Return current data bus value.
        """

        return self.data

    # ========================================================
    # MEMORY READ
    # ========================================================

    def read(
        self,
        address: int | None = None,
    ) -> int:
        """
        Read one byte from memory.

        If address is not provided,
        the current address bus value
        is used.
        """

        if address is not None:

            self.set_address(
                address
            )

        self.read_active = True

        self.write_active = False

        try:

            self.data = (
                self.memory.read(
                    self.address
                )
            )

            return self.data

        finally:

            self.read_active = False

    # ========================================================
    # MEMORY WRITE
    # ========================================================

    def write(
        self,
        address: int | None = None,
        data: int | None = None,
    ) -> None:
        """
        Write one byte to memory.

        If address is not provided,
        current address bus value is used.

        If data is not provided,
        current data bus value is used.
        """

        if address is not None:

            self.set_address(
                address
            )

        if data is not None:

            self.set_data(
                data
            )

        self.read_active = False

        self.write_active = True

        try:

            self.memory.write(
                self.address,
                self.data,
            )

        finally:

            self.write_active = False

    # ========================================================
    # TRANSFER
    # ========================================================

    def transfer(
        self,
        address: int,
    ) -> int:
        """
        Read data from a memory address
        and place it on the data bus.

        Returns:
            8-bit data.
        """

        return self.read(
            address
        )

    # ========================================================
    # LOAD PROGRAM
    # ========================================================

    def load_program(
        self,
        program: bytes,
        start_address: int = 0x00,
    ) -> None:
        """
        Load program bytes into memory.
        """

        if not isinstance(
            program,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Program must be bytes "
                "or bytearray."
            )

        self.memory.write_block(
            start_address,
            program,
        )

    # ========================================================
    # READ BLOCK
    # ========================================================

    def read_block(
        self,
        start_address: int,
        length: int,
    ) -> bytes:
        """
        Read a block of memory.
        """

        return self.memory.read_block(
            start_address,
            length,
        )

    # ========================================================
    # WRITE BLOCK
    # ========================================================

    def write_block(
        self,
        start_address: int,
        data: bytes,
    ) -> None:
        """
        Write a block of bytes to memory.
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        self.memory.write_block(
            start_address,
            data,
        )

    # ========================================================
    # CLEAR BUS
    # ========================================================

    def clear(
        self,
    ) -> None:
        """
        Clear current bus values.
        """

        self.address = 0x00

        self.data = 0x00

        self.read_active = False

        self.write_active = False

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset bus state.
        """

        self.clear()

    # ========================================================
    # BUS STATUS
    # ========================================================

    def is_idle(
        self,
    ) -> bool:
        """
        Return True if bus is idle.
        """

        return not (
            self.read_active
            or self.write_active
        )

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> dict:
        """
        Return current bus state.
        """

        return {
            "address": self.address,
            "data": self.data,
            "read_active": (
                self.read_active
            ),
            "write_active": (
                self.write_active
            ),
        }

    # ========================================================
    # LOAD SNAPSHOT
    # ========================================================

    def load_snapshot(
        self,
        state: dict,
    ) -> None:
        """
        Restore bus state.
        """

        if not isinstance(
            state,
            dict,
        ):
            raise TypeError(
                "Bus state must be a dictionary."
            )

        self.set_address(
            state.get(
                "address",
                0x00,
            )
        )

        self.set_data(
            state.get(
                "data",
                0x00,
            )
        )

        self.read_active = bool(
            state.get(
                "read_active",
                False,
            )
        )

        self.write_active = bool(
            state.get(
                "write_active",
                False,
            )
        )

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print current bus state.
        """

        print(
            "============= BUS ============="
        )

        print(
            f"Address Bus : "
            f"0x{self.address:02X}"
        )

        print(
            f"Data Bus    : "
            f"0x{self.data:02X}"
        )

        print(
            f"Read Active : "
            f"{self.read_active}"
        )

        print(
            f"Write Active: "
            f"{self.write_active}"
        )

        print(
            f"Bus Idle    : "
            f"{self.is_idle()}"
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
        Return readable bus state.
        """

        return (
            f"Bus("
            f"address=0x{self.address:02X}, "
            f"data=0x{self.data:02X}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Bus",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    from .memory import Memory

    memory = Memory()

    bus = Bus(
        memory
    )

    print(
        "MiniCPU 8-bit System Bus"
    )

    print()

    # Write through bus
    bus.write(
        0x10,
        0x42,
    )

    print(
        "After WRITE:"
    )

    bus.dump()

    print()

    # Read through bus
    value = bus.read(
        0x10
    )

    print(
        f"Read Value: "
        f"0x{value:02X}"
    )

    print()

    print(
        "After READ:"
    )

    bus.dump()
