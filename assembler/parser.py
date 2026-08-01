"""
parser.py

MiniCPU 8-bit CPU Architecture
Assembly Language Parser

Pipeline:

    Assembly Source
          |
          v
        Lexer
          |
          v
        Tokens
          |
          v
        Parser
          |
          v
    ParsedLine / Operand
          |
          v
    First Pass / Second Pass

The parser is responsible for:

    - Parsing labels
    - Parsing instructions
    - Parsing operands
    - Parsing directives
    - Validating operand count
    - Validating basic operand syntax

The parser does NOT:

    - Resolve labels
    - Calculate final addresses
    - Generate machine code
    - Execute CPU instructions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Optional, Sequence

from lexer import (
    Lexer,
    LexerError,
    Token,
    TokenType,
    group_tokens_by_line,
)

from instruction_set import (
    INSTRUCTION_SET,
    OperandType,
    get_instruction,
    validate_operand_count,
)


# ============================================================
# PARSER ERROR
# ============================================================

class ParserError(Exception):
    """
    Raised when assembly tokens cannot be parsed.
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
# OPERAND KIND
# ============================================================

class OperandKind(str, Enum):
    """
    Internal representation of an operand.
    """

    NUMBER = "number"

    REGISTER = "register"

    SYMBOL = "symbol"

    STRING = "string"


# ============================================================
# OPERAND
# ============================================================

@dataclass(frozen=True)
class Operand:
    """
    Represents one parsed operand.
    """

    kind: OperandKind

    value: str

    line: int

    column: int

    numeric_value: Optional[int] = None

    def is_number(self) -> bool:
        return (
            self.kind
            == OperandKind.NUMBER
        )

    def is_register(self) -> bool:
        return (
            self.kind
            == OperandKind.REGISTER
        )

    def is_symbol(self) -> bool:
        return (
            self.kind
            == OperandKind.SYMBOL
        )

    def is_string(self) -> bool:
        return (
            self.kind
            == OperandKind.STRING
        )


# ============================================================
# PARSED LINE
# ============================================================

@dataclass
class ParsedLine:
    """
    Represents one complete assembly source line.

    Examples:

        START:

        LOAD 0x10

        LOOP:
            JMP START

        .ORG 0x00
    """

    line: int

    column: int = 1

    label: Optional[str] = None

    instruction: Optional[str] = None

    operands: List[Operand] = field(
        default_factory=list
    )

    directive: Optional[str] = None

    directive_operands: List[Operand] = field(
        default_factory=list
    )

    source: str = ""

    @property
    def is_empty(self) -> bool:
        return (
            self.label is None
            and self.instruction is None
            and self.directive is None
        )

    @property
    def is_label_only(self) -> bool:
        return (
            self.label is not None
            and self.instruction is None
            and self.directive is None
        )

    @property
    def is_instruction(self) -> bool:
        return (
            self.instruction is not None
        )

    @property
    def is_directive(self) -> bool:
        return (
            self.directive is not None
        )

    @property
    def all_operands(self) -> List[Operand]:
        """
        Return instruction operands or
        directive operands.
        """

        if self.is_directive:
            return self.directive_operands

        return self.operands


# ============================================================
# PARSER
# ============================================================

class Parser:
    """
    MiniCPU Assembly Parser.
    """

    def __init__(
        self,
        tokens: Optional[
            Sequence[Token]
        ] = None,
    ):
        self.tokens = list(
            tokens or []
        )

    # ========================================================
    # PUBLIC API
    # ========================================================

    def parse(self) -> List[ParsedLine]:
        """
        Parse all tokens.

        Returns:
            List[ParsedLine]
        """

        parsed_lines = []

        grouped = group_tokens_by_line(
            self.tokens
        )

        for line_tokens in grouped:

            parsed_line = (
                self.parse_line(
                    line_tokens
                )
            )

            parsed_lines.append(
                parsed_line
            )

        return parsed_lines

    def parse_line(
        self,
        tokens: Sequence[Token],
    ) -> ParsedLine:
        """
        Parse one source line.
        """

        if not tokens:
            raise ParserError(
                "Cannot parse empty token list"
            )

        first = tokens[0]

        result = ParsedLine(
            line=first.line,
            column=first.column,
        )

        index = 0

        # ----------------------------------------------------
        # Label
        #
        # Example:
        #
        # START:
        #
        # START: NOP
        # ----------------------------------------------------

        if (
            index + 1 < len(tokens)
            and tokens[index].type
            == TokenType.SYMBOL
            and tokens[index + 1].type
            == TokenType.COLON
        ):

            result.label = (
                tokens[index]
                .value
                .upper()
            )

            index += 2

        # ----------------------------------------------------
        # Label-only line
        # ----------------------------------------------------

        if index >= len(tokens):

            return result

        current = tokens[index]

        # ----------------------------------------------------
        # Instruction
        # ----------------------------------------------------

        if (
            current.type
            == TokenType.INSTRUCTION
        ):

            result.instruction = (
                current.value.upper()
            )

            index += 1

            operands = self.parse_operands(
                tokens[index:]
            )

            result.operands = operands

            self.validate_instruction(
                result
            )

            return result

        # ----------------------------------------------------
        # Directive
        # ----------------------------------------------------

        if (
            current.type
            == TokenType.DIRECTIVE
        ):

            result.directive = (
                current.value.upper()
            )

            index += 1

            directive_operands = (
                self.parse_operands(
                    tokens[index:]
                )
            )

            result.directive_operands = (
                directive_operands
            )

            self.validate_directive(
                result
            )

            return result

        # ----------------------------------------------------
        # Unexpected token
        # ----------------------------------------------------

        raise ParserError(
            (
                f"Expected instruction or "
                f"directive, got "
                f"{current.value!r}"
            ),
            current.line,
            current.column,
        )

    # ========================================================
    # OPERAND PARSING
    # ========================================================

    def parse_operands(
        self,
        tokens: Sequence[Token],
    ) -> List[Operand]:
        """
        Parse comma-separated operands.

        Example:

            LOAD 0x10

        Result:

            [
                Operand(
                    kind=NUMBER,
                    value="0x10"
                )
            ]
        """

        if not tokens:
            return []

        operands = []

        expecting_operand = True

        index = 0

        while index < len(tokens):

            token = tokens[index]

            # ------------------------------------------------
            # Comma
            # ------------------------------------------------

            if (
                token.type
                == TokenType.COMMA
            ):

                if expecting_operand:

                    raise ParserError(
                        "Unexpected comma",
                        token.line,
                        token.column,
                    )

                expecting_operand = True

                index += 1

                continue

            # ------------------------------------------------
            # Operand
            # ------------------------------------------------

            if not expecting_operand:

                raise ParserError(
                    (
                        "Expected comma "
                        "between operands"
                    ),
                    token.line,
                    token.column,
                )

            operand = (
                self.parse_operand(
                    token
                )
            )

            operands.append(
                operand
            )

            expecting_operand = False

            index += 1

        # ----------------------------------------------------
        # Trailing comma
        # ----------------------------------------------------

        if expecting_operand:

            last_token = tokens[-1]

            raise ParserError(
                "Trailing comma",
                last_token.line,
                last_token.column,
            )

        return operands

    # ========================================================
    # SINGLE OPERAND
    # ========================================================

    @staticmethod
    def parse_operand(
        token: Token,
    ) -> Operand:
        """
        Convert a lexer Token into Operand.
        """

        # ----------------------------------------------------
        # Number
        # ----------------------------------------------------

        if (
            token.type
            == TokenType.NUMBER
        ):

            numeric_value = (
                parse_number(
                    token.value
                )
            )

            return Operand(
                kind=OperandKind.NUMBER,
                value=token.value,
                line=token.line,
                column=token.column,
                numeric_value=numeric_value,
            )

        # ----------------------------------------------------
        # Register
        # ----------------------------------------------------

        if (
            token.type
            == TokenType.REGISTER
        ):

            return Operand(
                kind=OperandKind.REGISTER,
                value=token.value.upper(),
                line=token.line,
                column=token.column,
            )

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if (
            token.type
            == TokenType.SYMBOL
        ):

            return Operand(
                kind=OperandKind.SYMBOL,
                value=token.value.upper(),
                line=token.line,
                column=token.column,
            )

        # ----------------------------------------------------
        # String
        # ----------------------------------------------------

        if (
            token.type
            == TokenType.STRING
        ):

            return Operand(
                kind=OperandKind.STRING,
                value=token.value,
                line=token.line,
                column=token.column,
            )

        # ----------------------------------------------------
        # Invalid operand
        # ----------------------------------------------------

        raise ParserError(
            (
                f"Invalid operand "
                f"{token.value!r}"
            ),
            token.line,
            token.column,
        )

    # ========================================================
    # INSTRUCTION VALIDATION
    # ========================================================

    @staticmethod
    def validate_instruction(
        parsed: ParsedLine,
    ) -> None:
        """
        Validate instruction operands.
        """

        if (
            parsed.instruction
            is None
        ):
            return

        definition = get_instruction(
            parsed.instruction
        )

        try:

            validate_operand_count(
                parsed.instruction,
                parsed.operands,
            )

        except ValueError as error:

            raise ParserError(
                str(error),
                parsed.line,
                parsed.column,
            ) from error

        # ----------------------------------------------------
        # Validate operand types
        # ----------------------------------------------------

        for index, operand in enumerate(
            parsed.operands
        ):

            expected_type = (
                definition
                .operand_types[index]
            )

            if not (
                Parser.operand_matches_type(
                    operand,
                    expected_type,
                )
            ):

                raise ParserError(
                    (
                        f"{parsed.instruction} "
                        f"operand {index + 1} "
                        f"must be "
                        f"{expected_type.value}, "
                        f"got "
                        f"{operand.kind.value}"
                    ),
                    operand.line,
                    operand.column,
                )

        # ----------------------------------------------------
        # Validate 8-bit immediate
        # ----------------------------------------------------

        for operand in (
            parsed.operands
        ):

            if (
                operand.is_number()
                and operand.numeric_value
                is not None
            ):

                if not (
                    0
                    <= operand.numeric_value
                    <= 0xFF
                ):

                    raise ParserError(
                        (
                            f"Numeric operand "
                            f"{operand.value} "
                            f"is outside "
                            f"8-bit range "
                            f"0x00-0xFF"
                        ),
                        operand.line,
                        operand.column,
                    )

    # ========================================================
    # OPERAND TYPE MATCHING
    # ========================================================

    @staticmethod
    def operand_matches_type(
        operand: Operand,
        expected: OperandType,
    ) -> bool:
        """
        Check whether operand matches
        expected operand type.

        Symbols are allowed for:
            - immediate
            - address
            - label

        because the symbol may be resolved
        during the first or second pass.
        """

        if expected == OperandType.NONE:

            return False

        if expected == OperandType.REGISTER:

            return operand.is_register()

        if expected == OperandType.IMMEDIATE:

            return (
                operand.is_number()
                or operand.is_symbol()
            )

        if expected == OperandType.ADDRESS:

            return (
                operand.is_number()
                or operand.is_symbol()
            )

        if expected == OperandType.LABEL:

            return operand.is_symbol()

        if expected == OperandType.SYMBOL:

            return operand.is_symbol()

        return False

    # ========================================================
    # DIRECTIVE VALIDATION
    # ========================================================

    @staticmethod
    def validate_directive(
        parsed: ParsedLine,
    ) -> None:
        """
        Validate assembler directives.
        """

        directive = (
            parsed.directive
        )

        if directive is None:
            return

        operands = (
            parsed.directive_operands
        )

        # ----------------------------------------------------
        # .ORG
        #
        # Example:
        #
        # .ORG 0x00
        # ----------------------------------------------------

        if directive == ".ORG":

            if len(operands) != 1:

                raise ParserError(
                    ".ORG expects exactly one operand",
                    parsed.line,
                    parsed.column,
                )

            operand = operands[0]

            if not (
                operand.is_number()
                or operand.is_symbol()
            ):

                raise ParserError(
                    (
                        ".ORG requires "
                        "a number or symbol"
                    ),
                    operand.line,
                    operand.column,
                )

            if (
                operand.is_number()
                and operand.numeric_value
                is not None
                and not (
                    0
                    <= operand.numeric_value
                    <= 0xFF
                )
            ):

                raise ParserError(
                    (
                        ".ORG address must "
                        "be between "
                        "0x00 and 0xFF"
                    ),
                    operand.line,
                    operand.column,
                )

            return

        # ----------------------------------------------------
        # .DB / .BYTE
        #
        # Example:
        #
        # .DB 0x10, 0x20, 0x30
        #
        # .BYTE "HELLO"
        # ----------------------------------------------------

        if directive in (
            ".DB",
            ".BYTE",
        ):

            if not operands:

                raise ParserError(
                    (
                        f"{directive} "
                        f"requires at least "
                        f"one operand"
                    ),
                    parsed.line,
                    parsed.column,
                )

            for operand in operands:

                if operand.is_string():

                    continue

                if (
                    operand.is_number()
                    and operand.numeric_value
                    is not None
                ):

                    if not (
                        0
                 
