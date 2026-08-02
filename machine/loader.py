"""
loader.py

MiniCPU 8-bit Machine Code Loader

Responsibilities:
    - Load raw binary programs
    - Load plain hexadecimal programs
    - Load Intel HEX programs
    - Validate addresses
    - Validate program size
    - Load programs into MiniCPU memory
    - Provide file-based loading helpers

Architecture:
    - 8-bit data
    - 8-bit address
    - 256-byte memory
    - 16 instructions

Expected memory API:

    memory.write(address, value)

Optional memory API:

    memory.load(data, start_address)

The loader prefers the memory object's `load()`
method when available. Otherwise it writes
bytes individually using `write()`.
"""

from __future__ import annotations

from pathlib import Path

from .binary_format import BinaryFormat
from .hex_format import HexFormat


class MachineLoader:
    """
    Load MiniCPU machine code into memory.

    Supported formats:

        - bin
        - binary
        - hex
        - plain_hex
        - ihex
        - intel_hex
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    MEMORY_SIZE = 256

    MIN_ADDRESS = 0x00

    MAX_ADDRESS = 0xFF

    FORMAT_BINARY = "bin"

    FORMAT_HEX = "hex"

    FORMAT_INTEL_HEX = "ihex"

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        memory=None,
    ):
        """
        Create a machine-code loader.

        Args:
            memory:
                Optional MiniCPU memory object.
        """

        self.memory = memory

    # ========================================================
    # MEMORY SETTER
    # ========================================================

    def set_memory(
        self,
        memory,
    ) -> None:
        """
        Set or replace the target memory object.
        """

        self.memory = memory

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
    # PROGRAM VALIDATION
    # ========================================================

    @classmethod
    def validate_program(
        cls,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> bytes:
        """
        Validate a machine-code program.

        The complete program must fit inside
        the MiniCPU 256-byte address space.
        """

        if not isinstance(
            data,
            (bytes, bytearray),
        ):
            raise TypeError(
                "Program must be bytes "
                "or bytearray."
            )

        cls.validate_address(
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
                "inside MiniCPU memory."
            )

        return bytes(
            data
        )

    # ========================================================
    # MEMORY VALIDATION
    # ========================================================

    def _require_memory(
        self,
    ):
        """
        Ensure a memory object is available.
        """

        if self.memory is None:

            raise RuntimeError(
                "No memory object is configured. "
                "Pass memory to MachineLoader "
                "or call set_memory()."
            )

        if not (
            hasattr(
                self.memory,
                "write",
            )
            or hasattr(
                self.memory,
                "load",
            )
        ):

            raise TypeError(
                "Memory object must provide "
                "either load(data, start_address) "
                "or write(address, value)."
            )

        return self.memory

    # ========================================================
    # LOAD DATA INTO MEMORY
    # ========================================================

    def load(
        self,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> int:
        """
        Load raw machine-code bytes into memory.

        Returns:
            Number of bytes loaded.
        """

        memory = self._require_memory()

        data = self.validate_program(
            data,
            start_address,
        )

        # Prefer optimized memory.load()
        if hasattr(
            memory,
            "load",
        ):

            try:

                result = memory.load(
                    data,
                    start_address,
                )

                if result is None:
                    return len(data)

                return result

            except TypeError:

                # Some memory implementations
                # may use keyword arguments.
                try:

                    result = memory.load(
                        data=data,
                        start_address=start_address,
                    )

                    if result is None:
                        return len(data)

                    return result

                except TypeError:
                    pass

        # Fallback to byte-by-byte writes.
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
    # LOAD BINARY DATA
    # ========================================================

    def load_binary(
        self,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> int:
        """
        Load raw binary machine code.
        """

        return self.load(
            data,
            start_address,
        )

    # ========================================================
    # LOAD PLAIN HEX
    # ========================================================

    def load_hex(
        self,
        text: str,
        start_address: int = 0x00,
    ) -> int:
        """
        Load plain hexadecimal machine code.

        Examples:

            "10 42 C0 F0"

        or:

            "1042C0F0"
        """

        data = HexFormat.hex_to_bytes(
            text
        )

        return self.load(
            data,
            start_address,
        )

    # ========================================================
    # LOAD INTEL HEX
    # ========================================================

    def load_intel_hex(
        self,
        text: str,
    ) -> int:
        """
        Load an Intel HEX program.

        The start address is obtained from
        the Intel HEX data records.
        """

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
    # LOAD BINARY FILE
    # ========================================================

    def load_binary_file(
        self,
        path: str | Path,
        start_address: int = 0x00,
    ) -> int:
        """
        Load a raw binary file.
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
    # LOAD PLAIN HEX FILE
    # ========================================================

    def load_hex_file(
        self,
        path: str | Path,
        start_address: int = 0x00,
    ) -> int:
        """
        Load a plain hexadecimal text file.

        Example file:

            10 42 C0 F0
        """

        path = Path(
            path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"HEX file not found: "
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

        return self.load_hex(
            text,
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
        Load an Intel HEX file.
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

        return self.load_intel_hex(
            text
        )

    # ========================================================
    # AUTO FORMAT DETECTION
    # ========================================================

    @classmethod
    def detect_format(
        cls,
        path: str | Path,
    ) -> str:
        """
        Detect file format from extension.

        Supported:

            .bin
            .binary
            .hex
            .ihex
            .ihx

        Returns:

            "bin"
            "hex"
            "ihex"
        """

        path = Path(
            path
        )

        suffix = (
            path.suffix
            .lower()
        )

        if suffix in (
            ".bin",
            ".binary",
        ):

            return cls.FORMAT_BINARY

        if suffix in (
            ".ihex",
            ".ihx",
        ):

            return cls.FORMAT_INTEL_HEX

        if suffix == ".hex":

            return cls.FORMAT_HEX

        raise ValueError(
            f"Cannot determine machine-code "
            f"format from extension: "
            f"{suffix}"
        )

    # ========================================================
    # AUTO FILE LOADER
    # ========================================================

    def load_file(
        self,
        path: str | Path,
        start_address: int = 0x00,
        file_format: str | None = None,
    ) -> int:
        """
        Automatically load a machine-code file.

        If file_format is not supplied,
        it is detected from the extension.

        For Intel HEX, addresses stored inside
        the file are used.
        """

        path = Path(
            path
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Machine-code file not found: "
                f"{path}"
            )

        if not path.is_file():

            raise ValueError(
                f"Path is not a file: "
                f"{path}"
            )

        if file_format is None:

            file_format = (
                self.detect_format(
                    path
                )
            )

        file_format = (
            file_format
            .strip()
            .lower()
        )

        if file_format in (
            "bin",
            "binary",
        ):

            return self.load_binary_file(
                path,
                start_address,
            )

        if file_format in (
            "hex",
            "plain_hex",
        ):

            return self.load_hex_file(
                path,
                start_address,
            )

        if file_format in (
            "ihex",
            "intel_hex",
            "intel-hex",
        ):

            return self.load_intel_hex_file(
                path
            )

        raise ValueError(
            f"Unsupported machine-code "
            f"format: {file_format}"
        )

    # ========================================================
    # LOAD MEMORY IMAGE
    # ========================================================

    def load_memory_image(
        self,
        image: bytes | bytearray,
    ) -> int:
        """
        Load a complete 256-byte memory image.

        The image is loaded starting at 0x00.
        """

        if len(image) != (
            self.MEMORY_SIZE
        ):

            raise ValueError(
                "A complete MiniCPU memory "
                "image must contain exactly "
                "256 bytes."
            )

        return self.load(
            image,
            0x00,
        )

    # ========================================================
    # CLEAR MEMORY
    # ========================================================

    def clear_memory(
        self,
        value: int = 0x00,
    ) -> int:
        """
        Fill all 256 memory locations
        with the specified byte value.

        Returns:
            Number of bytes written.
        """

        value = BinaryFormat.validate_byte(
            value,
            "Fill value",
        )

        memory = self._require_memory()

        if hasattr(
            memory,
            "clear",
        ):

            try:

                result = memory.clear(
                    value
                )

                if result is None:
                    return self.MEMORY_SIZE

                return result

            except TypeError:
                pass

        for address in range(
            self.MEMORY_SIZE
        ):

            memory.write(
                address,
                value,
            )

        return self.MEMORY_SIZE

    # ========================================================
    # RESET MEMORY
    # ========================================================

    def reset_memory(
        self,
    ) -> int:
        """
        Reset all memory to 0x00.
        """

        return self.clear_memory(
            0x00
        )

    # ========================================================
    # GET LOADED PROGRAM
    # ========================================================

    def read_memory(
        self,
        start_address: int = 0x00,
        size: int = 256,
    ) -> bytes:
        """
        Read bytes back from memory.

        Memory must provide:

            read(address)

        Returns:
            Bytes read.
        """

        memory = self._require_memory()

        self.validate_address(
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
            > self.MEMORY_SIZE
        ):
            raise ValueError(
                "Requested memory range "
                "exceeds MiniCPU memory."
            )

        if not hasattr(
            memory,
            "read",
        ):

            raise TypeError(
                "Memory object must provide "
                "read(address)."
            )

        result = bytearray()

        for offset in range(
            size
        ):

            value = memory.read(
                start_address
                + offset
            )

            value = BinaryFormat.validate_byte(
                value,
                f"Memory value at "
                f"0x{start_address + offset:02X}",
            )

            result.append(
                value
            )

        return bytes(
            result
        )

    # ========================================================
    # LOAD AND VERIFY
    # ========================================================

    def load_and_verify(
        self,
        data: bytes | bytearray,
        start_address: int = 0x00,
    ) -> int:
        """
        Load program and verify every byte
        after loading.

        Returns:
            Number of verified bytes.
        """

        data = self.validate_program(
            data,
            start_address,
        )

        count = self.load(
            data,
            start_address,
        )

        loaded = self.read_memory(
            start_address,
            len(data),
        )

        if loaded != data:

            raise RuntimeError(
                "Memory verification failed "
                "after loading program."
            )

        return count

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return loader information.
        """

        return (
            "MachineLoader("
            "data_width=8, "
            "address_width=8, "
            "memory_size=256"
            ")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "MachineLoader",
]


# ============================================================
# BASIC TEST MEMORY
# ============================================================

class _TestMemory:
    """
    Small internal memory implementation
    used only for module testing.
    """

    def __init__(
        self,
    ):
        self.data = bytearray(
            256
        )

    def write(
        self,
        address: int,
        value: int,
    ):
        self.data[
            address
        ] = value

    def read(
        self,
        address: int,
    ) -> int:
        return self.data[
            address
        ]


# ============================================================
# TEST / DEBUG
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit "
        "Machine Loader"
    )

    print()

    memory = _TestMemory()

    loader = MachineLoader(
        memory
    )

    program = bytes(
        [
            0x10,
            0x42,
            0xC0,
            0xF0,
        ]
    )

    loaded = loader.load_and_verify(
        program,
        start_address=0x00,
    )

    print(
        f"Loaded bytes: {loaded}"
    )

    print(
        "Memory:"
    )

    result = loader.read_memory(
        0x00,
        loaded,
    )

    print(
        BinaryFormat.bytes_to_hex(
            result
        )
    )

    print()

    intel_hex = (
        HexFormat.create_intel_hex(
            program
        )
    )

    print(
        "Intel HEX:"
    )

    print(
        intel_hex
    )
