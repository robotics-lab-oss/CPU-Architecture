"""
simulator

MiniCPU 8-bit CPU Simulator Package

This package provides:

    - CPU simulation
    - Program execution
    - Single-step execution
    - Debugging
    - Breakpoints
    - Execution tracing
    - Memory inspection
    - Simulator CLI

Package structure:

    simulator/
    ├── __init__.py
    ├── simulator.py
    ├── runner.py
    ├── debugger.py
    ├── breakpoints.py
    ├── trace.py
    ├── memory_view.py
    └── cli.py

The simulator works with the MiniCPU
8-bit CPU architecture.
"""

from __future__ import annotations


# ============================================================
# PACKAGE VERSION
# ============================================================

__version__ = "1.0.0"

__author__ = "MiniCPU Project"


# ============================================================
# PACKAGE INFORMATION
# ============================================================

NAME = "MiniCPU Simulator"

DESCRIPTION = (
    "Simulator and debugging environment "
    "for the MiniCPU 8-bit architecture."
)


# ============================================================
# LAZY / SAFE IMPORTS
# ============================================================

# Importing all modules directly here can create
# circular-import problems while the project is
# still being developed.
#
# Therefore, public classes are exposed through
# lazy imports using __getattr__.


def __getattr__(
    name: str,
):
    """
    Lazily expose simulator package classes.

    This avoids unnecessary imports and helps
    prevent circular dependencies.
    """

    if name == "Simulator":

        from .simulator import Simulator

        return Simulator

    if name == "Runner":

        from .runner import Runner

        return Runner

    if name == "Debugger":

        from .debugger import Debugger

        return Debugger

    if name == "BreakpointManager":

        from .breakpoints import (
            BreakpointManager,
        )

        return BreakpointManager

    if name == "Breakpoint":

        from .breakpoints import (
            Breakpoint,
        )

        return Breakpoint

    if name == "Trace":

        from .trace import Trace

        return Trace

    if name == "TraceEntry":

        from .trace import TraceEntry

        return TraceEntry

    if name == "MemoryView":

        from .memory_view import (
            MemoryView,
        )

        return MemoryView

    raise AttributeError(
        f"module {__name__!r} "
        f"has no attribute {name!r}"
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Simulator",
    "Runner",
    "Debugger",
    "BreakpointManager",
    "Breakpoint",
    "Trace",
    "TraceEntry",
    "MemoryView",
    "__version__",
    "__author__",
    "NAME",
    "DESCRIPTION",
]


# ============================================================
# PACKAGE INFORMATION FUNCTION
# ============================================================

def get_info() -> dict:
    """
    Return simulator package information.

    Returns:
        Dictionary containing package metadata.
    """

    return {
        "name": NAME,
        "version": __version__,
        "author": __author__,
        "description": DESCRIPTION,
    }


# ============================================================
# VERSION FUNCTION
# ============================================================

def get_version() -> str:
    """
    Return current simulator version.
    """

    return __version__


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        NAME
    )

    print(
        "================================"
    )

    print(
        f"Version     : "
        f"{__version__}"
    )

    print(
        f"Author      : "
        f"{__author__}"
    )

    print(
        f"Description : "
        f"{DESCRIPTION}"
    )

    print(
        "================================"
    )
