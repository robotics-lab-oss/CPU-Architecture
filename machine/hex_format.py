"""
hex_format.py

MiniCPU 8-bit Machine Code HEX Format

Responsibilities:
    - Convert machine code to hexadecimal text
    - Convert hexadecimal text to machine code
    - Create Intel HEX records
    - Parse Intel HEX records
    - Validate Intel HEX checksums
    - Load Intel HEX data
    - Create complete memory images

Architecture:
    - 8-bit data
    - 8-bit address
    - 256-byte memory space
    - 16 instructions

Supported HEX formats:

    1. Plain HEX

        10 42 C0 F0

    2. Compact HEX

        1042C0F0

    3. Intel HEX

        :LLAAAATTDD...CC

Because MiniCPU has an 8-bit address space,
Intel HEX addresses are validated against
the 0x00-0xFF memory range.
"""

from __future__ import annotations

from pathlib import Path


class HexFormat:
    """
    HEX format utility for MiniCPU.

    Supports:
        - Plain hexadecimal
        - Compact hexadecimal
        - Intel HEX
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    BYTE_BITS = 8

    MIN_BYTE = 0x00

    MAX_BYTE = 0xFF

    MEMORY_SIZE = 256

    # Intel HEX record types
    DATA_RECORD = 0x00

    EOF_RECORD = 0x01

    EXTENDED_SEGMENT_ADDRESS_RECORD = 0x02

    EXTENDED_LINEAR_ADDRESS_RECORD = 0x04

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
        Validate an 8-bit integer.
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
    # HEX BYTE
    # ========================================================

    @classmethod
    def format_byte(
        cls,
        value: int,
        prefix: bool = False,
    ) -> str:
        """
        Format one 8-bit value as HEX.

        Example:

            0x42 -> "42"

        With prefix:

            0x42 -> "0x42"
        """

        value = cls.validate_byte(
            value
        )

        if prefix:
            return f"0x{value:02X}"

        return f"{value:02X}"

    # ========================================================
    # INTEGER LIST -> HEX
    # ========================================================

    @classmethod
    def bytes_to_hex(
        cls,
        data: bytes | bytearray,
        separator: str = " ",
        prefix: bool = False,
    ) -> str:
        """
        Convert machine-code bytes to HEX text.

        Example:

            b"\\x10\\x42\\xF0"

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
    # HEX -> BYTES
    # ========================================================

    @classmethod
    def hex_to_bytes(
        cls,
        value: str,
    ) -> bytes:
        """
        Convert plain HEX text to bytes.

        Supported:

            "10 42 F0"

            "0x10 0x42 0xF0"

            "1042F0"
        """

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                "HEX value must be a string."
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
                "\t",
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
                "_",
                "",
            )
        )

        if not cleaned:
            return b""

        if len(cleaned) % 2 != 0:
            raise ValueError(
                "HEX data must contain "
                "an even number of digits."
            )

        try:

            return bytes.fromhex(
                cleaned
            )

        except ValueError as exc:

            raise ValueError(
                "Invalid HEX data."
            ) from exc

    # ========================================================
    # CHECKSUM
    # ========================================================

    @staticmethod
    def calculate_checksum(
        record_bytes: bytes | bytearray,
    ) -> int:
        """
        Calculate Intel HEX checksum.

        The checksum is the two's complement
        of the least significant byte of
        the sum of all record bytes.

        Record bytes include:

            Byte Count
            Address High
            Address Low
            Record Type
            Data
        """

        if not isinstance(
            record_bytes,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Record bytes must be bytes "
                "or bytearray."
            )

        total = sum(
            record_bytes
        )

        checksum = (
            (-total)
            & 0xFF
        )

        return checksum

    # ========================================================
    # VALIDATE CHECKSUM
    # ========================================================

    @classmethod
    def validate_checksum(
        cls,
        record: bytes | bytearray,
    ) -> bool:
        """
        Validate a complete Intel HEX record.

        The record must contain:

            Byte Count
            Address High
            Address Low
            Type
            Data
            Checksum
        """

        if not isinstance(
            record,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Record must be bytes "
                "or bytearray."
            )

        if len(record) < 5:
            return False

        return (
            sum(record)
            & 0xFF
        ) == 0

    # ========================================================
    # CREATE INTEL HEX RECORD
    # ========================================================

    @classmethod
    def create_record(
        cls,
        address: int,
        record_type: int,
        data: bytes | bytearray = b"",
    ) -> str:
        """
        Create one Intel HEX record.

        Format:

            :LLAAAATTDD...CC

        Example:

            :030000001042F0FD

        Args:

            address:
                16-bit record address.

            record_type:
                Intel HEX record type.

            data:
                Record data.
        """

        if not isinstance(
            address,
            int,
        ):
            raise TypeError(
                "Address must be an integer."
            )

        if not (
            0x0000
            <= address
            <= 0xFFFF
        ):
            raise ValueError(
                "Intel HEX address must "
                "be 16-bit."
            )

        if not isinstance(
            record_type,
            int,
        ):
            raise TypeError(
                "Record type must be "
                "an integer."
            )

        if not (
            0x00
            <= record_type
            <= 0xFF
        ):
            raise ValueError(
                "Record type must be "
                "between 0x00 and 0xFF."
            )

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        if len(data) > 0xFF:
            raise ValueError(
                "Intel HEX record cannot "
                "contain more than 255 bytes."
            )

        byte_count = len(data)

        record_bytes = bytes(
            [
                byte_count,
                (address >> 8) & 0xFF,
                address & 0xFF,
                record_type,
            ]
        ) + bytes(data)

        checksum = (
            cls.calculate_checksum(
                record_bytes
            )
        )

        return (
            ":"
            + record_bytes.hex().upper()
            + f"{checksum:02X}"
        )

    # ========================================================
    # CREATE DATA RECORD
    # ========================================================

    @classmethod
    def create_data_record(
        cls,
        address: int,
        data: bytes | bytearray,
    ) -> str:
        """
        Create an Intel HEX data record.
        """

        if not (
            0x0000
            <= address
            <= 0xFFFF
        ):
            raise ValueError(
                "Address must be 16-bit."
            )

        return cls.create_record(
            address,
            cls.DATA_RECORD,
            data,
        )

    # ========================================================
    # CREATE EOF RECORD
    # ========================================================

    @classmethod
    def create_eof_record(
        cls,
    ) -> str:
        """
        Create Intel HEX EOF record.

        Standard result:

            :00000001FF
        """

        return cls.create_record(
            0x0000,
            cls.EOF_RECORD,
            b"",
        )

    # ========================================================
    # PARSE INTEL HEX RECORD
    # ========================================================

    @classmethod
    def parse_record(
        cls,
        line: str,
    ) -> dict:
        """
        Parse one Intel HEX record.

        Returns:

            {
                "byte_count": 3,
                "address": 0x0000,
                "record_type": 0x00,
                "data": b"\\x10\\x42\\xF0",
                "checksum": 0xFD
            }
        """

        if not isinstance(
            line,
            str,
        ):
            raise TypeError(
                "Intel HEX record must "
                "be a string."
            )

        line = line.strip()

        if not line:
            raise ValueError(
                "Intel HEX record cannot "
                "be empty."
            )

        if not line.startswith(
            ":"
        ):
            raise ValueError(
                "Intel HEX record must "
                "start with ':'."
            )

        hex_data = line[1:]

        if len(hex_data) % 2 != 0:
            raise ValueError(
                "Intel HEX record must "
                "contain complete bytes."
            )

        try:

            raw = bytes.fromhex(
                hex_data
            )

        except ValueError as exc:

            raise ValueError(
                "Invalid Intel HEX characters."
            ) from exc

        if len(raw) < 5:
            raise ValueError(
                "Intel HEX record is too short."
            )

        byte_count = raw[0]

        expected_length = (
            byte_count + 5
        )

        if len(raw) != expected_length:
            raise ValueError(
                "Intel HEX byte count "
                "does not match record length."
            )

        if not cls.validate_checksum(
            raw
        ):
            raise ValueError(
                "Invalid Intel HEX checksum."
            )

        address = (
            (raw[1] << 8)
            | raw[2]
        )

        record_type = raw[3]

        data = raw[
            4:
            4 + byte_count
        ]

        checksum = raw[
            -1
        ]

        return {
            "byte_count": byte_count,
            "address": address,
            "record_type": record_type,
            "data": bytes(data),
            "checksum": checksum,
        }

    # ========================================================
    # CREATE INTEL HEX PROGRAM
    # ========================================================

    @classmethod
    def create_intel_hex(
        cls,
        data: bytes | bytearray,
        start_address: int = 0x0000,
        record_size: int = 16,
        include_eof: bool = True,
    ) -> str:
        """
        Convert machine code into Intel HEX.

        Example:

            10 42 C0 F0

        Output:

            :041000001042C0F0...
            :00000001FF

        The default record size is 16 bytes.
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        if not isinstance(
            start_address,
            int,
        ):
            raise TypeError(
                "Start address must "
                "be an integer."
            )

        if not (
            0x0000
            <= start_address
            <= 0xFFFF
        ):
            raise ValueError(
                "Start address must "
                "be 16-bit."
            )

        if not isinstance(
            record_size,
            int,
        ):
            raise TypeError(
                "Record size must "
                "be an integer."
            )

        if not (
            1
            <= record_size
            <= 0xFF
        ):
            raise ValueError(
                "Record size must be "
                "between 1 and 255."
            )

        lines = []

        address = start_address

        for offset in range(
            0,
            len(data),
            record_size,
        ):

            chunk = data[
                offset:
                offset + record_size
            ]

            current_address = (
                address + offset
            )

            if current_address > 0xFFFF:
                raise ValueError(
                    "Program exceeds "
                    "16-bit Intel HEX address space."
                )

            lines.append(
                cls.create_data_record(
                    current_address,
                    chunk,
                )
            )

        if include_eof:

            lines.append(
                cls.create_eof_record()
            )

        return "\n".join(
            lines
        )

    # ========================================================
    # PARSE INTEL HEX PROGRAM
    # ========================================================

    @classmethod
    def parse_intel_hex(
        cls,
        text: str,
    ) -> dict:
        """
        Parse a complete Intel HEX program.

        Returns:

            {
                "data": bytes(...),
                "start_address": 0x0000,
                "records": [...]
            }

        Only DATA and EOF records are required
        for MiniCPU memory loading.

        Extended address records are recognized
        but rejected if they exceed the 8-bit
        MiniCPU memory range.
        """

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "Intel HEX content must "
                "be a string."
            )

        records = []

        memory = {}

        eof_found = False

        for line_number, line in enumerate(
            text.splitlines(),
            start=1,
        ):

            line = line.strip()

            if not line:
                continue

            try:

                record = cls.parse_record(
                    line
                )

            except (
                TypeError,
                ValueError,
            ) as exc:

                raise ValueError(
                    f"Invalid Intel HEX "
                    f"record at line "
                    f"{line_number}: "
                    f"{exc}"
                ) from exc

            records.append(
                record
            )

            record_type = (
                record[
                    "record_type"
                ]
            )

            if record_type == (
                cls.DATA_RECORD
            ):

                address = (
                    record[
                        "address"
                    ]
                )

                data = record[
                    "data"
                ]

                if (
                    address
                    + len(data)
                    > cls.MEMORY_SIZE
                ):
                    raise ValueError(
                        "Intel HEX data exceeds "
                        "MiniCPU 8-bit address space."
                    )

                for offset, byte in enumerate(
                    data
                ):

                    memory[
                        address + offset
                    ] = byte

            elif record_type == (
                cls.EOF_RECORD
            ):

                eof_found = True

                break

            elif record_type in (
                cls.EXTENDED_SEGMENT_ADDRESS_RECORD,
                cls.EXTENDED_LINEAR_ADDRESS_RECORD,
            ):

                raise ValueError(
                    "Extended address records "
                    "are not supported by the "
                    "MiniCPU 8-bit memory model."
                )

        if not records:

            raise ValueError(
                "Intel HEX content is empty."
            )

        if not eof_found:

            raise ValueError(
                "Intel HEX EOF record "
                "is missing."
            )

        if memory:

            max_address = max(
                memory.keys()
            )

            image = bytearray(
                max_address + 1
            )

            for address, byte in (
                memory.items()
            ):

                image[
                    address
                ] = byte

            start_address = min(
                memory.keys()
            )

            result_data = bytes(
                image
            )

        else:

            start_address = 0x00

            result_data = b""

        return {
            "data": result_data,
            "start_address": start_address,
            "records": records,
        }

    # ========================================================
    # WRITE INTEL HEX FILE
    # ========================================================

    @classmethod
    def write_intel_hex_file(
        cls,
        path: str | Path,
        data: bytes | bytearray,
        start_address: int = 0x0000,
        record_size: int = 16,
    ) -> Path:
        """
        Write machine code as Intel HEX file.
        """

        text = cls.create_intel_hex(
            data,
            start_address,
            record_size,
            include_eof=True,
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
    # READ INTEL HEX FILE
    # ========================================================

    @classmethod
    def read_intel_hex_file(
        cls,
        path: str | Path,
    ) -> dict:
        """
        Read and parse an Intel HEX file.
        """

        path = Path(
            path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Intel HEX file not found: "
                f"{path}"
            )

        if not path.is_file():

            raise ValueError(
                f"Path is not a file: "
                f"{path}"
            )

        text = path.read_text(
            encoding="utf-8"
        )

        return cls.parse_intel_hex(
            text
        )

    # ========================================================
    # CREATE MEMORY IMAGE
    # ========================================================

    @classmethod
    def create_memory_image(
        cls,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> bytes:
        """
        Create a complete 256-byte MiniCPU
        memory image.
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Data must be bytes "
                "or bytearray."
            )

        cls.validate_byte(
            start_address,
            "Start address",
        )

        if (
            start_address
            + len(data)
            > cls.MEMORY_SIZE
        ):
            raise ValueError(
                "Data does not fit "
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
        Load HEX-decoded machine code
        into a memory object.

        Memory must provide:

            write(address, value)

        Returns:
            Number of loaded bytes.
        """

        if not hasattr(
            memory,
            "write",
        ):
            raise TypeError(
                "Memory object must provide "
                "write(address, value)."
            )

        cls.validate_byte(
            start_address,
            "Start address",
        )

        if (
            start_address
            + len(data)
            > cls.MEMORY_SIZE
        ):
            raise ValueError(
                "Data does not fit "
                "inside memory."
            )

        for offset, byte in enumerate(
            data
        ):

            memory.write(
                start_address + offset,
                byte,
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
        Print a HEX memory dump.
        """

        cls.validate_byte(
            start_address,
            "Start address",
        )

        if columns <= 0:
            raise ValueError(
                "columns must be "
                "greater than zero."
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
            "HexFormat("
            "data_width=8, "
            "address_width=8, "
            "memory_size=256"
            ")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "HexFormat",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit "
        "HEX Format"
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
        "Plain HEX:"
    )

    print(
        HexFormat.bytes_to_hex(
            program
        )
    )

    print()

    print(
        "Intel HEX:"
    )

    intel_hex = (
        HexFormat.create_intel_hex(
            program
        )
    )

    print(
        intel_hex
    )

    print()

    print(
        "Parsed Intel HEX:"
    )

    parsed = (
        HexFormat.parse_intel_hex(
            intel_hex
        )
    )

    print(
        HexFormat.bytes_to_hex(
            parsed["data"]
        )
    )
