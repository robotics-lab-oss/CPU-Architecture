"""
first_pass.py

MiniCPU 8-bit CPU Architecture
Assembler - First Pass

First Pass Responsibilities
----------------------------

1. Walk through parsed assembly lines.
2. Maintain the current memory address.
3. Define labels.
4. Detect duplicate labels.
5. Process .ORG.
6. Calculate instruction sizes.
7. Calculate .DB / .BYTE sizes.
8. Detect 8-bit address-space overflow.
9. Build the SymbolTable.
10. Produce intermediate FirstPassLine records.

CPU Address Space
-----------------

    0x00 - 0xFF

Total addressable locations:

    256 bytes

Instruction Sizes
-----------------

    1-byte instruction:
        opcode only

    2-byte instruction:
        opcode + operand

Example:

    NOP
        address 0x00
        size    1

    LOAD 0x10
        address 0x01
        size    2

Important
---------

The First Pass does NOT generate machine code.

The Second Pass is responsible for:

    - Resolving symbols
    - Encoding operands
    - Generating final machine code
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from instruction_set import (
    INSTRUCTION_SET,
)

from symbol_table import (
    ADDRESS_MAX,
    SymbolTable,
    SymbolTableError,
)


# ============================================================
# CONSTANTS
# ============================================================

ADDRESS_SPACE_SIZE = (
    ADDRESS_MAX + 1
)


# ============================================================
# FIRST PASS ERROR
# ============================================================

class FirstPassError(Exception):
    """
    Error raised during assembler first pass.
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
# FIRST PASS LINE
# ============================================================

@dataclass
class FirstPassLine:
    """
    Intermediate representation of one source line.

    Example:

        START:
            LOAD 0x10

    May become:

        address     = 0x00
        size        = 2
        label       = START
        instruction = LOAD
    """

    line: int

    address: int

    size: int

    label: Optional[str] = None

    instruction: Optional[str] = None

    directive: Optional[str] = None

    source: str = ""

    parsed_line: object = None

    @property
    def end_address(self) -> int:
        """
        Return the first address after this line.
        """

        return (
            self.address
            + self.size
        )

    @property
    def is_instruction(self) -> bool:
        return (
            self.instruction
            is not None
        )

    @property
    def is_directive(self) -> bool:
        return (
            self.directive
            is not None
        )

    @property
    def is_label_only(self) -> bool:
        return (
            self.label is not None
            and self.instruction
            is None
            and self.directive
            is None
            and self.size == 0
        )


# ============================================================
# FIRST PASS RESULT
# ============================================================

@dataclass
class FirstPassResult:
    """
    Complete result of first pass.
    """

    lines: List[
        FirstPassLine
    ]

    symbol_table: SymbolTable

    final_address: int

    program_size: int

    origin: int = 0

    @property
    def symbols(self):
        """
        Shortcut to symbol table.
        """

        return self.symbol_table


# ============================================================
# FIRST PASS
# ============================================================

class FirstPass:
    """
    MiniCPU assembler first pass.
    """

    def __init__(
        self,
        parsed_lines: Optional[
            Iterable
        ] = None,
    ):
        self.parsed_lines = list(
            parsed_lines or []
        )

        self.symbol_table = (
            SymbolTable()
        )

        self.results: List[
            FirstPassLine
        ] = []

        self.current_address = 0

        self.origin = 0

    # ========================================================
    # RUN
    # ========================================================

    def run(
        self,
    ) -> FirstPassResult:
        """
        Execute first pass.

        Returns:
            FirstPassResult
        """

        self.reset()

        for parsed_line in (
            self.parsed_lines
        ):

            self.process_line(
                parsed_line
            )

        program_size = (
            self.current_address
            - self.origin
        )

        return FirstPassResult(
            lines=self.results,
            symbol_table=(
                self.symbol_table
            ),
            final_address=(
                self.current_address
            ),
            program_size=(
                program_size
            ),
            origin=self.origin,
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset first-pass state.
        """

        self.symbol_table.reset()

        self.results.clear()

        self.current_address = 0

        self.origin = 0

    # ========================================================
    # PROCESS LINE
    # ========================================================

    def process_line(
        self,
        parsed_line,
    ) -> FirstPassLine:
        """
        Process one parsed source line.
        """

        line_number = (
            getattr(
                parsed_line,
                "line",
                None,
            )
        )

        column = (
            getattr(
                parsed_line,
                "column",
                None,
            )
        )

        address_before = (
            self.current_address
        )

        # ----------------------------------------------------
        # 1. Define Label
        # ----------------------------------------------------

        label = (
            getattr(
                parsed_line,
                "label",
                None,
            )
        )

        if label is not None:

            try:

                self.symbol_table.add_label(
                    name=label,
                    address=(
                        self.current_address
                    ),
                    line=line_number,
                    column=column,
                    source=getattr(
                        parsed_line,
                        "source",
                        "",
                    ),
                )

            except (
                SymbolTableError
            ) as error:

                raise FirstPassError(
                    str(error),
                    line_number,
                    column,
                ) from error

        # ----------------------------------------------------
        # 2. Instruction
        # ----------------------------------------------------

        instruction = (
            getattr(
                parsed_line,
                "instruction",
                None,
            )
        )

        if instruction is not None:

            size = (
                self.get_instruction_size(
                    instruction,
                    line_number,
                    column,
                )
            )

            self.check_address_range(
                self.current_address,
                size,
                line_number,
                column,
            )

            self.current_address += (
                size
            )

            result = FirstPassLine(
                line=(
                    line_number
                    if line_number
                    is not None
                    else 0
                ),
                address=(
                    address_before
                ),
                size=size,
                label=label,
                instruction=(
                    instruction.upper()
                ),
                directive=None,
                source=getattr(
                    parsed_line,
                    "source",
                    "",
                ),
                parsed_line=(
                    parsed_line
                ),
            )

            self.results.append(
                result
            )

            return result

        # ----------------------------------------------------
        # 3. Directive
        # ----------------------------------------------------

        directive = (
            getattr(
                parsed_line,
                "directive",
                None,
            )
        )

        if directive is not None:

            size = (
                self.process_directive(
                    parsed_line
                )
            )

            result = FirstPassLine(
                line=(
                    line_number
                    if line_number
                    is not None
                    else 0
                ),
                address=(
                    address_before
                ),
                size=size,
                label=label,
                instruction=None,
                directive=(
                    directive.upper()
                ),
                source=getattr(
                    parsed_line,
                    "source",
                    "",
                ),
                parsed_line=(
                    parsed_line
                ),
            )

            self.results.append(
                result
            )

            return result

        # ----------------------------------------------------
        # 4. Label-only line
        # ----------------------------------------------------

        result = FirstPassLine(
            line=(
                line_number
                if line_number
                is not None
                else 0
            ),
            address=(
                address_before
            ),
            size=0,
            label=label,
            instruction=None,
            directive=None,
            source=getattr(
                parsed_line,
                "source",
                "",
            ),
            parsed_line=(
                parsed_line
            ),
        )

        self.results.append(
            result
        )

        return result

    # ========================================================
    # INSTRUCTION SIZE
    # ========================================================

    def get_instruction_size(
        self,
        instruction: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
    ) -> int:
        """
        Return instruction size.

        Expected instruction_set.py
        definition:

            definition.size

        Example:

            NOP  -> 1
            LOAD -> 2
        """

        name = (
            instruction.upper()
        )

        if name not in (
            INSTRUCTION_SET
        ):

            raise FirstPassError(
                (
                    f"Unknown instruction: "
                    f"{name}"
                ),
                line,
                column,
            )

        definition = (
            INSTRUCTION_SET[name]
        )

        size = (
            getattr(
                definition,
                "size",
                None,
            )
        )

        if size is None:

            raise FirstPassError(
                (
                    f"Instruction "
                    f"{name} has no "
                    f"defined size"
                ),
                line,
                column,
            )

        if size not in (
            1,
            2,
        ):

            raise FirstPassError(
                (
                    f"Invalid instruction "
                    f"size for {name}: "
                    f"{size}. "
                    f"MiniCPU supports "
                    f"only 1-byte or "
                    f"2-byte instructions."
                ),
                line,
                column,
            )

        return size

    # ========================================================
    # PROCESS DIRECTIVE
    # ========================================================

    def process_directive(
        self,
        parsed_line,
    ) -> int:
        """
        Process assembler directive.

        Supported:

            .ORG
            .DB
            .BYTE

        EQU is intentionally not fully processed here
        until parser.py supports:

            VALUE EQU 0x80

        as a dedicated ParsedLine structure.
        """

        directive = (
            parsed_line.directive.upper()
        )

        operands = (
            parsed_line.directive_operands
        )

        line_number = (
            getattr(
                parsed_line,
                "line",
                None,
            )
        )

        column = (
            getattr(
                parsed_line,
                "column",
                None,
            )
        )

        # ----------------------------------------------------
        # .ORG
        # ----------------------------------------------------

        if directive == ".ORG":

            if len(operands) != 1:

                raise FirstPassError(
                    (
                        ".ORG requires "
                        "exactly one operand"
                    ),
                    line_number,
                    column,
                )

            operand = operands[0]

            # .ORG should be known during
            # first pass.
            #
            # Forward symbol references are
            # not allowed for .ORG here.

            if not operand.is_number():

                raise FirstPassError(
                    (
                        ".ORG requires a "
                        "numeric address "
                        "during first pass"
                    ),
                    operand.line,
                    operand.column,
                )

            value = (
                operand.numeric_value
            )

            if value is None:

                raise FirstPassError(
                    (
                        "Invalid .ORG value"
                    ),
                    operand.line,
                    operand.column,
                )

            if not (
                0
                <= value
                <= ADDRESS_MAX
            ):

                raise FirstPassError(
                    (
                        ".ORG address must "
                        "be between "
                        "0x00 and 0xFF"
                    ),
                    operand.line,
                    operand.column,
                )

            self.current_address = (
                value
            )

            # First .ORG becomes program
            # origin.

            if not self.results:

                self.origin = value

            return 0

        # ----------------------------------------------------
        # .DB / .BYTE
        # ----------------------------------------------------

        if directive in (
            ".DB",
            ".BYTE",
        ):

            if not operands:

                raise FirstPassError(
                    (
                        f"{directive} "
                        f"requires at least "
                        f"one operand"
                    ),
                    line_number,
                    column,
                )

            size = 0

            for operand in operands:

                # String:
                #
                # .DB "ABC"
                #
                # Requires 3 bytes.

                if operand.is_string():

                    size += len(
                        operand.value
                    )

                    continue

                # Number:
                #
                # .DB 0x10
                #
                # Requires 1 byte.

                if operand.is_number():

                    value = (
                        operand.numeric_value
                    )

                    if value is None:

                        raise FirstPassError(
                            (
                                "Invalid "
                                "numeric value"
                            ),
                            operand.line,
                            operand.column,
                        )

                    if not (
                        0
                        <= value
                        <= 0xFF
                    ):

                        raise FirstPassError(
                            (
                                f"{directive} "
                                f"value must "
                                f"be between "
                                f"0x00 and "
                                f"0xFF"
                            ),
                            operand.line,
                            operand.column,
                        )

                    size += 1

                    continue

                # Symbol:
                #
                # .DB VALUE
                #
                # One byte.
                #
                # Actual resolution is
                # performed later.

                if operand.is_symbol():

                    size += 1

                    continue

                raise FirstPassError(
                    (
                        f"Invalid operand "
                        f"for {directive}: "
                        f"{operand.value}"
                    ),
                    operand.line,
                    operand.column,
                )

            self.check_address_range(
                self.current_address,
                size,
                line_number,
                column,
            )

            self.current_address += (
                size
            )

            return size

        # ----------------------------------------------------
        # EQU
        # ----------------------------------------------------

        if directive in (
            "EQU",
            ".EQU",
        ):

            # The current parser implementation
            # does not expose the left-hand
            # symbol of:
            #
            # VALUE EQU 0x80
            #
            # in a dedicated field.
            #
            # Therefore FirstPass cannot safely
            # create an EQU symbol here.
            #
            # This branch prevents silent
            # address advancement.

            return 0

        # ----------------------------------------------------
        # Unknown directive
        # ----------------------------------------------------

        raise FirstPassError(
            (
                f"Unknown directive: "
                f"{directive}"
            ),
            line_number,
            column,
        )

    # ========================================================
    # ADDRESS RANGE CHECK
    # ============================
