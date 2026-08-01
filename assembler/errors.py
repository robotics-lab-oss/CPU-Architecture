"""
errors.py

MiniCPU 8-bit CPU Architecture
Assembler Error System

Centralized error and diagnostic definitions for:

    - Lexer
    - Parser
    - Symbol Table
    - First Pass
    - Second Pass
    - Encoder
    - Assembler

Features:

    - Source location tracking
    - Line and column information
    - Error codes
    - Warning support
    - Error collection
    - Multiple diagnostics
    - Human-readable formatting
    - Exception hierarchy
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Optional


# ============================================================
# ERROR SEVERITY
# ============================================================

class Severity(str, Enum):
    """
    Diagnostic severity levels.
    """

    ERROR = "error"

    WARNING = "warning"

    INFO = "info"


# ============================================================
# ERROR CODES
# ============================================================

class ErrorCode(str, Enum):
    """
    Standard MiniCPU assembler diagnostic codes.
    """

    # --------------------------------------------------------
    # General
    # --------------------------------------------------------

    UNKNOWN_ERROR = "E000"

    INVALID_ARGUMENT = "E001"

    INTERNAL_ERROR = "E002"

    # --------------------------------------------------------
    # Lexer
    # --------------------------------------------------------

    INVALID_TOKEN = "E100"

    INVALID_CHARACTER = "E101"

    UNTERMINATED_STRING = "E102"

    INVALID_NUMBER = "E103"

    INVALID_IDENTIFIER = "E104"

    # --------------------------------------------------------
    # Parser
    # --------------------------------------------------------

    UNEXPECTED_TOKEN = "E200"

    EXPECTED_INSTRUCTION = "E201"

    EXPECTED_OPERAND = "E202"

    INVALID_OPERAND = "E203"

    WRONG_OPERAND_COUNT = "E204"

    INVALID_DIRECTIVE = "E205"

    INVALID_SYNTAX = "E206"

    UNEXPECTED_COMMA = "E207"

    TRAILING_COMMA = "E208"

    # --------------------------------------------------------
    # Symbol Table
    # --------------------------------------------------------

    DUPLICATE_SYMBOL = "E300"

    UNDEFINED_SYMBOL = "E301"

    INVALID_SYMBOL = "E302"

    SYMBOL_OUT_OF_RANGE = "E303"

    DUPLICATE_LABEL = "E304"

    DUPLICATE_EQU = "E305"

    # --------------------------------------------------------
    # Address / Memory
    # --------------------------------------------------------

    ADDRESS_OUT_OF_RANGE = "E400"

    PROGRAM_TOO_LARGE = "E401"

    INVALID_ORIGIN = "E402"

    MEMORY_OVERFLOW = "E403"

    # --------------------------------------------------------
    # Instruction
    # --------------------------------------------------------

    UNKNOWN_INSTRUCTION = "E500"

    INVALID_INSTRUCTION = "E501"

    INVALID_OPCODE = "E502"

    INVALID_INSTRUCTION_SIZE = "E503"

    # --------------------------------------------------------
    # Encoding
    # --------------------------------------------------------

    ENCODING_ERROR = "E600"

    OPERAND_OUT_OF_RANGE = "E601"

    INVALID_OPERAND_TYPE = "E602"

    MISSING_OPERAND = "E603"

    EXTRA_OPERAND = "E604"

    # --------------------------------------------------------
    # Warnings
    # --------------------------------------------------------

    UNUSED_SYMBOL = "W001"

    DUPLICATE_SYMBOL_WARNING = "W002"

    ADDRESS_ALIGNMENT = "W003"


# ============================================================
# SOURCE LOCATION
# ============================================================

@dataclass(frozen=True)
class SourceLocation:
    """
    Represents a location in assembly source code.
    """

    filename: Optional[str] = None

    line: Optional[int] = None

    column: Optional[int] = None

    source_line: Optional[str] = None

    def format(self) -> str:
        """
        Return human-readable source location.
        """

        parts = []

        if self.filename:
            parts.append(
                self.filename
            )

        if self.line is not None:

            if parts:

                parts[-1] = (
                    f"{parts[-1]}:"
                    f"{self.line}"
                )

            else:

                parts.append(
                    f"line {self.line}"
                )

        if (
            self.column is not None
            and self.line is not None
        ):

            if parts:

                parts[-1] = (
                    f"{parts[-1]}:"
                    f"{self.column}"
                )

        return ":".join(
            parts
        )


# ============================================================
# DIAGNOSTIC
# ============================================================

@dataclass
class Diagnostic:
    """
    Represents one assembler diagnostic.
    """

    severity: Severity

    code: ErrorCode

    message: str

    location: Optional[
        SourceLocation
    ] = None

    hint: Optional[str] = None

    def format(
        self,
        show_source: bool = True,
    ) -> str:
        """
        Format diagnostic for terminal output.
        """

        location_text = ""

        if self.location:

            location_text = (
                self.location.format()
            )

            if location_text:

                location_text += ": "

        result = (
            f"{location_text}"
            f"{self.severity.value}: "
            f"{self.code.value}: "
            f"{self.message}"
        )

        if (
            self.hint
            and self.hint.strip()
        ):

            result += (
                f"\n  hint: "
                f"{self.hint}"
            )

        if (
            show_source
            and self.location
            and self.location.source_line
        ):

            result += (
                f"\n"
                f"  | "
                f"{self.location.source_line}"
            )

            if (
                self.location.column
                is not None
            ):

                result += (
                    "\n"
                    "  | "
                    + " "
                    * max(
                        0,
                        self.location.column - 1,
                    )
                    + "^"
                )

        return result

    def is_error(self) -> bool:
        """
        Return True for errors.
        """

        return (
            self.severity
            == Severity.ERROR
        )

    def is_warning(self) -> bool:
        """
        Return True for warnings.
        """

        return (
            self.severity
            == Severity.WARNING
        )


# ============================================================
# BASE ASSEMBLER ERROR
# ============================================================

class AssemblerError(Exception):
    """
    Base exception for all assembler errors.
    """

    default_code = (
        ErrorCode.UNKNOWN_ERROR
    )

    def __init__(
        self,
        message: str,
        *,
        code: Optional[
            ErrorCode
        ] = None,
        filename: Optional[
            str
        ] = None,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        source_line: Optional[
            str
        ] = None,
        hint: Optional[
            str
        ] = None,
    ):

        self.message = message

        self.code = (
            code
            or self.default_code
        )

        self.location = (
            SourceLocation(
                filename=filename,
                line=line,
                column=column,
                source_line=source_line,
            )
        )

        self.hint = hint

        super().__init__(
            self.format()
        )

    def diagnostic(
        self,
    ) -> Diagnostic:
        """
        Convert exception into Diagnostic.
        """

        return Diagnostic(
            severity=Severity.ERROR,
            code=self.code,
            message=self.message,
            location=self.location,
            hint=self.hint,
        )

    def format(self) -> str:
        """
        Return formatted error.
        """

        return self.diagnostic().format()


# ============================================================
# LEXER ERROR
# ============================================================

class LexerError(
    AssemblerError
):
    """
    Error raised during lexical analysis.
    """

    default_code = (
        ErrorCode.INVALID_TOKEN
    )

    def __init__(
        self,
        message: str,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        *,
        filename: Optional[
            str
        ] = None,
        source_line: Optional[
            str
        ] = None,
        code: ErrorCode = (
            ErrorCode.INVALID_TOKEN
        ),
        hint: Optional[
            str
        ] = None,
    ):

        super().__init__(
            message,
            code=code,
            filename=filename,
            line=line,
            column=column,
            source_line=source_line,
            hint=hint,
        )


# ============================================================
# PARSER ERROR
# ============================================================

class ParserError(
    AssemblerError
):
    """
    Error raised during parsing.
    """

    default_code = (
        ErrorCode.INVALID_SYNTAX
    )

    def __init__(
        self,
        message: str,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        *,
        filename: Optional[
            str
        ] = None,
        source_line: Optional[
            str
        ] = None,
        code: ErrorCode = (
            ErrorCode.INVALID_SYNTAX
        ),
        hint: Optional[
            str
        ] = None,
    ):

        super().__init__(
            message,
            code=code,
            filename=filename,
            line=line,
            column=column,
            source_line=source_line,
            hint=hint,
        )


# ============================================================
# SYMBOL ERROR
# ============================================================

class SymbolError(
    AssemblerError
):
    """
    Error related to symbols and labels.
    """

    default_code = (
        ErrorCode.INVALID_SYMBOL
    )

    def __init__(
        self,
        message: str,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        *,
        filename: Optional[
            str
        ] = None,
        source_line: Optional[
            str
        ] = None,
        code: ErrorCode = (
            ErrorCode.INVALID_SYMBOL
        ),
        hint: Optional[
            str
        ] = None,
    ):

        super().__init__(
            message,
            code=code,
            filename=filename,
            line=line,
            column=column,
            source_line=source_line,
            hint=hint,
        )


# ============================================================
# UNDEFINED SYMBOL ERROR
# ============================================================

class UndefinedSymbolError(
    SymbolError
):
    """
    Raised when a symbol cannot be resolved.
    """

    default_code = (
        ErrorCode.UNDEFINED_SYMBOL
    )

    def __init__(
        self,
        symbol: str,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        *,
        filename: Optional[
            str
        ] = None,
        source_line: Optional[
            str
        ] = None,
    ):

        super().__init__(
            (
                f"Undefined symbol: "
                f"{symbol}"
            ),
            line=line,
            column=column,
            filename=filename,
            source_line=source_line,
            code=(
                ErrorCode.UNDEFINED_SYMBOL
            ),
            hint=(
                "Check the spelling of the "
                "label or define it before use."
            ),
        )

        self.symbol = symbol


# ============================================================
# DUPLICATE SYMBOL ERROR
# ============================================================

class DuplicateSymbolError(
    SymbolError
):
    """
    Raised when a symbol is defined twice.
    """

    default_code = (
        ErrorCode.DUPLICATE_SYMBOL
    )

    def __init__(
        self,
        symbol: str,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        *,
        filename: Optional[
            str
        ] = None,
        source_line: Optional[
            str
        ] = None,
    ):

        super().__init__(
            (
                f"Duplicate symbol: "
                f"{symbol}"
            ),
            line=line,
            column=column,
            filename=filename,
            source_line=source_line,
            code=(
                ErrorCode.DUPLICATE_SYMBOL
            ),
            hint=(
                "Each label or constant "
                "must be defined only once."
            ),
        )

        self.symbol = symbol


# ============================================================
# ENCODING ERROR
# ============================================================

class EncodingError(
    AssemblerError
):
    """
    Error raised while converting
    parsed instructions to machine code.
    """

    default_code = (
        ErrorCode.ENCODING_ERROR
    )

    def __init__(
        self,
        message: str,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        *,
        filename: Optional[
            str
        ] = None,
        source_line: Optional[
            str
        ] = None,
        code: ErrorCode = (
            ErrorCode.ENCODING_ERROR
        ),
        hint: Optional[
            str
        ] = None,
    ):

        super().__init__(
            message,
            code=code,
            filename=filename,
            line=line,
            column=column,
            source_line=source_line,
            hint=hint,
        )


# ============================================================
# ADDRESS ERROR
# ============================================================

class AddressError(
    AssemblerError
):
    """
    Error related to memory addresses.
    """

    default_code = (
        ErrorCode.ADDRESS_OUT_OF_RANGE
    )

    def __init__(
        self,
        message: str,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        *,
        filename: Optional[
            str
        ] = None,
        source_line: Optional[
            str
        ] = None,
        code: ErrorCode = (
            ErrorCode.ADDRESS_OUT_OF_RANGE
        ),
        hint: Optional[
            str
        ] = None,
    ):

        super().__init__(
            message,
            code=code,
            filename=filename,
            line=line,
            column=column,
            source_line=source_line,
            hint=hint,
        )


# ============================================================
# DIAGNOSTIC COLLECTION
# ============================================================

class DiagnosticBag:
    """
    Collect multiple diagnostics.

    This allows the assembler to report
    multiple errors in one assembly run
    instead of stopping at the first error.
    """

    def __init__(self):
        self._diagnostics: List[
            Diagnostic
        ] = []

    # --------------------------------------------------------
    # Add
    # --------------------------------------------------------

    def add(
        self,
        diagnostic: Diagnostic,
    ) -> None:

        self._diagnostics.append(
            diagnostic
        )

    # --------------------------------------------------------
    # Add Error
    # --------------------------------------------------------

    def error(
        self,
        message: str,
        code: ErrorCode = (
            ErrorCode.UNKNOWN_ERROR
        ),
        *,
        filename: Optional[
            str
        ] = None,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        source_line: Optional[
            str
        ] = None,
        hint: Optional[
            str
        ] = None,
    ) -> None:

        self.add(
            Diagnostic(
                severity=Severity.ERROR,
                code=code,
                message=message,
                location=SourceLocation(
                    filename=filename,
                    line=line,
                    column=column,
                    source_line=source_line,
                ),
                hint=hint,
            )
        )

    # --------------------------------------------------------
    # Add Warning
    # --------------------------------------------------------

    def warning(
        self,
        message: str,
        code: ErrorCode = (
            ErrorCode.UNUSED_SYMBOL
        ),
        *,
        filename: Optional[
            str
        ] = None,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        source_line: Optional[
            str
        ] = None,
        hint: Optional[
            str
        ] = None,
    ) -> None:

        self.add(
            Diagnostic(
                severity=Severity.WARNING,
                code=code,
                message=message,
                location=SourceLocation(
                    filename=filename,
                    line=line,
                    column=column,
                    source_line=source_line,
                ),
                hint=hint,
            )
        )

    # --------------------------------------------------------
    # Add Info
    # --------------------------------------------------------

    def info(
        self,
        message: str,
        code: ErrorCode = (
            ErrorCode.UNKNOWN_ERROR
        ),
        *,
        filename: Optional[
            str
        ] = None,
        line: Optional[
            int
        ] = None,
        column: Optional[
            int
        ] = None,
        source_line: Optional[
            str
        ] = None,
        hint: Optional[
            str
        ] = None,
    ) -> None:

        self.add(
            Diagnostic(
                severity=Severity.INFO,
                code=code,
                message=message,
                location=SourceLocation(
                    filename=filename,
                    line=line,
                    column=column,
                    source_line=source_line,
                ),
                hint=hint,
            )
        )

    # --------------------------------------------------------
    # Properties
    # --------------------------------------------------------

    @property
    def diagnostics(
        self,
    ) -> List[Diagnostic]:

        return list(
            self._diagnostics
        )

    @property
    def has_errors(
        self,
    ) -> bool:

        return any(
            diagnostic.is_error()
            for diagnostic
            in self._diagnostics
        )

    @property
    def has_warnings(
        self,
    ) -> bool:

        return any(
            diagnostic.is_warning()
            for diagnostic
            in self._diagnostics
        )

    @property
    def er
