"""
memory.py

MiniCPU 8-bit CPU Architecture
Memory Unit

Architecture:
    - 8-bit address bus
    - 8-bit data bus
    - 256 addressable bytes
    - Address range: 0x00 - 0xFF
    - Data range:    0x00 - 0xFF
"""

from __future__ import annotations


class Memory:
    """
    MiniCPU memory model.

    Each memory location stores exactly
    one 8-bit byte.

    Default memory:

        256 bytes

    Address range:

        0x00 - 0xFF
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    ADDRESS_WIDTH = 8
    DATA_WIDTH = 8

    MIN_ADDRESS = 0x00
    MAX_ADDRESS = 0xFF

    MIN_VALUE = 0x00
    MAX_VALUE = 0xFF

    DEFAULT_SIZE = 256

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        size: int = DEFAULT_SIZE,
    ):
        """
        Initialize memory.

        Args:
            size:
                Number of addressable bytes.

        Default:
            256 bytes
        """

        if not isinstance(
            size,
            int,
        ):
            raise TypeError(
                "Memory size must be an integer."
            )

        if size <= 0:
            raise ValueError(
                "Memory size must be greater than zero."
            )

        if size > (
            self.MAX_ADDRESS + 1
        ):
            raise ValueError(
                "8-bit address space supports "
                "maximum 256 bytes."
            )

        self.size = size

        self.data = bytearray(
            size
        )

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    def validate_address(
        self,
        address: int,
    ) -> int:
        """
        Validate a memory address.

        Valid range:

            0x00 - 0xFF

        Also checks the configured memory size.
        """

        if not isinstance(
            address,
            int,
        ):
            raise TypeError(
                "Memory address must be an integer."
            )

        if not (
            self.MIN_ADDRESS
            <= address
            <= self.MAX_ADDRESS
        ):
            raise ValueError(
                f"Address must be between "
                f"0x{self.MIN_ADDRESS:02X} and "
                f"0x{self.MAX_ADDRESS:02X}."
            )

        if address >= self.size:
            raise IndexError(
                f"Address 0x{address:02X} "
                f"is outside configured memory "
                f"size ({self.size} bytes)."
            )

        return address

    # ========================================================
    # VALUE VALIDATION
    # ========================================================

    @classmethod
    def validate_value(
        cls,
        value: int,
    ) -> int:
        """
        Validate an 8-bit memory value.
        """

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "Memory value must be an integer."
            )

        if not (
            cls.MIN_VALUE
            <= value
            <= cls.MAX_VALUE
        ):
            raise ValueError(
                f"Memory value must be between "
                f"0x{cls.MIN_VALUE:02X} and "
                f"0x{cls.MAX_VALUE:02X}."
            )

        return value

    # ========================================================
    # READ BYTE
    # ========================================================

    def read(
        self,
        address: int,
    ) -> int:
        """
        Read one byte from memory.

        Returns:

            0x00 - 0xFF
        """

        address = self.validate_address(
            address
        )

        return self.data[
            address
        ]

    # ========================================================
    # WRITE BYTE
    # ========================================================

    def write(
        self,
        address: int,
        value: int,
    ) -> None:
        """
        Write one 8-bit byte to memory.
        """

        address = self.validate_address(
            address
        )

        value = self.validate_value(
            value
        )

        self.data[
            address
        ] = value

    # ========================================================
    # READ MULTIPLE BYTES
    # ========================================================

    def read_block(
        self,
        start_address: int,
        length: int,
    ) -> bytes:
        """
        Read multiple consecutive bytes.
        """

        if not isinstance(
            length,
            int,
        ):
            raise TypeError(
                "Length must be an integer."
            )

        if length < 0:
            raise ValueError(
                "Length cannot be negative."
            )

        if length == 0:
            return b""

        start_address = (
            self.validate_address(
                start_address
            )
        )

        end_address = (
            start_address
            + length
        )

        if end_address > self.size:
            raise IndexError(
                "Memory block exceeds "
                "available memory."
            )

        return bytes(
            self.data[
                start_address:end_address
            ]
        )

    # ========================================================
    # WRITE MULTIPLE BYTES
    # ========================================================

    def write_block(
        self,
        start_address: int,
        data: bytes,
    ) -> None:
        """
        Write multiple bytes to memory.
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        if len(data) == 0:
            return

        start_address = (
            self.validate_address(
                start_address
            )
        )

        end_address = (
            start_address
            + len(data)
        )

        if end_address > self.size:
            raise IndexError(
                "Memory block exceeds "
                "available memory."
            )

        self.data[
            start_address:end_address
        ] = data

    # ========================================================
    # LOAD PROGRAM
    # ========================================================

    def load(
        self,
        program: bytes,
        start_address: int = 0x00,
    ) -> None:
        """
        Load a binary program into memory.
        """

        self.write_block(
            start_address,
            program,
        )

    # ========================================================
    # CLEAR MEMORY
    # ========================================================

    def clear(
        self,
        start_address: int = 0x00,
        length: int | None = None,
    ) -> None:
        """
        Clear a memory region.

        If length is None, clears from
        start_address to the end of memory.
        """

        start_address = (
            self.validate_address(
                start_address
            )
        )

        if length is None:

            length = (
                self.size
                - start_address
            )

        if not isinstance(
            length,
            int,
        ):
            raise TypeError(
                "Length must be an integer."
            )

        if length < 0:
            raise ValueError(
                "Length cannot be negative."
            )

        end_address = (
            start_address
            + length
        )

        if end_address > self.size:
            raise IndexError(
                "Clear range exceeds memory."
            )

        for address in range(
            start_address,
            end_address,
        ):
            self.data[
                address
            ] = 0x00

    # ========================================================
    # RESET
    # ========================================================

    def reset(self) -> None:
        """
        Reset all memory locations to zero.
        """

        self.data = bytearray(
            self.size
        )

    # ========================================================
    # CHECK ADDRESS
    # ========================================================

    def contains(
        self,
        address: int,
    ) -> bool:
        """
        Return True if address is valid
        for the configured memory.
        """

        if not isinstance(
            address,
            int,
        ):
            return False

        return (
            0
            <= address
            < self.size
        )

    # ========================================================
    # ITERATE MEMORY
    # ========================================================

    def iter_bytes(
        self,
    ):
        """
        Iterate over all memory bytes.

        Yields:

            (address, value)
        """

        for address in range(
            self.size
        ):
            yield (
                address,
                self.data[address],
            )

    # ========================================================
    # DUMP MEMORY
    # ========================================================

    def dump(
        self,
        start_address: int = 0x00,
        length: int = 16,
    ) -> None:
        """
        Print a hexadecimal memory dump.
        """

        block = self.read_block(
            start_address,
            length,
        )

        print(
            "========== MEMORY DUMP =========="
        )

        for offset in range(
            0,
            len(block),
            16,
        ):

            address = (
                start_address
                + offset
            )

            chunk = block[
                offset:offset + 16
            ]

            hex_values = " ".join(
                f"{byte:02X}"
                for byte in chunk
            )

            print(
                f"{address:02X}: "
                f"{hex_values}"
            )

        print(
            "================================="
        )

    # ========================================================
    # EXPORT
    # ========================================================

    def to_bytes(
        self,
    ) -> bytes:
        """
        Return complete memory contents.
        """

        return bytes(
            self.data
        )

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __len__(
        self,
    ) -> int:
        """
        Return memory size.
        """

        return self.size

    def __repr__(
        self,
    ) -> str:
        """
        Return readable memory information.
        """

        return (
            f"Memory("
            f"size={self.size}, "
            f"address_width="
            f"{self.ADDRESS_WIDTH}, "
            f"data_width="
            f"{self.DATA_WIDTH}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Memory",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    memory = Memory()

    print(
        "MiniCPU 8-bit Memory"
    )

    print(
        f"Memory Size: "
        f"{len(memory)} bytes"
    )

    print(
        f"Address Range: "
        f"0x00 - 0x{memory.size - 1:02X}"
    )

    print()

    # Write single byte
    memory.write(
        0x10,
        0x42,
    )

    # Read single byte
    value = memory.read(
        0x10
    )

    print(
        f"Memory[0x10] = "
        f"0x{value:02X}"
    )

    # Write program
    program = bytes(
        [
            0x10,
            0x42,
            0xF0,
        ]
    )

    memory.load(
        program,
        0x00,
    )

    print()

    print(
        "Loaded Program:"
    )

    memory.dump(
        0x00,
        16,
      )
