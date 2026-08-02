"""
binary_format.py

MiniCPU 8-bit Machine Code Binary Format

Responsibilities:
    - Validate 8-bit values
    - Convert integers to bytes
    - Convert bytes to integers
    - Convert bytes to binary strings
    - Convert binary strings to bytes
    - Convert machine code to hexadecimal
    - Convert hexadecimal to machine code
    - Read and write binary machine-code files
    - Validate complete machine-code programs

Architecture:
    - 8-bit data
    - 8-bit address
    - 256-byte address space
"""

from __future__ import annotations

from pathlib import Path


class BinaryFormat:
    """
    Utility class for MiniCPU binary machine code.

    MiniCPU uses 8-bit bytes.

    Valid byte range:

        0x00 - 0xFF

    Examples:

        0x10
        0x42
        0xF0
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    BYTE_BITS = 8

    MIN_BYTE = 0x00

    MAX_BYTE = 0xFF

    MEMORY_SIZE = 256

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
        Validate one 8-bit integer.

        Example:

            BinaryFormat.validate_byte(0x42)

        Returns:

            0x42
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
    # INTEGER -> BYTE
    # ========================================================

    @classmethod
    def int_to_byte(
        cls,
        value: int,
    ) -> bytes:
        """
        Convert an 8-bit integer to one byte.

        Example:

            0x42 -> b'B'
        """

        value = cls.validate_byte(
            value
        )

        return bytes(
            [value]
        )

    # ========================================================
    # BYTE -> INTEGER
    # ========================================================

    @classmethod
    def byte_to_int(
        cls,
        value: bytes | bytearray,
    ) -> int:
        """
        Convert exactly one byte to integer.

        Example:

            b'B' -> 0x42
        """

        if not isinstance(
            value,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Value must be bytes "
                "or bytearray."
            )

        if len(value) != 1:
            raise ValueError(
                "Exactly one byte is required."
            )

        return value[0]

    # ========================================================
    # INTEGER LIST -> BYTES
    # ========================================================

    @classmethod
    def integers_to_bytes(
        cls,
        values,
    ) -> bytes:
        """
        Convert iterable of 8-bit integers
        to bytes.

        Example:

            [0x10, 0x42, 0xF0]

        Becomes:

            b'\\x10\\x42\\xF0'
        """

        if isinstance(
            values,
            (str, bytes, bytearray),
        ):
            raise TypeError(
                "Values must be an iterable "
                "of integers."
            )

        result = []

        for index, value in enumerate(
            values
        ):

            result.append(
                cls.validate_byte(
                    value,
                    f"Byte at index {index}",
                )
            )

        return bytes(
            result
        )

    # ========================================================
    # BYTES -> INTEGER LIST
    # ========================================================

    @classmethod
    def bytes_to_integers(
        cls,
        data: bytes | bytearray,
    ) -> list[int]:
        """
        Convert bytes into list of integers.

        Example:

            b'\\x10\\x42\\xF0'

        Returns:

            [16, 66, 240]
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        return list(
            data
        )

    # ========================================================
    # INTEGER -> BINARY STRING
    # ========================================================

    @classmethod
    def int_to_binary(
        cls,
        value: int,
    ) -> str:
        """
        Convert an 8-bit integer to
        an 8-bit binary string.

        Example:

            0x42 -> "01000010"
        """

        value = cls.validate_byte(
            value
        )

        return format(
            value,
            "08b",
        )

    # ========================================================
    # BINARY STRING -> INTEGER
    # ========================================================

    @classmethod
    def binary_to_int(
        cls,
        value: str,
    ) -> int:
        """
        Convert an 8-bit binary string
        to integer.

        Example:

            "01000010" -> 0x42
        """

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "Binary value must be a string."
            )

        value = value.strip()

        if len(value) != 8:
            raise ValueError(
                "Binary value must contain "
                "exactly 8 bits."
            )

        if any(
            bit not in "01"
            for bit in value
        ):
            raise ValueError(
                "Binary value can contain "
                "only 0 and 1."
            )

        result = int(
            value,
            2,
        )

        return cls.validate_byte(
            result
        )

    # ========================================================
    # BYTES -> BINARY STRINGS
    # ========================================================

    @classmethod
    def bytes_to_binary(
        cls,
        data: bytes | bytearray,
        separator: str = " ",
    ) -> str:
        """
        Convert complete machine code
        to binary string.

        Example:

            b'\\x10\\x42\\xF0'

        Returns:

            "00010000 01000010 11110000"
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        return separator.join(
            cls.int_to_binary(
                byte
            )
            for byte in data
        )

    # ========================================================
    # BINARY STRINGS -> BYTES
    # ========================================================

    @classmethod
    def binary_to_bytes(
        cls,
        value: str,
    ) -> bytes:
        """
        Convert binary string to bytes.

        Supported format:

            "00010000 01000010 11110000"

        Also supports:

            "000100000100001011110000"
        """

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "Binary value must be a string."
            )

        value = value.strip()

        if not value:
            return b""

        # Remove common separators.
        cleaned = (
            value
            .replace(
                " ",
                "",
            )
            .replace(
                "_",
                "",
            )
            .replace(
                "\n",
                "",
            )
            .replace(
                "\r",
                "",
            )
            .replace(
                "\t",
                "",
            )
        )

        if not cleaned:
            return b""

        if any(
            bit not in "01"
            for bit in cleaned
        ):
            raise ValueError(
                "Binary data can contain "
                "only 0 and 1."
            )

        if len(cleaned) % 8 != 0:
            raise ValueError(
                "Binary data length must be "
                "a multiple of 8 bits."
            )

        result = bytearray()

        for index in range(
            0,
            len(cleaned),
            8,
        ):

            chunk = cleaned[
                index:index + 8
            ]

            result.append(
                cls.binary_to_int(
                    chunk
                )
            )

        return bytes(
            result
        )

    # ========================================================
    # BYTES -> HEX STRING
    # ========================================================

    @classmethod
    def bytes_to_hex(
        cls,
        data: bytes | bytearray,
        separator: str = " ",
        prefix: bool = False,
    ) -> str:
        """
        Convert machine code to hexadecimal.

        Example:

            bytes_to_hex(
                b"\\x10\\x42\\xF0"
            )

        Returns:

            "10 42 F0"
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        if prefix:

            return separator.join(
                f"0x{byte:02X}"
                for byte in data
            )

        return separator.join(
            f"{byte:02X}"
            for byte in data
        )

    # ========================================================
    # HEX STRING -> BYTES
    # ========================================================

    @classmethod
    def hex_to_bytes(
        cls,
        value: str,
    ) -> bytes:
        """
        Convert hexadecimal string to bytes.

        Supported:

            "10 42 F0"

        Also:

            "0x10 0x42 0xF0"

        Also:

            "1042F0"
        """

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "Hex value must be a string."
            )

        value = value.strip()

        if not value:
            return b""

        cleaned = (
            value
            .replace(
                "0x",
                "",
            )
            .replace(
                "0X",
                "",
            )
            .replace(
                " ",
                "",
            )
            .replace(
                "_",
                "",
            )
            .replace(
                "\n",
                "",
            )
            .replace(
                "\r",
                "",
            )
            .replace(
                "\t",
                "",
            )
        )

        if not cleaned:
            return b""

        if len(cleaned) % 2 != 0:
            raise ValueError(
                "Hexadecimal data must contain "
                "an even number of digits."
            )

        try:

            return bytes.fromhex(
                cleaned
            )

        except ValueError as exc:

            raise ValueError(
                "Invalid hexadecimal data."
            ) from exc

    # ========================================================
    # FORMAT BYTE
    # ========================================================

    @classmethod
    def format_byte(
        cls,
        value: int,
        prefix: bool = True,
    ) -> str:
        """
        Format one byte.

        Example:

            0x42
        """

        value = cls.validate_byte(
            value
        )

        if prefix:

            return (
                f"0x{value:02X}"
            )

        return (
            f"{value:02X}"
        )

    # ========================================================
    # FORMAT BINARY BYTE
    # ========================================================

    @classmethod
    def format_binary_byte(
        cls,
        value: int,
        prefix: bool = False,
    ) -> str:
        """
        Format one byte as binary.

        Example:

            "0b01000010"
        """

        value = cls.validate_byte(
            value
        )

        binary = format(
            value,
            "08b",
        )

        if prefix:

            return (
                f"0b{binary}"
            )

        return binary

    # ========================================================
    # VALIDATE PROGRAM
    # ========================================================

    @classmethod
    def validate_program(
        cls,
        data: bytes | bytearray,
    ) -> bytes:
        """
        Validate complete machine code.

        The MiniCPU has a 256-byte address space,
        therefore a complete memory image cannot
        exceed 256 bytes.

        Returns validated bytes.
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Program must be bytes "
                "or bytearray."
            )

        if len(data) > cls.MEMORY_SIZE:
            raise ValueError(
                "Program cannot exceed "
                "256 bytes."
            )

        return bytes(
            data
        )

    # ========================================================
    # WRITE BINARY FILE
    # ========================================================

    @classmethod
    def write_file(
        cls,
        path: str | Path,
        data: bytes | bytearray,
    ) -> Path:
        """
        Write machine code to a binary file.

        Example:

            BinaryFormat.write_file(
                "program.bin",
                bytes([0x10, 0x42, 0xF0])
            )
        """

        data = cls.validate_program(
            data
        )

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
    # READ BINARY FILE
    # ========================================================

    @classmethod
    def read_file(
        cls,
        path: str | Path,
    ) -> bytes:
        """
        Read machine code from
        a binary file.
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

        return cls.validate_program(
            data
        )

    # ========================================================
    # WRITE HEX TEXT FILE
    # ========================================================

    @classmethod
    def write_hex_file(
        cls,
        path: str | Path,
        data: bytes | bytearray,
    ) -> Path:
        """
        Write machine code as plain
        hexadecimal text.

        Example file:

            10 42 F0
        """

        data = cls.validate_program(
            data
        )

        path = Path(
            path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        text = cls.bytes_to_hex(
            data
        )

        path.write_text(
            text + "\n",
            encoding="utf-8",
        )

        return path

    # ========================================================
    # READ HEX TEXT FILE
    # ========================================================

    @classmethod
    def read_hex_file(
        cls,
        path: str | Path,
    ) -> bytes:
        """
        Read plain hexadecimal machine code.
        """

        path = Path(
            path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Hex file not found: "
                f"{path}"
            )

        text = path.read_text(
            encoding="utf-8"
        )

        data = cls.hex_to_bytes(
            text
        )

        return cls.validate_program(
            data
        )

    # ========================================================
    # MEMORY IMAGE
    # ========================================================

    @classmethod
    def create_memory_image(
        cls,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> bytes:
        """
        Create a complete 256-byte memory image.

        Unused memory is initialized to 0x00.

        Example:

            Program:
                10 42 F0

            Start:
                0x00

        Result:

            10 42 F0 00 00 ...
        """

        data = cls.validate_program(
            data
        )

        start_address = cls.validate_byte(
            start_address,
            "Start address",
        )

        if (
            start_address
            + len(data)
            > cls.MEMORY_SIZE
        ):
            raise ValueError(
                "Program does not fit "
                "inside 256-byte memory."
            )

        image = bytearray(
            cls.MEMORY_SIZE
        )

        image[
            start_address:
            start_address + len(data)
        ] = data

        return bytes(
            image
        )

    # ========================================================
    # LOAD INTO MEMORY
    # ========================================================

    @classmethod
    def load_into_memory(
        cls,
        memory,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> int:
        """
        Load machine code into a memory object.

        The memory object must provide:

            write(address, value)

        Returns:
            Number of bytes loaded.
        """

        data = cls.validate_program(
            data
        )

        start_address = cls.validate_byte(
            start_address,
            "Start address",
        )

        if (
            start_address
            + len(data)
            > cls.MEMORY_SIZE
        ):
            raise ValueError(
                "Program does not fit "
                "inside memory."
            )

        if not hasattr(
            memory,
            "write",
        ):
            raise TypeError(
                "Memory object must provide "
                "a write(address, value) method."
            )

        for offset, value in enumerate(
            data
        ):

            address = (
                start_address
                + offset
            )

            memory.write(
                address,
                value,
            )

        return len(data)

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    @classmethod
    def dump(
        cls,
        data: bytes | bytearray,
        start_address: int = 0x00,
        columns: int = 16,
    ) -> None:
        """
        Print a hexadecimal memory dump.

        Example:

            0000: 10 42 F0 00 00 ...
        """

        data = cls.validate_program(
            data
        )

        start_address = cls.validate_byte(
            start_address,
            "Start address",
        )

        if not isinstance(
            columns,
            int,
        ):
            raise TypeError(
                "columns must be an integer."
            )

        if columns <= 0:
            raise ValueError(
                "columns must be greater than zero."
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
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return class information.
        """

        return (
            "BinaryFormat("
            "data_width=8, "
            "address_width=8, "
            "memory_size=256"
            ")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "BinaryFormat",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit "
        "Binary Format"
    )

    print()

    program = bytes(
        [
            0x10,
            0x42,
            0xC0,
            0xF0,
        ]
    )

    print(
        "Machine Code:"
    )

    print(
        BinaryFormat.bytes_to_hex(
            program
        )
    )

    print()

    print(
        "Binary:"
    )

    print(
        BinaryFormat.bytes_to_binary(
            program
        )
    )

    print()

    print(
        "Memory Dump:"
    )

    BinaryFormat.dump(
        program
    )

    print()

    print(
        "Memory Image Size:"
    )

    image = (
        BinaryFormat.create_memory_image(
            program
        )
    )

    print(
        len(image),
        "bytes"
    )
