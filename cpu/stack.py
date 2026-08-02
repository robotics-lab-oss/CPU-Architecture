"""
stack.py

MiniCPU 8-bit CPU Architecture
Stack Unit

Architecture:
    - 8-bit address space
    - 8-bit stack values
    - Stack grows downward
    - Stack Pointer (SP) starts at the top of memory

Default:
    Memory size = 256 bytes
    Initial SP  = 0xFF

Operations:
    PUSH
    POP
    PEEK
    CLEAR
    RESET
"""

from __future__ import annotations


class Stack:
    """
    MiniCPU stack implementation.

    The stack stores 8-bit values.

    Stack direction:

        Higher address
             │
             ▼

        0xFF  ← Initial SP
        0xFE
        0xFD
         ...
        0x00

    PUSH:
        Store value
        Decrease SP

    POP:
        Increase SP
        Read value

    This class can operate independently or be
    connected to CPU memory.
    """

    # ========================================================
    # CONSTANTS
    # ========================================================

    DATA_WIDTH = 8
    ADDRESS_WIDTH = 8

    MIN_VALUE = 0x00
    MAX_VALUE = 0xFF

    DEFAULT_MEMORY_SIZE = 256

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        memory_size: int = DEFAULT_MEMORY_SIZE,
    ):
        """
        Initialize stack.

        Args:
            memory_size:
                Total stack address space.

        Default:
            256 bytes
        """

        if not isinstance(
            memory_size,
            int,
        ):
            raise TypeError(
                "memory_size must be an integer."
            )

        if memory_size <= 0:
            raise ValueError(
                "memory_size must be greater than zero."
            )

        if memory_size > 256:
            raise ValueError(
                "8-bit address space supports "
                "maximum 256 bytes."
            )

        self.memory_size = memory_size

        self.stack_pointer = (
            memory_size - 1
        )

        self.base_pointer = (
            memory_size - 1
        )

        self._storage = []

    # ========================================================
    # VALUE VALIDATION
    # ========================================================

    @classmethod
    def validate_value(
        cls,
        value: int,
    ) -> int:
        """
        Validate an 8-bit stack value.
        """

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(
                "Stack value must be an integer."
            )

        if not (
            cls.MIN_VALUE
            <= value
            <= cls.MAX_VALUE
        ):
            raise ValueError(
                f"Stack value must be between "
                f"0x{cls.MIN_VALUE:02X} and "
                f"0x{cls.MAX_VALUE:02X}."
            )

        return value

    # ========================================================
    # PUSH
    # ========================================================

    def push(
        self,
        value: int,
    ) -> None:
        """
        Push an 8-bit value onto the stack.

        Example:

            stack.push(0x42)
        """

        value = self.validate_value(
            value
        )

        if self.is_full():
            raise OverflowError(
                "Stack overflow."
            )

        self._storage.append(
            value
        )

        self.stack_pointer -= 1

    # ========================================================
    # POP
    # ========================================================

    def pop(
        self,
    ) -> int:
        """
        Remove and return the top value
        from the stack.
        """

        if self.is_empty():
            raise IndexError(
                "Stack underflow."
            )

        value = self._storage.pop()

        self.stack_pointer += 1

        return value

    # ========================================================
    # PEEK
    # ========================================================

    def peek(
        self,
    ) -> int:
        """
        Return the top value without
        removing it.
        """

        if self.is_empty():
            raise IndexError(
                "Cannot peek empty stack."
            )

        return self._storage[-1]

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all values from stack.
        """

        self._storage.clear()

        self.stack_pointer = (
            self.base_pointer
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset stack to initial state.
        """

        self.clear()

    # ========================================================
    # IS EMPTY
    # ========================================================

    def is_empty(
        self,
    ) -> bool:
        """
        Return True if stack is empty.
        """

        return len(
            self._storage
        ) == 0

    # ========================================================
    # IS FULL
    # ========================================================

    def is_full(
        self,
    ) -> bool:
        """
        Return True if stack is full.
        """

        return len(
            self._storage
        ) >= self.memory_size

    # ========================================================
    # SIZE
    # ========================================================

    def size(
        self,
    ) -> int:
        """
        Return number of values currently
        stored on the stack.
        """

        return len(
            self._storage
        )

    # ========================================================
    # AVAILABLE
    # ========================================================

    def available(
        self,
    ) -> int:
        """
        Return number of free stack slots.
        """

        return (
            self.memory_size
            - self.size()
        )

    # ========================================================
    # GET STACK POINTER
    # ========================================================

    def get_stack_pointer(
        self,
    ) -> int:
        """
        Return current Stack Pointer.
        """

        return self.stack_pointer

    # ========================================================
    # SET STACK POINTER
    # ========================================================

    def set_stack_pointer(
        self,
        address: int,
    ) -> None:
        """
        Set Stack Pointer.

        This method is mainly useful for
        CPU state restoration or debugging.
        """

        if not isinstance(
            address,
            int,
        ):
            raise TypeError(
                "Stack Pointer must be an integer."
            )

        if not (
            0
            <= address
            < self.memory_size
        ):
            raise ValueError(
                "Stack Pointer is outside "
                "stack memory."
            )

        self.stack_pointer = address

    # ========================================================
    # GET BASE POINTER
    # ========================================================

    def get_base_pointer(
        self,
    ) -> int:
        """
        Return initial stack base address.
        """

        return self.base_pointer

    # ========================================================
    # ITERATE
    # ========================================================

    def values(
        self,
    ) -> tuple[int, ...]:
        """
        Return stack values from bottom
        to top.
        """

        return tuple(
            self._storage
        )

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> dict:
        """
        Return complete stack state.
        """

        return {
            "stack_pointer": (
                self.stack_pointer
            ),
            "base_pointer": (
                self.base_pointer
            ),
            "values": tuple(
                self._storage
            ),
        }

    # ========================================================
    # LOAD SNAPSHOT
    # ========================================================

    def load_snapshot(
        self,
        state: dict,
    ) -> None:
        """
        Restore stack state.
        """

        if not isinstance(
            state,
            dict,
        ):
            raise TypeError(
                "Stack state must be a dictionary."
            )

        values = state.get(
            "values",
            (),
        )

        if not isinstance(
            values,
            (list, tuple),
        ):
            raise TypeError(
                "Stack values must be "
                "a list or tuple."
            )

        if len(values) > self.memory_size:
            raise ValueError(
                "Stack state exceeds "
                "available memory."
            )

        self._storage = [
            self.validate_value(
                value
            )
            for value in values
        ]

        self.stack_pointer = (
            self.base_pointer
            - len(self._storage)
        )

    # ========================================================
    # DUPLICATE TOP
    # ========================================================

    def duplicate_top(
        self,
    ) -> None:
        """
        Duplicate the top stack value.
        """

        value = self.peek()

        self.push(
            value
        )

    # ========================================================
    # SWAP TOP TWO
    # ========================================================

    def swap_top(
        self,
    ) -> None:
        """
        Swap the top two stack values.
        """

        if self.size() < 2:
            raise IndexError(
                "At least two values are required "
                "to swap."
            )

        self._storage[-1], self._storage[-2] = (
            self._storage[-2],
            self._storage[-1],
        )

    # ========================================================
    # DEBUG DUMP
    # ========================================================

    def dump(
        self,
    ) -> None:
        """
        Print stack state.
        """

        print(
            "============= STACK ==========="
        )

        print(
            f"Stack Pointer : "
            f"0x{self.stack_pointer:02X}"
        )

        print(
            f"Base Pointer  : "
            f"0x{self.base_pointer:02X}"
        )

        print(
            f"Size          : "
            f"{self.size()}"
        )

        print(
            f"Available     : "
            f"{self.available()}"
        )

        print(
            "Values        : "
            f"{[f'0x{x:02X}' for x in self._storage]}"
        )

        print(
            "================================"
        )

    # ========================================================
    # LENGTH
    # ========================================================

    def __len__(
        self,
    ) -> int:
        """
        Return current stack size.
        """

        return self.size()

    # ========================================================
    # STRING REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return readable stack state.
        """

        return (
            f"Stack("
            f"size={self.size()}, "
            f"SP=0x{self.stack_pointer:02X}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "Stack",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    stack = Stack()

    print(
        "MiniCPU 8-bit Stack"
    )

    print()

    print(
        f"Initial SP: "
        f"0x{stack.get_stack_pointer():02X}"
    )

    stack.push(
        0x10
    )

    stack.push(
        0x20
    )

    stack.push(
        0x30
    )

    print(
        "After PUSH:"
    )

    stack.dump()

    print()

    print(
        f"PEEK: "
        f"0x{stack.peek():02X}"
    )

    value = stack.pop()

    print(
        f"POP: "
        f"0x{value:02X}"
    )

    print()

    stack.swap_top()

    print(
        "After SWAP:"
    )

    stack.dump()

    print()

    stack.duplicate_top()

    print(
        "After DUPLICATE:"
    )

    stack.dump()
