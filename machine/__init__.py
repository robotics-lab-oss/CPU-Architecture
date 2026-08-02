"""
machine

MiniCPU 8-bit Machine Code Package

This package provides tools for handling
MiniCPU machine-code representations.

Modules:
    binary_format.py
        Binary machine-code conversion.

    hex_format.py
        Intel HEX / hexadecimal representation
        utilities.

    loader.py
        Load machine code into CPU memory.

    memory_image.py
        Represent and manage a complete
        machine-memory image.

Architecture:
    - 8-bit data
    - 8-bit address
    - 256-byte address space
    - 16 instructions
"""

from __future__ import annotations


# ============================================================
# PACKAGE VERSION
# ============================================================

__version__ = "1.0.0"


# ============================================================
# ARCHITECTURE INFORMATION
# ============================================================

ARCHITECTURE_NAME = (
    "MiniCPU"
)

ARCHITECTURE_VERSION = (
    "1.0"
)

DATA_WIDTH = 8

ADDRESS_WIDTH = 8

MEMORY_SIZE = 256

INSTRUCTION_COUNT = 16


# ============================================================
# PACKAGE METADATA
# ============================================================

PACKAGE_NAME = (
    "MiniCPU Machine"
)

DESCRIPTION = (
    "Machine-code and memory-image "
    "utilities for the MiniCPU 8-bit "
    "CPU architecture."
)


# ============================================================
# OPTIONAL MODULE IMPORTS
#
# These imports are intentionally protected so that
# importing the machine package does not fail if
# a module is being developed independently.
# ============================================================

try:

    from .binary_format import (
        BinaryFormat,
    )

except ImportError:

    BinaryFormat = None


try:

    from .hex_format import (
        HexFormat,
    )

except ImportError:

    HexFormat = None


try:

    from .loader import (
        MachineLoader,
    )

except ImportError:

    MachineLoader = None


try:

    from .memory_image import (
        MemoryImage,
    )

except ImportError:

    MemoryImage = None


# ============================================================
# PACKAGE INFORMATION
# ============================================================

def get_architecture_info() -> dict:
    """
    Return MiniCPU machine architecture information.

    Returns:
        Dictionary containing architecture metadata.
    """

    return {
        "name": ARCHITECTURE_NAME,
        "version": ARCHITECTURE_VERSION,
        "package_version": __version__,
        "data_width": DATA_WIDTH,
        "address_width": ADDRESS_WIDTH,
        "memory_size": MEMORY_SIZE,
        "instruction_count": (
            INSTRUCTION_COUNT
        ),
    }


# ============================================================
# PACKAGE STATUS
# ============================================================

def get_package_status() -> dict:
    """
    Return availability status of machine modules.

    This is useful during development to check
    which machine modules are currently importable.
    """

    return {
        "binary_format": (
            BinaryFormat is not None
        ),
        "hex_format": (
            HexFormat is not None
        ),
        "loader": (
            MachineLoader is not None
        ),
        "memory_image": (
            MemoryImage is not None
        ),
    }


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    # Package metadata
    "__version__",
    "PACKAGE_NAME",
    "DESCRIPTION",

    # Architecture information
    "ARCHITECTURE_NAME",
    "ARCHITECTURE_VERSION",
    "DATA_WIDTH",
    "ADDRESS_WIDTH",
    "MEMORY_SIZE",
    "INSTRUCTION_COUNT",

    # Classes
    "BinaryFormat",
    "HexFormat",
    "MachineLoader",
    "MemoryImage",

    # Functions
    "get_architecture_info",
    "get_package_status",
]
