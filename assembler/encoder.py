"""
encoder.py

MiniCPU 8-bit CPU Architecture
Machine Code Encoder

Instruction format:

    1-byte instruction:
        [ OPCODE ]

    2-byte instruction:
        [ OPCODE ][ OPERAND ]

Examples:

    NOP
        00

    HALT
        F0

    LOAD 0x10
        10 10

    STORE 0x80
        20 80

    JMP LOOP
        80 <address-of-LOOP>

Responsibilities:
    - Convert ParsedLine objects to machine-code bytes
    - Encode opcodes
    - Encode 8-bit operands
    - Resolve symbols through supplied symbol table
    - Validate instruction sizes
    - Validate 8-bit address/value range

This module does NOT:
    - Perform lexical analysis
    - Parse raw assembly source
    - Build the symbol table
    - Calculate label addresses
"""

from __future__ import annotations

from typing import (
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
)

from instruction_set import (
    BYTE_MAX,
    BYTE_MIN,
    OperandType,
    get_instruction,
)

from parser import (
    Operand,
    OperandKind,
    ParsedLine,
)


# ============================================================
# TYPES
# ============================================================

SymbolValue = Union[
    int,
]

SymbolTableLike = Mapping[
    str,
    SymbolValue,
]


# ============================================================
# ENCODER ERROR
# ============================================================

class EncoderError(Exception):
    """
    Raised when machine-code encoding fails.
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
# ENCODER
# ============================================================

class Encoder:
    """
    MiniCPU machine-code encoder.

    Example:

        encoder = Encoder(
            symbols={
                "START": 0x00,
                "LOOP": 0x05,
            }
        )

        machine_code = encoder.encode(
            parsed_lines
        )
    """

    def __init__(
        self,
        symbols: Optional[
            SymbolTableLike
        ] = None,
    ):
        self.symbols = {}

        if symbols is not None:

            for name, value in (
                symbols.items()
            ):

                self.symbols[
                    name.upper()
                ] = value

    # ========================================================
    # PUBLIC API
    # ========================================================

    def encode(
        self,
        parsed_lines: Iterable[
            ParsedLine
        ],
    ) -> bytearray:
        """
        Encode all parsed assembly lines.

        Returns:
            bytearray containing machine code.
        """

        output = bytearray()

        current_address = 0

        for parsed_line in (
            parsed_lines
        ):

            encoded = (
                self.encode_line(
                    parsed_line
                )
            )

            output.extend(
                encoded
            )

            current_address += len(
                encoded
            )

        return output

    def encode_line(
        self,
        parsed_line: ParsedLine,
    ) -> bytes:
        """
        Encode one ParsedLine.
        """

        if parsed_line.is_empty:

            return b""

        # ----------------------------------------------------
        # Label-only line
        # ----------------------------------------------------

        if parsed_line.is_label_only:

            return b""

        # ----------------------------------------------------
        # Directive
        # ----------------------------------------------------

        if parsed_line.is_directive:

            return self.encode_directive(
                parsed_line
            )

        # ----------------------------------------------------
        # Instruction
        # ----------------------------------------------------

        if parsed_line.is_instruction:

            return self.encode_instruction(
                parsed_line
            )

        raise EncoderError(
            "Parsed line contains "
            "no encodable instruction "
            "or directive",
            parsed_line.line,
            parsed_line.column,
        )

    # ========================================================
    # INSTRUCTION ENCODING
    # ========================================================

    def encode_instruction(
        self,
        parsed_line: ParsedLine,
    ) -> bytes:
        """
        Encode one instruction.

        1-byte:

            NOP
            HALT
            INC

        2-byte:

            LOAD 0x10
            STORE 0x80
            JMP LOOP
        """

        instruction = (
            parsed_line.instruction
        )

        if instruction is None:

            raise EncoderError(
                "Missing instruction",
                parsed_line.line,
                parsed_line.column,
            )

        definition = get_instruction(
            instruction
        )

        opcode = definition.opcode

        self.validate_byte(
            opcode,
            "opcode",
            parsed_line,
        )

        operands = (
            parsed_line.operands
        )

        # ----------------------------------------------------
        # 1-byte instruction
        # ----------------------------------------------------

        if definition.size == 1:

            if operands:

                raise EncoderError(
                    (
                        f"{instruction} "
                        f"does not accept "
                        f"operands"
                    ),
                    parsed_line.line,
                    parsed_line.column,
                )

            return bytes(
                [opcode]
            )

        # ----------------------------------------------------
        # 2-byte instruction
        # ----------------------------------------------------

        if definition.size == 2:

            if len(operands) != 1:

                raise EncoderError(
                    (
                        f"{instruction} "
                        f"requires exactly "
                        f"one operand"
                    ),
                    parsed_line.line,
                    parsed_line.column,
                )

            operand = operands[0]

            value = (
                self.resolve_operand(
                    operand,
                    definition
                    .operand_types[0],
                )
            )

            self.validate_byte(
                value,
                "operand",
                parsed_line,
            )

            return bytes(
                [
                    opcode,
                    value,
                ]
            )

        raise EncoderError(
            (
                f"Unsupported instruction "
                f"size: "
                f"{definition.size}"
            ),
            parsed_line.line,
            parsed_line.column,
        )

    # ========================================================
    # OPERAND RESOLUTION
    # ========================================================

    def resolve_operand(
        self,
        operand: Operand,
        expected_type: OperandType,
    ) -> int:
        """
        Convert an Operand into an 8-bit integer.

        Number:
            0x10 -> 16

        Symbol:
            LOOP -> symbol table address

        Register:
            Currently not encoded because
            current instruction definitions
            do not use register operands.
        """

        # ----------------------------------------------------
        # Numeric operand
        # ----------------------------------------------------

        if operand.kind == (
            OperandKind.NUMBER
        ):

            if (
                operand.numeric_value
                is None
            ):

                raise EncoderError(
                    (
                        "Numeric operand "
                        "has no parsed value"
                    ),
                    operand.line,
                    operand.column,
                )

            return operand.numeric_value

        # ----------------------------------------------------
        # Symbol operand
        # ----------------------------------------------------

        if operand.kind == (
            OperandKind.SYMBOL
        ):

            symbol = (
                operand.value.upper()
            )

            if symbol not in self.symbols:

                raise EncoderError(
                    (
                        f"Undefined symbol: "
                        f"{symbol}"
                    ),
                    operand.line,
                    operand.column,
                )

            value = self.symbols[
                symbol
            ]

            if not isinstance(
                value,
                int,
            ):

                raise EncoderError(
                    (
                        f"Symbol {symbol} "
                        f"does not contain "
                        f"an integer value"
                    ),
                    operand.line,
                    operand.column,
                )

            return value

        # ----------------------------------------------------
        # Register operand
        # ----------------------------------------------------

        if operand.kind == (
            OperandKind.REGISTER
        ):

            raise EncoderError(
                (
                    f"Register operand "
                    f"{operand.value} "
                    f"is not supported "
                    f"by the current "
                    f"machine-code format"
                ),
                operand.line,
                operand.column,
            )

        # ----------------------------------------------------
        # String operand
        # ----------------------------------------------------

        if operand.kind == (
            OperandKind.STRING
        ):

            raise EncoderError(
                (
                    "String operands cannot "
                    "be used by instructions"
                ),
                operand.line,
                operand.column,
            )

        raise EncoderError(
            (
                f"Unsupported operand "
                f"type: "
                f"{operand.kind}"
            ),
            operand.line,
            operand.column,
        )

    # ========================================================
    # DIRECTIVE ENCODING
    # ========================================================

    def encode_directive(
        self,
        parsed_line: ParsedLine,
    ) -> bytes:
        """
        Encode assembler directives.

        Supported:

            .DB
            .BYTE

        Non-emitting directives:

            .ORG
            EQU
            .EQU
        """

        directive = (
            parsed_line.directive
        )

        if directive is None:

            return b""

        # ----------------------------------------------------
        # .DB / .BYTE
        # ----------------------------------------------------

        if directive in (
            ".DB",
            ".BYTE",
        ):

            return self.encode_data_directive(
                parsed_line
            )

        # ----------------------------------------------------
        # .ORG
        #
        # .ORG changes logical address.
        #
        # It does not itself emit bytes.
        #
        # Address placement must be handled by
        # the final assembler/linker layer.
        # ----------------------------------------------------

        if directive == ".ORG":

            return b""

        # ----------------------------------------------------
        # EQU
        # ----------------------------------------------------

        if directive in (
            "EQU",
            ".EQU",
        ):

            return b""

        raise EncoderError(
            (
                f"Unsupported directive: "
                f"{directive}"
            ),
            parsed_line.line,
            parsed_line.column,
        )

    # ========================================================
    # DATA DIRECTIVE
    # ========================================================

    def encode_data_directive(
        self,
        parsed_line: ParsedLine,
    ) -> bytes:
        """
        Encode .DB / .BYTE.

        Example:

            .DB 0x10, 0x20, 0x30

        Output:

            10 20 30

        String:

            .DB "ABC"

        Output:

            41 42 43
        """

        output = bytearray()

        for operand in (
            parsed_line.directive_operands
        ):

            # ------------------------------------------------
            # String
            # ------------------------------------------------

            if operand.kind == (
                OperandKind.STRING
            ):

                for char in operand.value:

                    value = ord(char)

                    self.validate_byte_value(
                        value,
                        operand,
                    )

                    output.append(
                        value
                    )

                continue

            # ------------------------------------------------
            # Number
            # ------------------------------------------------

            if operand.kind == (
                OperandKind.NUMBER
            ):

                if (
                    operand.numeric_value
                    is None
                ):

                    raise EncoderError(
                        (
                            "Data operand "
                            "has no value"
                        ),
                        operand.line,
                        operand.column,
                    )

                value = (
                    operand.numeric_value
                )

                self.validate_byte_value(
                    value,
                    operand,
                )

                output.append(
                    value
                )

                continue

            # ------------------------------------------------
            # Symbol
            # ------------------------------------------------

            if operand.kind == (
                OperandKind.SYMBOL
            ):

                value = (
                    self.resolve_symbol(
                        operand
                    )
                )

                self.validate_byte_value(
                    value,
                    operand,
                )

                output.append(
                    value
                )

                continue

            raise EncoderError(
                (
                    f"Unsupported data "
                    f"operand: "
                    f"{operand.value}"
                ),
                operand.line,
                operand.column,
            )

        return bytes(
            output
        )

    # ========================================================
    # SYMBOL RESOLUTION
    # ========================================================

    def resolve_symbol(
        self,
        operand: Operand,
    ) -> int:
        """
        Resolve a symbol from the symbol table.
        """

        symbol = (
            operand.value.upper()
        )

        if symbol not in self.symbols:

            raise EncoderError(
                (
                    f"Undefined symbol: "
                    f"{symbol}"
                ),
                operand.line,
                operand.column,
            )

        value = self.symbols[
            symbol
        ]

        if not isinstance(
            value,
            int,
        ):

            raise EncoderError(
                (
                    f"Symbol {symbol} "
                    f"must resolve to "
                    f"an integer"
                ),
                operand.line,
                operand.column,
            )

        return value

    # ========================================================
    # VALIDATION
    # ========================================================

    @staticmethod
    def validate_byte(
        value: int,
        name: str,
        parsed_line: ParsedLine,
    ) -> None:
        """
        Validate an 8-bit value.
        """

        if not isinstance(
            value,
            int,
        ):

            raise EncoderError(
                (
                    f"{name} must be "
                    f"an integer"
                ),
                parsed_line.line,
                parsed_line.column,
            )

        if not (
            BYTE_MIN
            <= value
            <= BYTE_MAX
        ):

            raise EncoderError(
                (
                    f"{name} {value} "
                    f"is outside "
                    f"8-bit range "
                    f"0x00-0xFF"
                ),
                parsed_line.line,
                parsed_line.column,
            )

    @staticmethod
    def validate_byte_value(
        value: int,
        operand: Operand,
    ) -> None:
        """
        Validate a byte value from
        an Operand.
        """

        if not (
            BYTE_MIN
            <= value
            <= BYTE_MAX
        ):

            raise EncoderError(
                (
                    f"Value {value} "
                    f"is outside "
                    f"8-bit range "
                    f"0x00-0xFF"
                ),
                operand.line,
                operand.column,
            )

    # ========================================================
    # HEX OUTPUT
    # ========================================================

    @staticmethod
    def to_hex(
        machine_code: bytes,
        separator: str = " ",
    ) -> str:
        """
        Convert machine code to HEX string.

        Example:

            b"\\x10\\x10\\xf0"

        becomes:

            "10 10 F0"
        """

        return separator.join(
            f"{byte:02X}"
            for byte in machine_code
        )

    # ========================================================
    # BINARY OUTPUT
    # ========================================================

    @staticmethod
    def to_binary(
        machine_code: bytes,
        separator: str = " ",
    ) -> str:
        """
        Convert machine code to binary string.
        """

        return separator.join(
            f"{byte:08b}"
            for byte in machine_code
        )


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def encode(
    parsed_lines: Iterable[
        ParsedLine
    ],
    symbols: Optional[
        SymbolTableLike
    ] = None,
) -> bytearray:
    """
    Encode parsed assembly lines.
    """

    encoder = Encoder(
        symbols=symbols
    )

    return encoder.encode(
        parsed_lines
    )


def encode_source(
    source: str,
    symbols: Optional[
        SymbolTableLike
    ] = None,
) 
