"""
memory_view.py

MiniCPU 8-bit CPU Architecture
Memory Inspection and Visualization

Responsibilities:
    - Inspect CPU memory
    - Read individual addresses
    - Read memory ranges
    - Write memory for debugging
    - Hex dump
    - ASCII dump
    - Search memory
    - Compare memory ranges
    - Export memory snapshots
    - Display memory pages

Memory model:

    Address range:
        0x00 - 0xFF

    Each memory location:
        8-bit (0x00 - 0xFF)
"""

from __future__ import annotations

from typing import Optional


class MemoryView:
    """
    Debugger-oriented memory inspection interface.

    Example:

        view = MemoryView(simulator)

        value = view.read(0x10)

        data = view.read_range(
            0x00,
            16,
        )

        view.dump(
            0x00,
            64,
        )
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    MIN_ADDRESS = 0x00

    MAX_ADDRESS = 0xFF

    MEMORY_SIZE = 256

    BYTE_MASK = 0xFF

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        simulator=None,
        memory=None,
    ):
        """
        Initialize MemoryView.

        Args:
            simulator:
                MiniCPU Simulator instance.

            memory:
                Optional direct Memory instance.

        At least one of simulator or memory
        should be provided before using memory
        operations.
        """

        self.simulator = simulator

        self.memory = memory

    # ========================================================
    # ATTACH SIMULATOR
    # ========================================================

    def attach_simulator(
        self,
        simulator,
    ) -> None:
        """
        Attach Simulator instance.
        """

        if simulator is None:

            raise ValueError(
                "Simulator cannot be None."
            )

        self.simulator = simulator

    # ========================================================
    # ATTACH MEMORY
    # ========================================================

    def attach_memory(
        self,
        memory,
    ) -> None:
        """
        Attach direct Memory instance.
        """

        if memory is None:

            raise ValueError(
                "Memory cannot be None."
            )

        self.memory = memory

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    @classmethod
    def validate_address(
        cls,
        address: int,
    ) -> int:
        """
        Validate 8-bit memory address.
        """

        if not isinstance(
            address,
            int,
        ):

            raise TypeError(
                "Memory address must "
                "be an integer."
            )

        if not (
            cls.MIN_ADDRESS
            <= address
            <= cls.MAX_ADDRESS
        ):

            raise ValueError(
                "Memory address must "
                "be between 0x00 and 0xFF."
            )

        return address

    # ========================================================
    # BYTE VALIDATION
    # ========================================================

    @staticmethod
    def validate_byte(
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
                "Memory value must "
                "be an integer."
            )

        if not (
            0x00
            <= value
            <= 0xFF
        ):

            raise ValueError(
                "Memory value must "
                "be between 0x00 and 0xFF."
            )

        return value

    # ========================================================
    # RESOLVE MEMORY
    # ========================================================

    def _resolve_memory(
        self,
    ):
        """
        Resolve Memory object.

        Priority:

            1. Explicit memory
            2. simulator.memory
        """

        if self.memory is not None:

            return self.memory

        if self.simulator is not None:

            memory = getattr(
                self.simulator,
                "memory",
                None,
            )

            if memory is not None:

                return memory

        raise RuntimeError(
            "No Memory instance is attached."
        )

    # ========================================================
    # READ
    # ========================================================

    def read(
        self,
        address: int,
    ) -> int:
        """
        Read one byte from memory.
        """

        address = (
            self.validate_address(
                address
            )
        )

        memory = (
            self._resolve_memory()
        )

        # ----------------------------------------------------
        # Standard Memory API
        # ----------------------------------------------------

        if hasattr(
            memory,
            "read",
        ):

            return self.validate_byte(
                memory.read(
                    address
                )
            )

        # ----------------------------------------------------
        # Alternative read_byte API
        # ----------------------------------------------------

        if hasattr(
            memory,
            "read_byte",
        ):

            return self.validate_byte(
                memory.read_byte(
                    address
                )
            )

        # ----------------------------------------------------
        # Direct list / dictionary
        # ----------------------------------------------------

        try:

            return self.validate_byte(
                memory[address]
            )

        except (
            TypeError,
            KeyError,
            IndexError,
        ) as exc:

            raise RuntimeError(
                "Unable to read memory."
            ) from exc

    # ========================================================
    # READ BYTE ALIAS
    # ========================================================

    def read_byte(
        self,
        address: int,
    ) -> int:
        """
        Alias for read().
        """

        return self.read(
            address
        )

    # ========================================================
    # READ RANGE
    # ========================================================

    def read_range(
        self,
        start_address: int,
        length: int,
    ) -> list[int]:
        """
        Read consecutive bytes.

        Raises ValueError if the range exceeds
        8-bit address space.
        """

        start_address = (
            self.validate_address(
                start_address
            )
        )

        if not isinstance(
            length,
            int,
        ):

            raise TypeError(
                "Length must be integer."
            )

        if length < 0:

            raise ValueError(
                "Length cannot be negative."
            )

        end_address = (
            start_address
            + length
        )

        if end_address > (
            self.MAX_ADDRESS + 1
        ):

            raise ValueError(
                "Memory range exceeds "
                "8-bit address space."
            )

        return [
            self.read(
                start_address
                + offset
            )
            for offset
            in range(length)
        ]

    # ========================================================
    # WRITE
    # ========================================================

    def write(
        self,
        address: int,
        value: int,
    ) -> None:
        """
        Write one byte to memory.

        This method is intended primarily
        for debugger usage.
        """

        address = (
            self.validate_address(
                address
            )
        )

        value = (
            self.validate_byte(
                value
            )
        )

        memory = (
            self._resolve_memory()
        )

        # ----------------------------------------------------
        # Standard Memory API
        # ----------------------------------------------------

        if hasattr(
            memory,
            "write",
        ):

            memory.write(
                address,
                value,
            )

            return

        # ----------------------------------------------------
        # Alternative write_byte API
        # ----------------------------------------------------

        if hasattr(
            memory,
            "write_byte",
        ):

            memory.write_byte(
                address,
                value,
            )

            return

        # ----------------------------------------------------
        # Direct list / dictionary
        # ----------------------------------------------------

        try:

            memory[address] = value

        except (
            TypeError,
            KeyError,
            IndexError,
        ) as exc:

            raise RuntimeError(
                "Unable to write memory."
            ) from exc

    # ========================================================
    # WRITE BYTE ALIAS
    # ========================================================

    def write_byte(
        self,
        address: int,
        value: int,
    ) -> None:
        """
        Alias for write().
        """

        self.write(
            address,
            value,
        )

    # ========================================================
    # WRITE RANGE
    # ========================================================

    def write_range(
        self,
        start_address: int,
        data,
    ) -> None:
        """
        Write multiple bytes.
        """

        start_address = (
            self.validate_address(
                start_address
            )
        )

        data = list(
            data
        )

        if (
            start_address
            + len(data)
            > self.MAX_ADDRESS + 1
        ):

            raise ValueError(
                "Memory range exceeds "
                "8-bit address space."
            )

        for offset, value in enumerate(
            data
        ):

            self.write(
                start_address
                + offset,
                value,
            )

    # ========================================================
    # FILL
    # ========================================================

    def fill(
        self,
        start_address: int,
        length: int,
        value: int = 0x00,
    ) -> None:
        """
        Fill memory range with one byte value.
        """

        value = (
            self.validate_byte(
                value
            )
        )

        if not isinstance(
            length,
            int,
        ):

            raise TypeError(
                "Length must be integer."
            )

        if length < 0:

            raise ValueError(
                "Length cannot be negative."
            )

        for offset in range(
            length
        ):

            self.write(
                start_address
                + offset,
                value,
            )

    # ========================================================
    # DUMP
    # ========================================================

    def dump(
        self,
        start_address: int = 0x00,
        length: int = 16,
        columns: int = 16,
    ) -> None:
        """
        Print hexadecimal memory dump.

        Example:

            0000: 10 20 30 00 00 00 00 00
                  ........
        """

        print(
            self.hex_dump(
                start_address,
                length,
                columns,
            )
        )

    # ========================================================
    # HEX DUMP
    # ========================================================

    def hex_dump(
        self,
        start_address: int = 0x00,
        length: int = 16,
        columns: int = 16,
    ) -> str:
        """
        Return formatted hexadecimal memory dump.
        """

        start_address = (
            self.validate_address(
                start_address
            )
        )

        if not isinstance(
            length,
            int,
        ):

            raise TypeError(
                "Length must be integer."
            )

        if length < 0:

            raise ValueError(
                "Length cannot be negative."
            )

        if not isinstance(
            columns,
            int,
        ):

            raise TypeError(
                "Columns must be integer."
            )

        if columns <= 0:

            raise ValueError(
                "Columns must be greater than zero."
            )

        data = (
            self.read_range(
                start_address,
                length,
            )
        )

        lines = []

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

            hex_part = " ".join(
                f"{value:02X}"
                for value
                in chunk
            )

            hex_part = (
                hex_part.ljust(
                    columns * 3 - 1
                )
            )

            ascii_part = "".join(
                (
                    chr(value)
                    if 32
                    <= value
                    <= 126
                    else "."
                )
                for value
                in chunk
            )

            lines.append(
                f"{address:02X}: "
                f"{hex_part}  "
                f"|{ascii_part}|"
            )

        if not lines:

            return (
                "(empty memory range)"
            )

        return "\n".join(
            lines
        )

    # ========================================================
    # ASCII DUMP
    # ========================================================

    def ascii_dump(
        self,
        start_address: int = 0x00,
        length: int = 16,
    ) -> str:
        """
        Return printable ASCII representation.
        """

        data = (
            self.read_range(
                start_address,
                length,
            )
        )

        return "".join(
            (
                chr(value)
                if 32
                <= value
                <= 126
                else "."
            )
            for value
            in data
        )

    # ========================================================
    # SEARCH BYTE
    # ========================================================

    def find(
        self,
        value: int,
        start_address: int = 0x00,
        length: Optional[int] = None,
    ) -> list[int]:
        """
        Find all occurrences of byte value.
        """

        value = (
            self.validate_byte(
                value
            )
        )

        start_address = (
            self.validate_address(
                start_address
            )
        )

        if length is None:

            length = (
                self.MAX_ADDRESS
                - start_address
                + 1
            )

        data = (
            self.read_range(
                start_address,
                length,
            )
        )

        return [
            start_address + index
            for index, current
            in enumerate(data)
            if current == value
        ]

    # ========================================================
    # SEARCH PATTERN
    # ========================================================

    def find_pattern(
        self,
        pattern,
        start_address: int = 0x00,
        length: Optional[int] = None,
    ) -> list[int]:
        """
        Find byte sequence in memory.

        Example:

            view.find_pattern(
                [0x10, 0x20]
            )
        """

        pattern = [
            self.validate_byte(
                value
            )
            for value
            in pattern
        ]

        if not pattern:

            return []

        start_address = (
            self.validate_address(
                start_address
            )
        )

        if length is None:

            length = (
                self.MAX_ADDRESS
                - start_address
                + 1
            )

        data = (
            self.read_range(
                start_address,
                length,
            )
        )

        results = []

        pattern_length = (
            len(pattern)
        )

        for index in range(
            len(data)
            - pattern_length
            + 1
        ):

            if (
                data[
                    index:
                    index
                    + pattern_length
                ]
                == pattern
            ):

                results.append(
                    start_address
                    + index
                )

        return results

    # ========================================================
    # COMPARE
    # ========================================================

    def compare(
        self,
        first_address: int,
        second_address: int,
        length: int,
    ) -> list[dict]:
        """
        Compare two memory ranges.

        Returns differences.
        """

        first = (
            self.read_range(
                first_address,
                length,
            )
        )

        second = (
            self.read_range(
                second_address,
                length,
            )
        )

        differences = []

        for offset, (
            first_value,
            second_value,
        ) in enumerate(
            zip(
                first,
                second,
            )
        ):

            if (
                first_value
                != second_value
            ):

                differences.append(
                    {
                        "offset": offset,

                        "first_address": (
                            first_address
                            + offset
                        ),

                        "second_address": (
                            second_address
                            + offset
                        ),

                        "first_value": (
                            first_value
                        ),

                        "second_value": (
                            second_value
                        ),
                    }
                )

        return differences

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> list[int]:
        """
        Return complete 256-byte memory snapshot.
        """

        return self.read_range(
            0x00,
            self.MEMORY_SIZE,
        )

    # ========================================================
    # RESTORE
    # ========================================================

    def restore(
        self,
        data,
    ) -> None:
        """
        Restore complete memory snapshot.

        Data must contain exactly 256 bytes.
        """

        data = list(
            data
        )

        if len(data) != (
            self.MEMORY_SIZE
        ):

            raise ValueError(
                "Memory snapshot must "
                "contain exactly 256 bytes."
            )

        for value in data:

            self.validate_byte(
                value
            )

        self.write_range(
            0x00,
            data,
        )

    # ========================================================
    # PAGE
    # ========================================================

    def page(
        self,
        page_number: int,
    ) -> list[int]:
        """
        Return one 16-byte memory page.

        Page range:

            Page 0:
                0x00 - 0x0F

            Page 1:
                0x10 - 0x1F

            ...

            Page 15:
                0xF0 - 0xFF
        """

        if not isinstance(
            page_number,
            int,
        ):

            raise TypeError(
                "Page number must be integer."
            )

        if not (
            0
            <= page_number
            <= 15
        ):

            raise ValueError(
                "Page number must "
                "be between 0 and 15."
            )

        return self.read_range(
            page_number * 16,
            16,
        )

    # ========================================================
    # PAGE DUMP
    # ========================================================

    def dump_page(
        self,
        page_number: int,
    ) -> None:
        """
        Print one memory page.
        """

        start_address = (
            page_number * 16
        )

        self.dump(
            start_address,
            16,
            16,
        )

    # ========================================================
    # RESET MEMORY
    # ========================================================

    def clear_memory(
        self,
        value: int = 0x00,
    ) -> None:
        """
        Fill complete memory with value.
        """

        value = (
            self.validate_byte(
                value
            )
        )

        self.fill(
            0x00,
            self.MEMORY_SIZE,
            value,
        )

    # ========================================================
    # STRING
    # ========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"MemoryView("
            f"size={self.MEMORY_SIZE}, "
            f"range=0x00-0xFF"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "MemoryView",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Memory View"
    )

    print()

    print(
        "Memory address range:"
    )

    print(
        "0x00 - 0xFF"
    )

    print()

    print(
        "MemoryView requires a "
        "Simulator or Memory instance."
    )
