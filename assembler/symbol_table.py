"""
symbol_table.py

MiniCPU 8-bit CPU Architecture
Symbol Table

Responsibilities:
    - Store labels
    - Store EQU constants
    - Resolve symbols
    - Detect duplicate symbols
    - Detect undefined symbols
    - Validate 8-bit addresses
    - Validate 8-bit constants
    - Track source line information
    - Support first-pass address calculation

The symbol table does NOT:
    - Generate machine code
    - Execute instructions
    - Encode opcodes

Address space:
    0x00 - 0xFF

Maximum address:
    255

Instruction size:
    1 byte or 2 bytes
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional

from instruction_set import (
    INSTRUCTION_SET,
)


# ============================================================
# CPU LIMITS
# ============================================================

ADDRESS_MIN = 0x00
ADDRESS_MAX = 0xFF

VALUE_MIN = 0x00
VALUE_MAX = 0xFF


# ============================================================
# SYMBOL TYPES
# ============================================================

class SymbolType(str, Enum):
    """
    Type of symbol stored in the symbol table.
    """

    LABEL = "label"

    EQU = "equ"


# ============================================================
# SYMBOL ERROR
# ============================================================

class SymbolTableError(Exception):
    """
    Base exception for symbol-table errors.
    """

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ):
        self.message = message
        self.line = line
        self.column = column

        location = ""

        if line is not None:
            location += f"Line {line}"

        if column is not None:
            location += f", Column {column}"

        if location:
            location += ": "

        super().__init__(
            f"{location}{message}"
        )


# ============================================================
# SYMBOL
# ============================================================

@dataclass(frozen=True)
class Symbol:
    """
    Represents one symbol.

    Examples:

        LOOP:
            -> LABEL

        VALUE EQU 0x80
            -> EQU
    """

    name: str

    value: int

    symbol_type: SymbolType

    line: Optional[int] = None

    column: Optional[int] = None

    source: str = ""

    @property
    def address(self) -> int:
        """
        Return symbol value as an address.

        This is mainly useful for labels.
        """

        return self.value

    @property
    def is_label(self) -> bool:
        return (
            self.symbol_type
            == SymbolType.LABEL
        )

    @property
    def is_equ(self) -> bool:
        return (
            self.symbol_type
            == SymbolType.EQU
        )


# ============================================================
# SYMBOL TABLE
# ============================================================

class SymbolTable:
    """
    MiniCPU symbol table.

    Symbols are case-insensitive.

    Example:

        START:
            -> START

        start:
            -> duplicate symbol

    Both refer to the same symbol name.
    """

    def __init__(self):
        self.reset()

    # ========================================================
    # RESET
    # ========================================================

    def reset(self) -> None:
        """
        Clear all symbols.
        """

        self.symbols: Dict[
            str,
            Symbol,
        ] = {}

    # ========================================================
    # NORMALIZE NAME
    # ========================================================

    @staticmethod
    def normalize_name(
        name: str,
    ) -> str:
        """
        Normalize symbol name.

        Symbols are case-insensitive.
        """

        if not isinstance(
            name,
            str,
        ):
            raise TypeError(
                "Symbol name must be a string"
            )

        name = name.strip()

        if not name:
            raise ValueError(
                "Symbol name cannot be empty"
            )

        return name.upper()

    # ========================================================
    # VALIDATE NAME
    # ========================================================

    @staticmethod
    def validate_name(
        name: str,
    ) -> None:
        """
        Validate symbol name.

        Valid:

            START
            LOOP
            VALUE
            _TEMP
            LABEL1

        Invalid:

            123
            1LABEL
            HELLO-WORLD
            A.B
        """

        name = name.strip()

        if not name:
            raise ValueError(
                "Symbol name cannot be empty"
            )

        first = name[0]

        if not (
            first.isalpha()
            or first == "_"
        ):
            raise ValueError(
                f"Invalid symbol name: "
                f"{name!r}"
            )

        for char in name[1:]:

            if not (
                char.isalnum()
                or char == "_"
            ):
                raise ValueError(
                    f"Invalid symbol name: "
                    f"{name!r}"
                )

    # ========================================================
    # VALIDATE VALUE
    # ========================================================

    @staticmethod
    def validate_value(
        value: int,
        name: str = "symbol",
    ) -> None:
        """
        Validate an 8-bit symbol value.
        """

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{name} value must "
                f"be an integer"
            )

        if not (
            VALUE_MIN
            <= value
            <= VALUE_MAX
        ):
            raise ValueError(
                f"{name} value must be "
                f"between 0x00 and 0xFF: "
                f"{value}"
            )

    # ========================================================
    # ADD SYMBOL
    # ========================================================

    def add(
        self,
        name: str,
        value: int,
        symbol_type: SymbolType,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source: str = "",
    ) -> Symbol:
        """
        Add a symbol.

        Raises:
            SymbolTableError
                if symbol already exists.
        """

        name = self.normalize_name(
            name
        )

        self.validate_name(
            name
        )

        self.validate_value(
            value,
            name,
        )

        if name in self.symbols:

            previous = (
                self.symbols[name]
            )

            location = ""

            if (
                previous.line
                is not None
            ):

                location = (
                    f" previously defined "
                    f"at line "
                    f"{previous.line}"
                )

            raise SymbolTableError(
                (
                    f"Duplicate symbol: "
                    f"{name}"
                    f"{location}"
                ),
                line,
                column,
            )

        symbol = Symbol(
            name=name,
            value=value,
            symbol_type=symbol_type,
            line=line,
            column=column,
            source=source,
        )

        self.symbols[name] = symbol

        return symbol

    # ========================================================
    # ADD LABEL
    # ========================================================

    def add_label(
        self,
        name: str,
        address: int,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source: str = "",
    ) -> Symbol:
        """
        Add a label at a memory address.
        """

        return self.add(
            name=name,
            value=address,
            symbol_type=SymbolType.LABEL,
            line=line,
            column=column,
            source=source,
        )

    # ========================================================
    # ADD EQU
    # ========================================================

    def add_equ(
        self,
        name: str,
        value: int,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source: str = "",
    ) -> Symbol:
        """
        Add an EQU constant.
        """

        return self.add(
            name=name,
            value=value,
            symbol_type=SymbolType.EQU,
            line=line,
            column=column,
            source=source,
        )

    # ========================================================
    # EXISTS
    # ========================================================

    def exists(
        self,
        name: str,
    ) -> bool:
        """
        Return True if symbol exists.
        """

        name = self.normalize_name(
            name
        )

        return (
            name in self.symbols
        )

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        name: str,
    ) -> Symbol:
        """
        Get a symbol.

        Raises:
            SymbolTableError
                if undefined.
        """

        name = self.normalize_name(
            name
        )

        if name not in self.symbols:

            raise SymbolTableError(
                (
                    f"Undefined symbol: "
                    f"{name}"
                )
            )

        return self.symbols[name]

    # ========================================================
    # RESOLVE
    # ========================================================

    def resolve(
        self,
        name: str,
    ) -> int:
        """
        Resolve symbol to numeric value.
        """

        return self.get(
            name
        ).value

    # ========================================================
    # REMOVE
    # ========================================================

    def remove(
        self,
        name: str,
    ) -> None:
        """
        Remove a symbol.
        """

        name = self.normalize_name(
            name
        )

        self.symbols.pop(
            name,
            None,
        )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self) -> None:
        """
        Clear symbol table.
        """

        self.reset()

    # ========================================================
    # LENGTH
    # ========================================================

    def __len__(
        self,
    ) -> int:
        return len(
            self.symbols
        )

    # ========================================================
    # CONTAINS
    # ========================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.exists(
            name
        )

    # ========================================================
    # ITERATION
    # ========================================================

    def __iter__(
        self,
    ):
        """
        Iterate symbols in deterministic
        alphabetical order.
        """

        for name in sorted(
            self.symbols
        ):
            yield self.symbols[
                name
            ]

    # ========================================================
    # ITEMS
    # ========================================================

    def items(
        self,
    ):
        """
        Return symbols as
        name -> Symbol pairs.
        """

        for name in sorted(
            self.symbols
        ):
            yield (
                name,
                self.symbols[name],
            )

    # ========================================================
    # VALUES
    # ========================================================

    def values(
        self,
    ):
        """
        Return symbols in
        deterministic order.
        """

        for symbol in self:
            yield symbol

    # ========================================================
    # KEYS
    # ========================================================

    def keys(
        self,
    ):
        """
        Return symbol names in
        deterministic order.
        """

        return sorted(
            self.symbols
        )

    # ========================================================
    # BUILD FROM PARSED LINES
    # ========================================================

    def build(
        self,
        parsed_lines: Iterable,
    ) -> None:
        """
        Build symbol table from parsed lines.

        Expected ParsedLine structure:

            parsed_line.label
            parsed_line.instruction
            parsed_line.operands
            parsed_line.directive
            parsed_line.directive_operands
            parsed_line.line

        The address counter is increased by:

            1 byte
                for 1-byte instruction

            2 bytes
                for 2-byte instruction

        Directives:

            .ORG
                changes current address

            .DB
                reserves one byte per value

            .BYTE
                reserves one byte per value

            EQU
                defines a constant
        """

        self.reset()

        address = 0

        for parsed in parsed_lines:

            # ------------------------------------------------
            # Label
            # ------------------------------------------------

            if parsed.label is not None:

                self.add_label(
                    name=parsed.label,
                    address=address,
                    line=parsed.line,
                    column=parsed.column,
                    source=getattr(
                        parsed,
                        "source",
                        "",
                    ),
                )

            # ------------------------------------------------
            # Directive
            # ------------------------------------------------

            if parsed.directive is not None:

                address = (
                    self._process_directive(
                        parsed,
                        address,
                    )
                )

                continue

            # ------------------------------------------------
            # No instruction
            # ------------------------------------------------

            if parsed.instruction is None:

                continue

            # ------------------------------------------------
            # Instruction
            # ------------------------------------------------

            instruction = (
                parsed.instruction.upper()
            )

            if instruction not in (
                INSTRUCTION_SET
            ):

                raise SymbolTableError(
                    (
                        f"Unknown instruction: "
                        f"{instruction}"
                    ),
                    parsed.line,
                    parsed.column,
                )

            definition = (
                INSTRUCTION_SET[
                    instruction
                ]
            )

            instruction_size = (
                definition.size
            )

            # ------------------------------------------------
            # Address overflow check
            # ------------------------------------------------

            if (
                address
                + instruction_size
                > ADDRESS_MAX + 1
            ):

                raise SymbolTableError(
                    (
                        "Program exceeds "
                        "8-bit address space "
                        f"at address "
                        f"0x{address:02X}"
                    ),
                    parsed.line,
                    parsed.column,
                )

            address += (
                instruction_size
            )

    # ========================================================
    # PROCESS DIRECTIVE
    # ========================================================

    def _process_directive(
        self,
        parsed,
        address: int,
    ) -> int:
        """
        Process one assembler directive.
        """

        directive = (
            parsed.directive.upper()
        )

        operands = (
            parsed.directive_operands
        )

        # ----------------------------------------------------
        # .ORG
        # ----------------------------------------------------

        if directive == ".ORG":

            if len(operands) != 1:

                raise SymbolTableError(
                    (
                        ".ORG requires "
                        "exactly one operand"
                    ),
                    parsed.line,
                    parsed.column,
                )

            value = (
                self._resolve_operand(
                    operands[0]
                )
            )

            if not (
                ADDRESS_MIN
                <= value
                <= ADDRESS_MAX
            ):

                raise SymbolTableError(
                    (
                        ".ORG address must "
                        "be between "
                        "0x00 and 0xFF"
                    ),
                    operands[0].line,
                    operands[0].column,
                )

            return value

        # ----------------------------------------------------
        # .DB / .BYTE
        # ----------------------------------------------------

        if directive in (
            ".DB",
            ".BYTE",
        ):

            if not operands:

                raise SymbolTableError(
                    (
                        f"{directive} "
                        f"requires at least "
                        f"one value"
                    ),
                    parsed.line,
                    parsed.column,
                )

            bytes_required = 0

            for operand in operands:

                if operand.is_string():

                    bytes_required += len(
                        operand.value
                    )

                else:

                    value = (
                        self._resolve_operand(
                            operand
                        )
                    )

                    self.validate_value(
                        value,
                        f"{directive} value",
                    )

                    bytes_required += 1

            if (
                address
                + bytes_required
                > ADDRESS_MAX + 1
            ):

                raise SymbolTableError(
                    (
                        "Data exceeds "
                        "8-bit address space"
                    ),
                    parsed.line,
                    parsed.column,
                )

            return (
                address
                + bytes_required
            )

        # ----------------------------------------------------
        # EQU
        # ----------------------------------------------------

        if directive in (
            "EQU",
            ".EQU",
        ):

            # The parser currently represents
            # EQU as a directive.
            #
  
