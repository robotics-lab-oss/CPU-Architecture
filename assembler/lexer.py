"""
lexer.py

MiniCPU 8-bit CPU Architecture
Assembly Language Lexer

Responsibilities:
    - Read assembly source code
    - Remove comments
    - Detect labels
    - Detect instructions
    - Detect directives
    - Detect registers
    - Detect numeric literals
    - Detect symbols
    - Preserve source line numbers

The lexer does not:
    - Resolve labels
    - Calculate addresses
    - Generate machine code
    - Execute instructions

Those responsibilities belong to later assembler stages.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable, List, Optional

from opcode import is_valid_instruction


# ============================================================
# TOKEN TYPES
# ============================================================

class TokenType(str, Enum):
    INSTRUCTION = "INSTRUCTION"
    REGISTER = "REGISTER"
    NUMBER = "NUMBER"
    SYMBOL = "SYMBOL"
    LABEL = "LABEL"
    DIRECTIVE = "DIRECTIVE"
    COMMA = "COMMA"
    COLON = "COLON"
    STRING = "STRING"


# ============================================================
# TOKEN
# ============================================================

@dataclass(frozen=True)
class Token:
    """
    Represents one lexical token.
    """

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return (
            f"Token("
            f"type={self.type.value!r}, "
            f"value={self.value!r}, "
            f"line={self.line}, "
            f"column={self.column}"
            f")"
        )


# ============================================================
# LEXER ERROR
# ============================================================

class LexerError(Exception):
    """
    Raised when invalid assembly syntax is found
    during lexical analysis.
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
# REGISTERS
# ============================================================

# The exact CPU register architecture has not yet been
# defined in the provided opcode.py.
#
# These common register names are recognized by the lexer.
# This can be changed later when the CPU register specification
# is finalized.

REGISTERS = {
    "A",
    "B",
    "C",
    "D",
    "R0",
    "R1",
    "R2",
    "R3",
    "R4",
    "R5",
    "R6",
    "R7",
    "R8",
    "R9",
    "R10",
    "R11",
    "R12",
    "R13",
    "R14",
    "R15",
}


# ============================================================
# DIRECTIVES
# ============================================================

DIRECTIVES = {
    ".ORG",
    ".DB",
    ".BYTE",
    ".EQU",
    "EQU",
}


# ============================================================
# LEXICAL PATTERNS
# ============================================================

IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*$"
)


NUMBER_PATTERN = re.compile(
    r"""
    ^
    (?:
        0[xX][0-9A-Fa-f]+
        |
        0[bB][01]+
        |
        0[oO][0-7]+
        |
        [0-9]+
    )
    $
    """,
    re.VERBOSE,
)


# ============================================================
# LEXER
# ============================================================

class Lexer:
    """
    MiniCPU Assembly Lexer.

    Example:

        START:
            LOAD 0x10
            ADD 5
            JMP LOOP
            HALT

    The lexer converts source code into Token objects.
    """

    def __init__(
        self,
        source: str = "",
    ):
        if not isinstance(
            source,
            str,
        ):
            raise TypeError(
                "source must be a string"
            )

        self.source = source

    # ========================================================
    # PUBLIC API
    # ========================================================

    def tokenize(self) -> List[Token]:
        """
        Tokenize the complete source.

        Returns:
            List[Token]
        """

        tokens: List[Token] = []

        lines = self.source.splitlines()

        for line_number, line in enumerate(
            lines,
            start=1,
        ):
            line_tokens = self.tokenize_line(
                line,
                line_number,
            )

            tokens.extend(
                line_tokens
            )

        return tokens

    def tokenize_line(
        self,
        line: str,
        line_number: int,
    ) -> List[Token]:
        """
        Tokenize a single source line.
        """

        tokens: List[Token] = []

        cleaned = self.remove_comment(
            line
        )

        if not cleaned.strip():
            return tokens

        i = 0
        length = len(cleaned)

        while i < length:

            char = cleaned[i]

            # ------------------------------------------------
            # Whitespace
            # ------------------------------------------------

            if char.isspace():
                i += 1
                continue

            column = i + 1

            # ------------------------------------------------
            # Comma
            # ------------------------------------------------

            if char == ",":
                tokens.append(
                    Token(
                        type=TokenType.COMMA,
                        value=",",
                        line=line_number,
                        column=column,
                    )
                )

                i += 1
                continue

            # ------------------------------------------------
            # Colon
            # ------------------------------------------------

            if char == ":":
                tokens.append(
                    Token(
                        type=TokenType.COLON,
                        value=":",
                        line=line_number,
                        column=column,
                    )
                )

                i += 1
                continue

            # ------------------------------------------------
            # String
            # ------------------------------------------------

            if char in (
                '"',
                "'",
            ):

                token, i = (
                    self.read_string(
                        cleaned,
                        i,
                        line_number,
                    )
                )

                tokens.append(token)

                continue

            # ------------------------------------------------
            # Identifier / Number / Directive
            # ------------------------------------------------

            start = i

            while (
                i < length
                and not cleaned[i].isspace()
                and cleaned[i]
                not in ",:"
            ):
                i += 1

            value = cleaned[
                start:i
            ]

            if not value:
                raise LexerError(
                    "Unexpected character",
                    line_number,
                    column,
                )

            token = self.classify(
                value,
                line_number,
                column,
            )

            tokens.append(token)

        return tokens

    # ========================================================
    # COMMENT HANDLING
    # ========================================================

    @staticmethod
    def remove_comment(
        line: str,
    ) -> str:
        """
        Remove comments from a source line.

        Supported:
            ; comment
            # comment

        Comment markers inside quoted strings
        are preserved.
        """

        in_string = False
        quote = None

        for index, char in enumerate(
            line
        ):

            if char in (
                '"',
                "'",
            ):

                if not in_string:
                    in_string = True
                    quote = char

                elif char == quote:
                    in_string = False
                    quote = None

                continue

            if (
                not in_string
                and char in (
                    ";",
                    "#",
                )
            ):
                return line[:index]

        return line

    # ========================================================
    # STRING READER
    # ========================================================

    def read_string(
        self,
        line: str,
        start: int,
        line_number: int,
    ):
        """
        Read a quoted string.
        """

        quote = line[start]

        i = start + 1

        value = []

        while i < len(line):

            char = line[i]

            if char == quote:

                token = Token(
                    type=TokenType.STRING,
                    value="".join(value),
                    line=line_number,
                    column=start + 1,
                )

                return (
                    token,
                    i + 1,
                )

            if char == "\\":

                if i + 1 >= len(line):
                    raise LexerError(
                        "Incomplete escape sequence",
                        line_number,
                        i + 1,
                    )

                next_char = line[
                    i + 1
                ]

                escape_map = {
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                    "\\": "\\",
                    '"': '"',
                    "'": "'",
                }

                value.append(
                    escape_map.get(
                        next_char,
                        next_char,
                    )
                )

                i += 2
                continue

            value.append(char)

            i += 1

        raise LexerError(
            "Unterminated string literal",
            line_number,
            start + 1,
        )

    # ========================================================
    # TOKEN CLASSIFICATION
    # ========================================================

    @staticmethod
    def classify(
        value: str,
        line_number: int,
        column: int,
    ) -> Token:
        """
        Convert raw text into a Token.
        """

        normalized = value.upper()

        # ----------------------------------------------------
        # Directive
        # ----------------------------------------------------

        if normalized in DIRECTIVES:

            return Token(
                type=TokenType.DIRECTIVE,
                value=normalized,
                line=line_number,
                column=column,
            )

        # ----------------------------------------------------
        # Instruction
        # ----------------------------------------------------

        if is_valid_instruction(
            normalized
        ):

            return Token(
                type=TokenType.INSTRUCTION,
                value=normalized,
                line=line_number,
                column=column,
            )

        # ----------------------------------------------------
        # Register
        # ----------------------------------------------------

        if normalized in REGISTERS:

            return Token(
                type=TokenType.REGISTER,
                value=normalized,
                line=line_number,
                column=column,
            )

        # ----------------------------------------------------
        # Number
        # ----------------------------------------------------

        if NUMBER_PATTERN.match(
            value
        ):

            return Token(
                type=TokenType.NUMBER,
                value=value,
                line=line_number,
                column=column,
            )

        # ----------------------------------------------------
        # Symbol
        # ----------------------------------------------------

        if IDENTIFIER_PATTERN.match(
            value
        ):

            return Token(
                type=TokenType.SYMBOL,
                value=normalized,
                line=line_number,
                column=column,
            )

        # ----------------------------------------------------
        # Invalid token
        # ----------------------------------------------------

        raise LexerError(
            f"Invalid token: {value!r}",
            line_number,
            column,
        )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def tokenize(
    source: str,
) -> List[Token]:
    """
    Convenience function.

    Example:

        tokens = tokenize(source)
    """

    lexer = Lexer(source)

    return lexer.tokenize()


def tokenize_file(
    filename: str,
    encoding: str = "utf-8",
) -> List[Token]:
    """
    Read and tokenize an assembly file.
    """

    with open(
        filename,
        "r",
        encoding=encoding,
    ) as file:

        source = file.read()

    return tokenize(
        source
    )


# ============================================================
# TOKEN GROUPING
# ============================================================

def group_tokens_by_line(
    tokens: Iterable[Token],
) -> List[List[Token]]:
    """
    Group tokens according to source line.

    This is useful for the parser.
    """

    grouped: List[List[Token]] = []

    current_line = None

    current_group: List[Token] = []

    for token in tokens:

        if (
            current_line is None
            or token.line
            != current_line
        ):

            if current_group:
                grouped.append(
                    current_group
                )

            current_group = [
                token
            ]

            current_line = token.line

        else:

            current_group.append(
                token
            )

    if current_group:
        grouped.append(
            current_group
        )

    return grouped


# ============================================================
# DEBUG OUTPUT
# ============================================================

def dump_tokens(
    tokens: Iterable[Token],
) -> str:
    """
    Convert tokens to readable text.
    """

    lines = []

    for token in tokens:

        lines.append(
            f"Line {token.line}, "
            f"Column {token.column}: "
            f"{token.type.value:<12} "
            f"{token.value!r}"
        )

    return "\n".join(
        lines
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "TokenType",
    "Token",
    "LexerError",
    "REGISTERS",
    "DIRECTIVES",
    "Lexer",
    "tokenize",
    "tokenize_file",
    "group_tokens_by_line",
    "dump_tokens",
]


# ============================================================
# TEST / DEBUG
# ============================================================

if __name__ == "__main__":

    example_source = """
; MiniCPU example

.ORG 0x00

START:
    LOAD 0x10
    ADD 5
    STORE 0x80
    JMP LOOP

LOOP:
    INC
    JZ START
    OUT
    HALT
"""

    try:

        lexer = Lexer(
            example_source
        )

        tokens = lexer.tokenize()

        print(
            dump_tokens(tokens)
        )

    except LexerError as error:

        print(
            f"Lexer Error: {error}"
    )
