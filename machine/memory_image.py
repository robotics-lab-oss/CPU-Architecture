"""
memory_image.py

MiniCPU 8-bit Memory Image

Represents the complete 256-byte address space
of the MiniCPU architecture.

Features:
    - 256-byte memory image
    - 8-bit addresses
    - Read / write bytes
    - Load programs
    - Fill memory
    - Clear memory
    - Export raw bytes
    - Import raw bytes
    - Export HEX
    - Import HEX
    - Memory dump
    - Address validation
    - Range validation

Architecture:
    Data width:
        8-bit

    Address width:
        8-bit

    Address range:
        0x00 - 0xFF

    Memory size:
        256 bytes
"""

from __future__ import annotations

from pathlib import Path

from .binary_format import BinaryFormat
from .hex_format import HexFormat


class MemoryImage:
    """
    Complete 256-byte MiniCPU memory image.

    Memory layout:

        0x00
        0x01
        0x02
        ...
        0xFE
        0xFF

    Every memory location contains
    one 8-bit value.
    """

    # ========================================================
    # ARCHITECTURE CONSTANTS
    # ========================================================

    DATA_WIDTH = 8

    ADDRESS_WIDTH = 8

    MEMORY_SIZE = 256

    MIN_ADDRESS = 0x00

    MAX_ADDRESS = 0xFF

    MIN_BYTE = 0x00

    MAX_BYTE = 0xFF

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        fill_value: int = 0x00,
    ):
        """
        Create a new 256-byte memory image.

        By default all memory is initialized
        to 0x00.
        """

        self.validate_byte(
            fill_value,
            "Fill value",
        )

        self.data = bytearray(
            [
                fill_value
            ]
            * self.MEMORY_SIZE
        )

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    @classmethod
    def validate_address(
        cls,
        address: int,
        name: str = "Address",
    ) -> int:
        """
        Validate an 8-bit memory address.

        Valid range:

            0x00 - 0xFF
        """

        if not isinstance(
            address,
            int,
        ):
            raise TypeError(
                f"{name} must be an integer."
            )

        if not (
            cls.MIN_ADDRESS
            <= address
            <= cls.MAX_ADDRESS
        ):
            raise ValueError(
                f"{name} must be between "
                f"0x00 and 0xFF."
            )

        return address

    # ========================================================
    # BYTE VALIDATION
    # ========================================================

    @classmethod
    def validate_byte(
        cls,
        value: int,
        name: str = "Value",
    ) -> int:
        """
        Validate an 8-bit memory value.
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
    # RANGE VALIDATION
    # ========================================================

    @classmethod
    def validate_range(
        cls,
        start_address: int,
        size: int,
    ) -> tuple[int, int]:
        """
        Validate a memory address range.

        Example:

            start = 0x10
            size  = 4

        Valid addresses:

            0x10
            0x11
            0x12
            0x13
        """

        cls.validate_address(
            start_address,
            "Start address",
        )

        if not isinstance(
            size,
            int,
        ):
            raise TypeError(
                "Size must be an integer."
            )

        if size < 0:
            raise ValueError(
                "Size cannot be negative."
            )

        if (
            start_address
            + size
            > cls.MEMORY_SIZE
        ):
            raise ValueError(
                "Memory range exceeds "
                "256-byte address space."
            )

        return (
            start_address,
            size,
        )

    # ========================================================
    # READ BYTE
    # ========================================================

    def read(
        self,
        address: int,
    ) -> int:
        """
        Read one byte from memory.

        Example:

            value = memory.read(0x10)
        """

        self.validate_address(
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
        Write one byte to memory.

        Example:

            memory.write(
                0x10,
                0x42
            )
        """

        self.validate_address(
            address
        )

        self.validate_byte(
            value
        )

        self.data[
            address
        ] = value

    # ========================================================
    # READ RANGE
    # ========================================================

    def read_range(
        self,
        start_address: int,
        size: int,
    ) -> bytes:
        """
        Read multiple bytes from memory.
        """

        self.validate_range(
            start_address,
            size,
        )

        return bytes(
            self.data[
                start_address:
                start_address + size
            ]
        )

    # ========================================================
    # WRITE RANGE
    # ========================================================

    def write_range(
        self,
        start_address: int,
        data: bytes | bytearray,
    ) -> int:
        """
        Write multiple bytes into memory.

        Returns:
            Number of bytes written.
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        self.validate_range(
            start_address,
            len(data),
        )

        self.data[
            start_address:
            start_address + len(data)
        ] = data

        return len(data)

    # ========================================================
    # LOAD PROGRAM
    # ========================================================

    def load(
        self,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> int:
        """
        Load machine code into memory.

        Example:

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
        """

        return self.write_range(
            start_address,
            data,
        )

    # ========================================================
    # LOAD RAW BINARY FILE
    # ========================================================

    def load_binary_file(
        self,
        path: str | Path,
        start_address: int = 0x00,
    ) -> int:
        """
        Load a raw binary file into memory.
        """

        path = Path(
            path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Binary file not found: "
                f"{path}"
            )

        if not path.is_file():

            raise ValueError(
                f"Path is not a file: "
                f"{path}"
            )

        data = path.read_bytes()

        return self.load(
            data,
            start_address,
        )

    # ========================================================
    # LOAD HEX FILE
    # ========================================================

    def load_hex_file(
        self,
        path: str | Path,
        start_address: int = 0x00,
    ) -> int:
        """
        Load a plain HEX file into memory.
        """

        path = Path(
            path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"HEX file not found: "
                f"{path}"
            )

        text = path.read_text(
            encoding="utf-8",
        )

        data = (
            HexFormat.hex_to_bytes(
                text
            )
        )

        return self.load(
            data,
            start_address,
        )

    # ========================================================
    # LOAD INTEL HEX FILE
    # ========================================================

    def load_intel_hex_file(
        self,
        path: str | Path,
    ) -> int:
        """
        Load Intel HEX data into memory.

        Addresses are obtained from the
        Intel HEX records.
        """

        path = Path(
            path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Intel HEX file not found: "
                f"{path}"
            )

        text = path.read_text(
            encoding="utf-8",
        )

        parsed = (
            HexFormat.parse_intel_hex(
                text
            )
        )

        data = parsed[
            "data"
        ]

        start_address = parsed[
            "start_address"
        ]

        return self.load(
            data,
            start_address,
        )

    # ========================================================
    # FILL MEMORY
    # ========================================================

    def fill(
        self,
        value: int = 0x00,
    ) -> None:
        """
        Fill complete memory with one byte value.

        Example:

            memory.fill(0xFF)
        """

        self.validate_byte(
            value,
            "Fill value",
        )

        self.data = bytearray(
            [
                value
            ]
            * self.MEMORY_SIZE
        )

    # ========================================================
    # CLEAR MEMORY
    # ========================================================

    def clear(
        self,
        value: int = 0x00,
    ) -> None:
        """
        Clear complete memory.

        Default:

            0x00
        """

        self.fill(
            value
        )

    # ========================================================
    # RESET MEMORY
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset complete memory to 0x00.
        """

        self.clear(
            0x00
        )

    # ========================================================
    # EXPORT BYTES
    # ========================================================

    def to_bytes(
        self,
    ) -> bytes:
        """
        Return complete memory as bytes.

        Always returns exactly 256 bytes.
        """

        return bytes(
            self.data
        )

    # ========================================================
    # EXPORT BYTEARRAY
    # ========================================================

    def to_bytearray(
        self,
    ) -> bytearray:
        """
        Return a copy of memory as bytearray.
        """

        return bytearray(
            self.data
        )

    # ========================================================
    # IMPORT BYTES
    # ========================================================

    @classmethod
    def from_bytes(
        cls,
        data: bytes | bytearray,
        fill_value: int = 0x00,
    ) -> "MemoryImage":
        """
        Create memory image from raw bytes.

        Data is loaded starting at 0x00.
        """

        image = cls(
            fill_value
        )

        image.load(
            data,
            0x00,
        )

        return image

    # ========================================================
    # EXPORT PLAIN HEX
    # ========================================================

    def to_hex(
        self,
        include_unused: bool = True,
    ) -> str:
        """
        Convert memory to plain HEX.

        By default all 256 bytes are exported.

        If include_unused is False,
        trailing 0x00 bytes are removed.
        """

        data = self.to_bytes()

        if not include_unused:

            end = len(data)

            while (
                end > 0
                and data[
                    end - 1
                ] == 0x00
            ):

                end -= 1

            data = data[
                :end
            ]

        return HexFormat.bytes_to_hex(
            data
        )

    # ========================================================
    # EXPORT INTEL HEX
    # ========================================================

    def to_intel_hex(
        self,
        start_address: int = 0x00,
        size: int | None = None,
        record_size: int = 16,
    ) -> str:
        """
        Export memory as Intel HEX.

        Args:

            start_address:
                First memory address.

            size:
                Number of bytes to export.

            record_size:
                Maximum bytes per HEX record.
        """

        if size is None:

            size = (
                self.MEMORY_SIZE
                - start_address
            )

        data = self.read_range(
            start_address,
            size,
        )

        return HexFormat.create_intel_hex(
            data,
            start_address,
            record_size,
        )

    # ========================================================
    # WRITE BINARY FILE
    # ========================================================

    def write_binary_file(
        self,
        path: str | Path,
        include_unused: bool = True,
    ) -> Path:
        """
        Write memory to a raw binary file.

        By default exactly 256 bytes are written.
        """

        data = self.to_bytes()

        if not include_unused:

            end = len(data)

            while (
                end > 0
                and data[
                    end - 1
                ] == 0x00
            ):

                end -= 1

            data = data[
                :end
            ]

        path = Path(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            data
        )

        return path

    # ========================================================
    # WRITE HEX FILE
    # ========================================================

    def write_hex_file(
        self,
        path: str | Path,
        include_unused: bool = False,
    ) -> Path:
        """
        Write memory as plain HEX text.
        """

        text = self.to_hex(
            include_unused
        )

        path = Path(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            text + "\n",
            encoding="utf-8",
        )

        return path

    # ========================================================
    # WRITE INTEL HEX FILE
    # ========================================================

    def write_intel_hex_file(
        self,
        path: str | Path,
        start_address: int = 0x00,
        size: int | None = None,
        record_size: int = 16,
    ) -> Path:
        """
        Write memory as Intel HEX.
        """

        text = self.to_intel_hex(
            start_address,
            size,
            record_size,
        )

        path = Path(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            text + "\n",
            encoding="utf-8",
        )

        return path

    # ========================================================
    # MEMORY DUMP
    # ========================================================

    def dump(
        self,
        start_address: int = 0x00,
        size: int = 256,
        columns: int = 16,
    ) -> None:
        """
        Print a hexadecimal memory dump.

        Example:

            0000: 10 42 C0 F0 00 00 ...
        """

        self.validate_range(
            start_address,
            size,
        )

        if not isinstance(
            columns,
            int,
        ):
            raise TypeError(
                "Columns must be an integer."
            )

        if columns <= 0:
            raise ValueError(
                "Columns must be greater "
                "than zero."
            )

        data = self.read_range(
            start_address,
            size,
        )

        for offset in range(
            0,
            len(data),
            columns,
        ):

            chunk = data[
                offset:
                offset + columns
            ]

            address = (
                start_address
                + offset
            )

            hex_data = " ".join(
                f"{byte:02X}"
                for byte in chunk
            )

            print(
                f"{address:04X}: "
                f"{hex_data}"
            )

    # ========================================================
    # ITERATION
    # ========================================================

    def __iter__(
        self,
    ):
        """
        Iterate over all 256 memory bytes.
        """

        return iter(
            self.data
        )

    # ========================================================
    # LENGTH
    # ========================================================

    def __len__(
        self,
    ) -> int:
        """
        Return memory size.

        Always:

            256
        """

        return self.MEMORY_SIZE

    # ========================================================
    # INDEX ACCESS
    # ========================================================

    def __getitem__(
        self,
        address: int,
    ) -> int:
        """
        Allow:

            memory[0x10]
        """

        return self.read(
            address
        )

    # ========================================================
    # INDEX WRITE
    # ========================================================

    def __setitem__(
        self,
        address: int,
        value: int,
    ) -> None:
        """
        Allow:

            memory[0x10] = 0x42
        """

        self.write(
            address,
            value,
        )

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return memory image information.
        """

        return (
            "MemoryImage("
            "size=256, "
            "data_width=8, "
            "address_width=8"
            ")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "MemoryImage",
]


# ============================================================
# TEST / DEBUG
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit "
        "Memory Image"
    )

    print()

    memory = MemoryImage()

    program = bytes(
        [
            0x10,
            0x42,
            0xC0,
            0xF0,
        ]
    )

    loaded = memory.load(
        program,
        0x00,
    )

    print(
        f"Loaded bytes: {loaded}"
    )

    print()

    print(
        "Memory dump:"
    )

    memory.dump(
        0x00,
        16,
    )

    print()

    print(
        "Memory size:",
        len(memory),
        "bytes",
    )

    print()

    print(
        "Byte at 0x00:",
        f"0x{memory.read(0x00):02X}",
    )

    print(
        "Byte at 0x01:",
        f"0x{memory.read(0x01):02X}",
    )

    print()

    print(
        "Intel HEX:"
    )

    print(
        memory.to_intel_hex(
            start_address=0x00,
            size=4,
        )
    )
