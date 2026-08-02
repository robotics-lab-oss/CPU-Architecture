"""
breakpoints.py

MiniCPU 8-bit CPU Architecture
Breakpoint Management

Features:
    - Address breakpoints
    - Temporary breakpoints
    - Enable / disable breakpoints
    - Remove breakpoints
    - Clear all breakpoints
    - Breakpoint hit tracking
    - Breakpoint lookup
    - Breakpoint listing
    - 8-bit address validation

Memory address range:

    0x00 - 0xFF
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ============================================================
# BREAKPOINT
# ============================================================

@dataclass
class Breakpoint:
    """
    Represents one debugger breakpoint.

    Attributes:
        address:
            8-bit memory address.

        enabled:
            Whether breakpoint is active.

        temporary:
            Temporary breakpoint. It can be removed
            automatically after being hit.

        hits:
            Number of times breakpoint was hit.

        condition:
            Optional callable condition.

            The callable receives the Breakpoint object
            and returns True or False.
    """

    address: int

    enabled: bool = True

    temporary: bool = False

    hits: int = 0

    condition: Optional[object] = None

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __post_init__(
        self,
    ) -> None:

        self.address = (
            BreakpointManager
            .validate_address(
                self.address
            )
        )

    # ========================================================
    # ENABLE
    # ========================================================

    def enable(
        self,
    ) -> None:
        """
        Enable breakpoint.
        """

        self.enabled = True

    # ========================================================
    # DISABLE
    # ========================================================

    def disable(
        self,
    ) -> None:
        """
        Disable breakpoint.
        """

        self.enabled = False

    # ========================================================
    # IS ACTIVE
    # ========================================================

    def is_active(
        self,
    ) -> bool:
        """
        Return True if breakpoint is enabled.
        """

        return self.enabled

    # ========================================================
    # CHECK CONDITION
    # ========================================================

    def check_condition(
        self,
    ) -> bool:
        """
        Check optional breakpoint condition.

        If no condition exists, breakpoint is active.

        The condition can be:

            callable

        Example:

            condition=lambda bp: bp.hits >= 3
        """

        if not self.enabled:

            return False

        if self.condition is None:

            return True

        if not callable(
            self.condition
        ):

            raise TypeError(
                "Breakpoint condition "
                "must be callable."
            )

        return bool(
            self.condition(
                self
            )
        )

    # ========================================================
    # HIT
    # ========================================================

    def hit(
        self,
    ) -> bool:
        """
        Register a breakpoint hit.

        Returns:
            True if breakpoint should stop execution.
        """

        if not self.enabled:

            return False

        if not self.check_condition():

            return False

        self.hits += 1

        return True

    # ========================================================
    # RESET HITS
    # ========================================================

    def reset_hits(
        self,
    ) -> None:
        """
        Reset hit counter.
        """

        self.hits = 0

    # ========================================================
    # DICTIONARY
    # ========================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Convert breakpoint to dictionary.
        """

        return {
            "address": self.address,
            "address_hex": (
                f"0x{self.address:02X}"
            ),
            "enabled": self.enabled,
            "temporary": self.temporary,
            "hits": self.hits,
            "has_condition": (
                self.condition is not None
            ),
        }

    # ========================================================
    # STRING
    # ========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            "Breakpoint("
            f"address=0x"
            f"{self.address:02X}, "
            f"enabled={self.enabled}, "
            f"temporary={self.temporary}, "
            f"hits={self.hits}"
            ")"
        )


# ============================================================
# BREAKPOINT MANAGER
# ============================================================

class BreakpointManager:
    """
    Manage all MiniCPU debugger breakpoints.

    Breakpoints are stored by address.

    Example:

        manager = BreakpointManager()

        manager.add_breakpoint(
            0x20
        )

        if manager.has_breakpoint(
            0x20
        ):
            print("Breakpoint!")

    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    MIN_ADDRESS = 0x00

    MAX_ADDRESS = 0xFF

    ADDRESS_SPACE = 256

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
    ):
        """
        Initialize empty breakpoint manager.
        """

        self._breakpoints = {}

        self.last_hit = None

        self.total_hits = 0

    # ========================================================
    # ADDRESS VALIDATION
    # ========================================================

    @staticmethod
    def validate_address(
        address: int,
    ) -> int:
        """
        Validate an 8-bit address.

        Returns:
            Normalized integer address.
        """

        if not isinstance(
            address,
            int,
        ):

            raise TypeError(
                "Breakpoint address "
                "must be an integer."
            )

        if not (
            0x00
            <= address
            <= 0xFF
        ):

            raise ValueError(
                "Breakpoint address must "
                "be between 0x00 and 0xFF."
            )

        return address

    # ========================================================
    # ADD BREAKPOINT
    # ========================================================

    def add_breakpoint(
        self,
        address: int,
        temporary: bool = False,
        condition=None,
    ) -> Breakpoint:
        """
        Add a breakpoint.

        If breakpoint already exists, the existing
        breakpoint is returned.

        Args:
            address:
                8-bit memory address.

            temporary:
                Remove breakpoint automatically
                after it is hit.

            condition:
                Optional callable condition.
        """

        address = (
            self.validate_address(
                address
            )
        )

        if address in self._breakpoints:

            breakpoint = (
                self._breakpoints[
                    address
                ]
            )

            breakpoint.enabled = True

            return breakpoint

        breakpoint = Breakpoint(
            address=address,
            enabled=True,
            temporary=temporary,
            condition=condition,
        )

        self._breakpoints[
            address
        ] = breakpoint

        return breakpoint

    # ========================================================
    # SHORT ALIAS
    # ========================================================

    def add(
        self,
        address: int,
        temporary: bool = False,
        condition=None,
    ) -> Breakpoint:
        """
        Short alias for add_breakpoint().
        """

        return self.add_breakpoint(
            address=address,
            temporary=temporary,
            condition=condition,
        )

    # ========================================================
    # REMOVE
    # ========================================================

    def remove_breakpoint(
        self,
        address: int,
    ) -> bool:
        """
        Remove breakpoint.

        Returns:
            True if breakpoint existed.
        """

        address = (
            self.validate_address(
                address
            )
        )

        if address not in self._breakpoints:

            return False

        del self._breakpoints[
            address
        ]

        return True

    # ========================================================
    # SHORT REMOVE ALIAS
    # ========================================================

    def remove(
        self,
        address: int,
    ) -> bool:
        """
        Short alias for remove_breakpoint().
        """

        return self.remove_breakpoint(
            address
        )

    # ========================================================
    # HAS BREAKPOINT
    # ========================================================

    def has_breakpoint(
        self,
        address: int,
        enabled_only: bool = True,
    ) -> bool:
        """
        Check whether breakpoint exists.

        Args:
            address:
                Address to check.

            enabled_only:
                If True, disabled breakpoints
                are treated as inactive.
        """

        address = (
            self.validate_address(
                address
            )
        )

        breakpoint = (
            self._breakpoints.get(
                address
            )
        )

        if breakpoint is None:

            return False

        if enabled_only:

            return breakpoint.enabled

        return True

    # ========================================================
    # CONTAINS
    # ========================================================

    def contains(
        self,
        address: int,
    ) -> bool:
        """
        Alias for has_breakpoint().
        """

        return self.has_breakpoint(
            address
        )

    # ========================================================
    # IS BREAKPOINT
    # ========================================================

    def is_breakpoint(
        self,
        address: int,
    ) -> bool:
        """
        Alias for has_breakpoint().
        """

        return self.has_breakpoint(
            address
        )

    # ========================================================
    # GET BREAKPOINT
    # ========================================================

    def get_breakpoint(
        self,
        address: int,
    ) -> Optional[
        Breakpoint
    ]:
        """
        Return breakpoint at address.

        Returns:
            Breakpoint or None.
        """

        address = (
            self.validate_address(
                address
            )
        )

        return self._breakpoints.get(
            address
        )

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        address: int,
    ) -> Optional[
        Breakpoint
    ]:
        """
        Alias for get_breakpoint().
        """

        return self.get_breakpoint(
            address
        )

    # ========================================================
    # ENABLE BREAKPOINT
    # ========================================================

    def enable(
        self,
        address: int,
    ) -> bool:
        """
        Enable breakpoint.

        Returns:
            True if breakpoint exists.
        """

        breakpoint = (
            self.get_breakpoint(
                address
            )
        )

        if breakpoint is None:

            return False

        breakpoint.enable()

        return True

    # ========================================================
    # DISABLE BREAKPOINT
    # ========================================================

    def disable(
        self,
        address: int,
    ) -> bool:
        """
        Disable breakpoint.

        Returns:
            True if breakpoint exists.
        """

        breakpoint = (
            self.get_breakpoint(
                address
            )
        )

        if breakpoint is None:

            return False

        breakpoint.disable()

        return True

    # ========================================================
    # TOGGLE
    # ========================================================

    def toggle(
        self,
        address: int,
    ) -> bool:
        """
        Toggle breakpoint enabled state.

        Returns:
            New enabled state.
        """

        breakpoint = (
            self.get_breakpoint(
                address
            )
        )

        if breakpoint is None:

            raise KeyError(
                f"No breakpoint at "
                f"0x{address:02X}"
            )

        breakpoint.enabled = (
            not breakpoint.enabled
        )

        return breakpoint.enabled

    # ========================================================
    # RECORD HIT
    # ========================================================

    def hit(
        self,
        address: int,
    ) -> bool:
        """
        Register a breakpoint hit.

        Returns:
            True if execution should stop.
        """

        address = (
            self.validate_address(
                address
            )
        )

        breakpoint = (
            self.get_breakpoint(
                address
            )
        )

        if breakpoint is None:

            return False

        should_stop = (
            breakpoint.hit()
        )

        if not should_stop:

            return False

        self.last_hit = breakpoint

        self.total_hits += 1

        # ----------------------------------------------------
        # Temporary breakpoint
        # ----------------------------------------------------

        if breakpoint.temporary:

            self.remove_breakpoint(
                address
            )

        return True

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all breakpoints.
        """

        self._breakpoints.clear()

        self.last_hit = None

    # ========================================================
    # CLEAR ALL
    # ========================================================

    def clear_all(
        self,
    ) -> None:
        """
        Alias for clear().
        """

        self.clear()

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
        clear_breakpoints: bool = False,
    ) -> None:
        """
        Reset breakpoint statistics.

        Args:
            clear_breakpoints:
                If True, remove all breakpoints.
        """

        self.last_hit = None

        self.total_hits = 0

        for breakpoint in (
            self._breakpoints.values()
        ):

            breakpoint.reset_hits()

        if clear_breakpoints:

            self.clear()

    # ========================================================
    # LIST
    # ========================================================

    def list_breakpoints(
        self,
        enabled_only: bool = False,
    ) -> list[
        Breakpoint
    ]:
        """
        Return breakpoints sorted by address.
        """

        breakpoints = list(
            self._breakpoints.values()
        )

        if enabled_only:

            breakpoints = [
                breakpoint
                for breakpoint
                in breakpoints
                if breakpoint.enabled
            ]

        return sorted(
            breakpoints,
            key=lambda item:
                item.address,
        )

    # ========================================================
    # LIST ADDRESSES
    # ========================================================

    def addresses(
        self,
        enabled_only: bool = True,
    ) -> list[int]:
        """
        Return breakpoint addresses.
        """

        return [
            breakpoint.address
            for breakpoint
            in self.list_breakpoints(
                enabled_only=enabled_only
            )
        ]

    # ========================================================
    # COUNT
    # ========================================================

    def count(
        self,
        enabled_only: bool = False,
    ) -> int:
        """
        Return number of breakpoints.
        """

        return len(
            self.list_breakpoints(
                enabled_only=enabled_only
            )
        )

    # ========================================================
    # EMPTY
    # ========================================================

    def is_empty(
        self,
    ) -> bool:
        """
        Return True if no breakpoints exist.
        """

        return not bool(
            self._breakpoints
        )

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> list[dict]:
        """
        Return serializable breakpoint state.
        """

        return [
            breakpoint.to_dict()
            for breakpoint
            in self.list_breakpoints()
        ]

    # ========================================================
    # DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print all breakpoints.
        """

        print(
            "========== BREAKPOINTS =========="
        )

        breakpoints = (
            self.list_breakpoints()
        )

        if not breakpoints:

            print(
                "No breakpoints."
            )

        else:

            for breakpoint in (
                breakpoints
            ):

                status = (
                    "enabled"
                    if breakpoint.enabled
                    else "disabled"
                )

                kind = (
                    "temporary"
                    if breakpoint.temporary
                    else "permanent"
                )

                print(
                    f"0x"
                    f"{breakpoint.address:02X} "
                    f"| {status:<8} "
                    f"| {kind:<10} "
                    f"| hits="
                    f"{breakpoint.hits}"
                )

        print(
            "================================"
        )

    # ========================================================
    # ITERATION
    # ========================================================

    def __iter__(
        self,
    ):
        """
        Iterate over breakpoints in address order.
        """

        return iter(
            self.list_breakpoints()
        )

    # ========================================================
    # LENGTH
    # ========================================================

    def __len__(
        self,
    ) -> int:
        """
        Return number of breakpoints.
        """

        return len(
            self._breakpoints
        )

    # ========================================================
    # STRING
    # ========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"BreakpointManager("
            f"count={len(self)}, "
            f"hits={self.total_hits}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Breakpoint",
    "BreakpointManager",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Breakpoint Manager"
    )

    print()

    manager = (
        BreakpointManager()
    )

    manager.add_breakpoint(
        0x10
    )

    manager.add_breakpoint(
        0x20,
        temporary=True,
    )

    manager.add_breakpoint(
        0x30
    )

    manager.disable(
        0x30
    )

    manager.dump()

    print()

    print(
        "Breakpoint addresses:",
        [
            f"0x{address:02X}"
            for address
            in manager.addresses()
        ],
    )

    print()

    print(
        "Hit 0x10:",
        manager.hit(
            0x10
        ),
    )

    print(
        "Hit 0x20:",
        manager.hit(
            0x20
        ),
    )

    print(
        "Remaining breakpoints:",
        manager.count(),
    )
