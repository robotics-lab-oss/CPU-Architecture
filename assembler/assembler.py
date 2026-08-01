"""
assembler.py

MiniCPU 8-bit CPU Architecture
16-Instruction Assembler

Assembler Pipeline:

    Source Code
        |
        v
      Lexer
        |
        v
      Parser
        |
        v
    Parsed Lines
        |
        v
    First Pass
        |
        v
    Symbol Table
        |
        v
    Second Pass
        |
        v
    Machine Code
        |
        v
    HEX / Binary Output


CPU Architecture:
    - 8-bit data
    - 8-bit addresses
    - Address range: 0x00 - 0xFF
    - 16 instructions
    - 1-byte and 2-byte instructions

Instruction format:

    1-byte:
        [ OPCODE ]

    2-byte:
        [ OPCODE ][ OPERAND ]

Example:

    LOAD 0x10
    ADD 5
    STORE 0x80
    JMP LOOP
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

from lexer import Lexer, LexerError
from parser import (
    Operand,
    OperandKind,
    ParsedLine,
    Parser,
    ParserError,
    parse_source,
)

from opcode import (
    OPCODES,
    get_instruction_size,
)

from instruction_set import (
    INSTRUCTION_SET,
    get_instruction,
)


# ============================================================
# CPU CONSTANTS
# ============================================================

BYTE_MIN = 0x00
BYTE_MAX = 0xFF

ADDRESS_MIN = 0x00
ADDRESS_MAX = 0xFF

MEMORY_SIZE = 256


# ============================================================
# ASSEMBLER ERROR
# ============================================================

class AssemblerError(Exception):
    """
    General assembler error.
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
# ASSEMBLY RESULT
# ============================================================

@dataclass
class AssemblyResult:
    """
    Result returned by the assembler.
    """

    code: bytes

    symbols: Dict[str, int] = field(
        default_factory=dict
    )

    origin: int = 0

    source_size: int = 0

    errors: List[str] = field(
        default_factory=list
    )

    warnings: List[str] = field(
        default_factory=list
    )

    @property
    def size(self) -> int:
        """
        Number of generated machine-code bytes.
        """

        return len(self.code)

    @property
    def hex_string(self) -> str:
        """
        Return machine code as hexadecimal text.
        """

        return " ".join(
            f"{byte:02X}"
            for byte in self.code
        )

    @property
    def hex_lines(self) -> str:
        """
        Return machine code as one byte per line.
        """

        return "\n".join(
            f"{byte:02X}"
            for byte in self.code
        )

    def to_list(self) -> List[int]:
        """
        Return machine code as integer list.
        """

        return list(
            self.code
        )


# ============================================================
# ASSEMBLER
# ============================================================

class Assembler:
    """
    Complete MiniCPU assembler.

    The assembler performs:

        1. Lexical analysis
        2. Parsing
        3. First pass
        4. Symbol resolution
        5. Second pass
        6. Machine-code generation
    """

    def __init__(
        self,
        origin: int = 0x00,
        strict: bool = True,
    ):
        self.origin = origin

        self.strict = strict

        self.symbols: Dict[
            str,
            int,
        ] = {}

        self.equ_symbols: Dict[
            str,
            int,
        ] = {}

        self.machine_code: List[
            int
        ] = []

        self.current_address = (
            origin
        )

        self.parsed_lines: List[
            ParsedLine
        ] = []

        self.errors: List[
            str
        ] = []

        self.warnings: List[
            str
        ] = []

        self._validate_origin()

    # ========================================================
    # RESET
    # ========================================================

    def reset(self) -> None:
        """
        Reset assembler state.
        """

        self.symbols.clear()

        self.equ_symbols.clear()

        self.machine_code.clear()

        self.current_address = (
            self.origin
        )

        self.parsed_lines.clear()

        self.errors.clear()

        self.warnings.clear()

    # ========================================================
    # MAIN ASSEMBLY
    # ========================================================

    def assemble(
        self,
        source: str,
    ) -> AssemblyResult:
        """
        Assemble complete source code.
        """

        self.reset()

        # ----------------------------------------------------
        # Parse source
        # ----------------------------------------------------

        try:

            self.parsed_lines = (
                parse_source(
                    source
                )
            )

        except (
            LexerError,
            ParserError,
            ValueError,
        ) as error:

            raise AssemblerError(
                str(error)
            ) from error

        # ----------------------------------------------------
        # First pass
        # ----------------------------------------------------

        self.first_pass()

        # ----------------------------------------------------
        # Second pass
        # ----------------------------------------------------

        self.second_pass()

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return AssemblyResult(
            code=bytes(
                self.machine_code
            ),
            symbols=dict(
                self.symbols
            ),
            origin=self.origin,
            source_size=len(
                self.machine_code
            ),
            errors=list(
                self.errors
            ),
            warnings=list(
                self.warnings
            ),
        )

    # ========================================================
    # FIRST PASS
    # ========================================================

    def first_pass(self) -> None:
        """
        First assembler pass.

        Responsibilities:

            - Register labels
            - Register EQU constants
            - Calculate instruction addresses
            - Calculate directive sizes
        """

        self.current_address = (
            self.origin
        )

        for parsed in (
            self.parsed_lines
        ):

            # ------------------------------------------------
            # ORG
            # ------------------------------------------------

            if (
                parsed.directive
                == ".ORG"
            ):

                self.process_org_first_pass(
                    parsed
                )

                continue

            # ------------------------------------------------
            # Label
            # ------------------------------------------------

            if parsed.label:

                self.define_label(
                    parsed
                )

            # ------------------------------------------------
            # EQU
            # ------------------------------------------------

            if parsed.directive in (
                "EQU",
                ".EQU",
            ):

                self.process_equ(
                    parsed
                )

                continue

            # ------------------------------------------------
            # Instruction
            # ------------------------------------------------

            if parsed.instruction:

                size = (
                    get_instruction_size(
                        parsed.instruction
                    )
                )

                self.advance_address(
                    size,
                    parsed.line,
                )

                continue

            # ------------------------------------------------
            # Data
            # ------------------------------------------------

            if parsed.directive in (
                ".DB",
                ".BYTE",
            ):

                size = (
                    self.get_data_size(
                        parsed
                    )
                )

                self.advance_address(
                    size,
                    parsed.line,
                )

    # ========================================================
    # SECOND PASS
    # ========================================================

    def second_pass(self) -> None:
        """
        Second assembler pass.

        Converts parsed instructions and
        directives into machine code.
        """

        self.machine_code = []

        self.current_address = (
            self.origin
        )

        for parsed in (
            self.parsed_lines
        ):

            # ------------------------------------------------
            # ORG
            # ------------------------------------------------

            if (
                parsed.directive
                == ".ORG"
            ):

                self.process_org_second_pass(
                    parsed
                )

                continue

            # ------------------------------------------------
            # EQU
            # ------------------------------------------------

            if parsed.directive in (
                "EQU",
                ".EQU",
            ):

                continue

            # ------------------------------------------------
            # Label-only
            # ------------------------------------------------

            if parsed.is_label_only:

                continue

            # ------------------------------------------------
            # Instruction
            # ------------------------------------------------

            if parsed.instruction:

                encoded = (
                    self.encode_instruction(
                        parsed
                    )
                )

                self.machine_code.extend(
                    encoded
                )

                self.current_address += (
                    len(encoded)
                )

                continue

            # ------------------------------------------------
            # Data
            # ------------------------------------------------

            if parsed.directive in (
                ".DB",
                ".BYTE",
            ):

                encoded = (
                    self.encode_data(
                        parsed
                    )
                )

                self.machine_code.extend(
                    encoded
                )

                self.current_address += (
                    len(encoded)
                )

    # ========================================================
    # LABELS
    # ========================================================

    def define_label(
        self,
        parsed: ParsedLine,
    ) -> None:
        """
        Define a label at current address.
        """

        if not parsed.label:
            return

        name = (
            parsed.label.upper()
        )

        if (
            name in self.symbols
            or name in self.equ_symbols
        ):

            raise AssemblerError(
                (
                    f"Duplicate symbol: "
                    f"{name}"
                ),
                parsed.line,
                parsed.column,
            )

        self.validate_address(
            self.current_address,
            parsed.line,
        )

        self.symbols[name] = (
            self.current_address
        )

    # ========================================================
    # EQU
    # ========================================================

    def process_equ(
        self,
        parsed: ParsedLine,
    ) -> None:
        """
        Process EQU constant.

        Supported conceptual syntax:

            VALUE EQU 0x80

        The parser's current representation
        may require the source to be adapted
        if EQU is written as a prefix directive.
        """

        if not parsed.label:

            raise AssemblerError(
                (
                    "EQU requires a symbol "
                    "name before EQU"
                ),
                parsed.line,
                parsed.column,
            )

        if len(
            parsed.directive_operands
        ) != 1:

            raise AssemblerError(
                (
                    "EQU requires exactly "
                    "one value"
                ),
                parsed.line,
                parsed.column,
            )

        name = (
            parsed.label.upper()
        )

        operand = (
            parsed.directive_operands[0]
        )

        value = (
            self.resolve_operand(
                operand,
                parsed.line,
            )
        )

        if not (
            BYTE_MIN
            <= value
            <= BYTE_MAX
        ):

            raise AssemblerError(
                (
                    f"EQU value for "
                    f"{name} must be "
                    f"0x00-0xFF"
                ),
                parsed.line,
                parsed.column,
            )

        if (
            name in self.symbols
            or name in self.equ_symbols
        ):

            raise AssemblerError(
                (
                    f"Duplicate symbol: "
                    f"{name}"
                ),
                parsed.line,
                parsed.column,
            )

        self.equ_symbols[name] = (
            value
        )

    # ========================================================
    # ORG
    # ========================================================

    def process_org_first_pass(
        self,
        parsed: ParsedLine,
    ) -> None:
        """
        Process .ORG during first pass.
        """

        if len(
            parsed.directive_operands
        ) != 1:

            raise AssemblerError(
                (
                    ".ORG requires "
                    "exactly one operand"
                ),
                parsed.line,
                parsed.column,
            )

        operand = (
            parsed.directive_operands[0]
        )

        value = (
            self.resolve_operand(
                operand,
                parsed.line,
            )
        )

        self.validate_address(
            value,
            parsed.line,
        )

        self.current_address = (
            value
        )

    def process_org_second_pass(
        self,
        parsed: ParsedLine,
    ) -> None:
        """
        Process .ORG during second pass.
        """

        if len(
            parsed.directive_operands
        ) != 1:

            raise AssemblerError(
                (
                    ".ORG requires "
                    "exactly one operand"
                ),
                parsed.line,
                parsed.column,
            )

        value = (
            self.resolve_operand(
                parsed.directive_operands[0],
                parsed.line,
            )
        )

        self.validate_address(
            value,
            parsed.line,
        )

        self.current_address = (
            value
        )

    # ========================================================
    # INSTRUCTION ENCODING
    # ========================================================

    def encode_instruction(
        self,
        parsed: ParsedLine,
    ) -> List[int]:
        """
        Encode one instruction.
        """

        if not parsed.instruction:

            return []

        instruction = (
            parsed.instruction.upper()
        )

        if instruction not in OPCODES:

            raise AssemblerError(
                (
                    f"Unknown instruction: "
                    f"{instruction}"
                ),
                parsed.line,
                parsed.column,
            )

        opcode = OPCODES[
            instruction
        ]

        expected_size = (
            get_instruction_size(
                instruction
            )
        )

        definition = get_instruction(
            instruction
        )

        if len(
            parsed.operands
        ) != definition.operand_count:

            raise AssemblerError(
                (
                    f"{instruction} "
                    f"expects "
                    f"{definition.operand_count} "
                    f"operand(s)"
                ),
                parsed.line,
                parsed.column,
            )

        result = [
            opcode
        ]

        # ----------------------------------------------------
        # 1-byte instruction
        # ----------------------------------------------------

        if expected_size == 1:

            if parsed.operands:

                raise AssemblerError(
                    (
                        f"{instruction} "
                        f"does not accept "
                        f"operands"
                    ),
                    parsed.line,
                    parsed.column,
                )

            return result

        # ----------------------------------------------------
        # 2-byte instruction
        # ----------------------------------------------------

        if expected_size == 2:

            if len(
                parsed.operands
            ) != 1:

                raise AssemblerError(
                    (
                        f"{instruction} "
                        f"requires exactly "
                        f"one operand"
                    ),
                    parsed.line,
                    parsed.column,
                )

            operand = (
                parsed.operands[0]
            )

            value = (
                self.resolve_operand(
                    operand,
                    parsed.line,
                )
            )

            self.validate_byte_value(
                value,
                parsed.line,
            )

            result.append(
                value
            )

            return result

        # ----------------------------------------------------
        # Unsupported size
        # ----------------------------------------------------

        raise AssemblerError(
            (
                f"Unsupported instruction "
                f"size: {expected_size}"
            ),
            parsed.line,
            parsed.column,
        )

    # ========================================================
    # DATA ENCODING
    # ========================================================

    def encode_data(
        self,
        parsed: ParsedLine,
    ) -> List[int]:
        """
        Encode .DB / .BYTE directives.
        """

        result = []

        for operand in (
            parsed.directive_operands
        ):

            # ------------------------------------------------
            # String
            # ----------------------------------------------
