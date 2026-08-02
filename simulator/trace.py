"""
trace.py

MiniCPU 8-bit CPU Architecture
Execution Trace System

Responsibilities:
    - Record CPU execution history
    - Store program counter
    - Store executed instruction
    - Store opcode
    - Store operands
    - Store register state
    - Store flags
    - Store execution result
    - Store memory changes
    - Limit trace history
    - Export trace data
    - Clear trace history

The Trace system is designed to work with:

    Simulator
    Runner
    Debugger

Example:

    trace = Trace()

    trace.record(
        pc=0x00,
        instruction="LOAD",
        opcode=0x10,
        operands=[0x20],
    )

    trace.dump()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================
# TRACE ENTRY
# ============================================================

@dataclass
class TraceEntry:
    """
    Represents one CPU execution event.

    Attributes:
        step:
            Global trace step number.

        pc:
            Program Counter before instruction execution.

        instruction:
            Instruction name.

        opcode:
            Numeric opcode.

        operands:
            Instruction operand bytes.

        registers:
            Register snapshot.

        flags:
            CPU flag snapshot.

        result:
            Instruction execution result.

        memory_changes:
            Memory modifications caused by instruction.

        pc_after:
            Program Counter after instruction execution.

        halted:
            Whether CPU became halted.

        metadata:
            Additional implementation-specific data.
    """

    step: int

    pc: Optional[int] = None

    instruction: Optional[str] = None

    opcode: Optional[int] = None

    operands: list[int] = field(
        default_factory=list
    )

    registers: Any = None

    flags: Any = None

    result: Any = None

    memory_changes: Any = None

    pc_after: Optional[int] = None

    halted: bool = False

    metadata: dict = field(
        default_factory=dict
    )

    # ========================================================
    # DICTIONARY
    # ========================================================

    def to_dict(
        self,
    ) -> dict:
        """
        Convert trace entry into a serializable dictionary.
        """

        return {
            "step": self.step,

            "pc": self.pc,

            "pc_hex": (
                f"0x{self.pc:02X}"
                if self.pc is not None
                else None
            ),

            "instruction": (
                self.instruction
            ),

            "opcode": self.opcode,

            "opcode_hex": (
                f"0x{self.opcode:02X}"
                if self.opcode is not None
                else None
            ),

            "operands": list(
                self.operands
            ),

            "registers": (
                self.registers
            ),

            "flags": (
                self.flags
            ),

            "result": (
                self.result
            ),

            "memory_changes": (
                self.memory_changes
            ),

            "pc_after": (
                self.pc_after
            ),

            "pc_after_hex": (
                f"0x{self.pc_after:02X}"
                if self.pc_after is not None
                else None
            ),

            "halted": (
                self.halted
            ),

            "metadata": dict(
                self.metadata
            ),
        }

    # ========================================================
    # STRING
    # ========================================================

    def format(
        self,
    ) -> str:
        """
        Return human-readable trace line.
        """

        pc_text = (
            f"0x{self.pc:02X}"
            if self.pc is not None
            else "----"
        )

        opcode_text = (
            f"0x{self.opcode:02X}"
            if self.opcode is not None
            else "--"
        )

        instruction_text = (
            self.instruction
            if self.instruction
            else "UNKNOWN"
        )

        operand_text = " ".join(
            f"{value:02X}"
            for value in self.operands
        )

        if not operand_text:

            operand_text = "--"

        return (
            f"[{self.step:06d}] "
            f"PC={pc_text} "
            f"OP={opcode_text} "
            f"{instruction_text:<6} "
            f"OPERAND={operand_text}"
        )

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"TraceEntry("
            f"step={self.step}, "
            f"pc={self.pc}, "
            f"instruction="
            f"{self.instruction!r}, "
            f"opcode={self.opcode}"
            f")"
        )


# ============================================================
# TRACE
# ============================================================

class Trace:
    """
    CPU execution trace manager.

    The Trace class stores a chronological list
    of TraceEntry objects.

    Example:

        trace = Trace()

        trace.record(
            pc=0x00,
            instruction="LOAD",
            opcode=0x10,
            operands=[0x20],
        )

        print(
            trace.latest()
        )
    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(
        self,
        enabled: bool = True,
        max_entries: Optional[int] = None,
    ):
        """
        Initialize Trace.

        Args:
            enabled:
                Enable or disable recording.

            max_entries:
                Maximum number of entries.

                None means unlimited.
        """

        self.enabled = enabled

        self.max_entries = (
            max_entries
        )

        if (
            max_entries is not None
            and (
                not isinstance(
                    max_entries,
                    int,
                )
                or max_entries <= 0
            )
        ):

            raise ValueError(
                "max_entries must be "
                "a positive integer "
                "or None."
            )

        self.entries: list[
            TraceEntry
        ] = []

        self.total_recorded = 0

        self.next_step = 0

    # ========================================================
    # ENABLE
    # ========================================================

    def enable(
        self,
    ) -> None:
        """
        Enable trace recording.
        """

        self.enabled = True

    # ========================================================
    # DISABLE
    # ========================================================

    def disable(
        self,
    ) -> None:
        """
        Disable trace recording.
        """

        self.enabled = False

    # ========================================================
    # IS ENABLED
    # ========================================================

    def is_enabled(
        self,
    ) -> bool:
        """
        Return True if tracing is enabled.
        """

        return self.enabled

    # ========================================================
    # RECORD
    # ========================================================

    def record(
        self,
        entry: Optional[
            TraceEntry
        ] = None,
        *,
        pc: Optional[int] = None,
        instruction: Optional[
            str
        ] = None,
        opcode: Optional[int] = None,
        operands=None,
        registers=None,
        flags=None,
        result=None,
        memory_changes=None,
        pc_after: Optional[int] = None,
        halted: bool = False,
        metadata=None,
        state=None,
    ) -> Optional[
        TraceEntry
    ]:
        """
        Record one execution event.

        Supports both:

            trace.record(
                TraceEntry(...)
            )

        and:

            trace.record(
                pc=0x00,
                instruction="LOAD",
                opcode=0x10,
            )

        The optional 'state' argument allows the
        debugger to pass a complete state dictionary.
        """

        if not self.enabled:

            return None

        # ----------------------------------------------------
        # Existing TraceEntry
        # ----------------------------------------------------

        if isinstance(
            entry,
            TraceEntry,
        ):

            trace_entry = entry

            if (
                trace_entry.step
                < 0
            ):

                trace_entry.step = (
                    self.next_step
                )

        else:

            # ------------------------------------------------
            # Normalize operands
            # ------------------------------------------------

            if operands is None:

                operands = []

            else:

                operands = list(
                    operands
                )

            # ------------------------------------------------
            # Normalize metadata
            # ------------------------------------------------

            if metadata is None:

                metadata = {}

            else:

                metadata = dict(
                    metadata
                )

            # ------------------------------------------------
            # Merge state information
            # ------------------------------------------------

            if state is not None:

                if not isinstance(
                    state,
                    dict,
                ):

                    raise TypeError(
                        "state must be a dictionary."
                    )

                if pc is None:

                    pc = state.get(
                        "program_counter"
                    )

                if registers is None:

                    registers = state.get(
                        "registers"
                    )

                if flags is None:

                    flags = state.get(
                        "flags"
                    )

                if result is None:

                    result = state.get(
                        "last_result"
                    )

                metadata[
                    "state"
                ] = state

            # ------------------------------------------------
            # Create entry
            # ------------------------------------------------

            trace_entry = TraceEntry(

                step=self.next_step,

                pc=pc,

                instruction=(
                    instruction
                ),

                opcode=opcode,

                operands=operands,

                registers=registers,

                flags=flags,

                result=result,

                memory_changes=(
                    memory_changes
                ),

                pc_after=pc_after,

                halted=halted,

                metadata=metadata,
            )

        # ----------------------------------------------------
        # Append
        # ----------------------------------------------------

        self.entries.append(
            trace_entry
        )

        self.total_recorded += 1

        self.next_step = (
            trace_entry.step + 1
        )

        # ----------------------------------------------------
        # Enforce maximum history
        # ----------------------------------------------------

        self._trim()

        return trace_entry

    # ========================================================
    # ADD ALIAS
    # ========================================================

    def add(
        self,
        entry=None,
        **kwargs,
    ):
        """
        Alias for record().
        """

        return self.record(
            entry,
            **kwargs,
        )

    # ========================================================
    # TRIM
    # ========================================================

    def _trim(
        self,
    ) -> None:
        """
        Keep trace within max_entries.
        """

        if self.max_entries is None:

            return

        excess = (
            len(self.entries)
            - self.max_entries
        )

        if excess > 0:

            del self.entries[
                :excess
            ]

    # ========================================================
    # LATEST
    # ========================================================

    def latest(
        self,
    ) -> Optional[
        TraceEntry
    ]:
        """
        Return latest trace entry.
        """

        if not self.entries:

            return None

        return self.entries[-1]

    # ========================================================
    # FIRST
    # ========================================================

    def first(
        self,
    ) -> Optional[
        TraceEntry
    ]:
        """
        Return first available trace entry.
        """

        if not self.entries:

            return None

        return self.entries[0]

    # ========================================================
    # GET
    # ========================================================

    def get(
        self,
        index: int,
    ) -> TraceEntry:
        """
        Return trace entry by list index.
        """

        if not isinstance(
            index,
            int,
        ):

            raise TypeError(
                "Trace index must be integer."
            )

        return self.entries[
            index
        ]

    # ========================================================
    # FIND BY PC
    # ========================================================

    def find_by_pc(
        self,
        pc: int,
    ) -> list[
        TraceEntry
    ]:
        """
        Return all trace entries for a PC.
        """

        return [
            entry
            for entry
            in self.entries
            if entry.pc == pc
        ]

    # ========================================================
    # FIND BY INSTRUCTION
    # ========================================================

    def find_by_instruction(
        self,
        instruction: str,
    ) -> list[
        TraceEntry
    ]:
        """
        Return all trace entries for
        a specific instruction.
        """

        if not isinstance(
            instruction,
            str,
        ):

            raise TypeError(
                "Instruction must be string."
            )

        instruction = (
            instruction
            .strip()
            .upper()
        )

        return [
            entry
            for entry
            in self.entries
            if (
                entry.instruction
                and
                entry.instruction.upper()
                == instruction
            )
        ]

    # ========================================================
    # FIND BY OPCODE
    # ========================================================

    def find_by_opcode(
        self,
        opcode: int,
    ) -> list[
        TraceEntry
    ]:
        """
        Return all trace entries for opcode.
        """

        if not isinstance(
            opcode,
            int,
        ):

            raise TypeError(
                "Opcode must be integer."
            )

        return [
            entry
            for entry
            in self.entries
            if entry.opcode == opcode
        ]

    # ========================================================
    # LAST N
    # ========================================================

    def last(
        self,
        count: int = 10,
    ) -> list[
        TraceEntry
    ]:
        """
        Return last N trace entries.
        """

        if not isinstance(
            count,
            int,
        ):

            raise TypeError(
                "count must be integer."
            )

        if count < 0:

            raise ValueError(
                "count cannot be negative."
            )

        if count == 0:

            return []

        return self.entries[
            -count:
        ]

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(
        self,
    ) -> None:
        """
        Clear all trace entries.
        """

        self.entries.clear()

        self.next_step = 0

    # ========================================================
    # RESET
    # ========================================================

    def reset(
        self,
    ) -> None:
        """
        Reset trace history and counters.
        """

        self.entries.clear()

        self.total_recorded = 0

        self.next_step = 0

    # ========================================================
    # SET MAX ENTRIES
    # ========================================================

    def set_max_entries(
        self,
        max_entries: Optional[int],
    ) -> None:
        """
        Change trace history size limit.
        """

        if (
            max_entries is not None
            and (
                not isinstance(
                    max_entries,
                    int,
                )
                or max_entries <= 0
            )
        ):

            raise ValueError(
                "max_entries must be "
                "a positive integer "
                "or None."
            )

        self.max_entries = (
            max_entries
        )

        self._trim()

    # ========================================================
    # EXPORT DICTIONARIES
    # ========================================================

    def to_list(
        self,
    ) -> list[dict]:
        """
        Export all trace entries as dictionaries.
        """

        return [
            entry.to_dict()
            for entry
            in self.entries
        ]

    # ========================================================
    # SNAPSHOT
    # ========================================================

    def snapshot(
        self,
    ) -> list[dict]:
        """
        Alias for to_list().
        """

        return self.to_list()

    # ========================================================
    # FORMAT
    # ========================================================

    def format(
        self,
        limit: Optional[int] = None,
    ) -> str:
        """
        Return human-readable trace output.

        Args:
            limit:
                Optional number of latest entries.
        """

        entries = self.entries

        if limit is not None:

            entries = self.last(
                limit
            )

        if not entries:

            return (
                "Trace is empty."
            )

        return "\n".join(
            entry.format()
            for entry
            in entries
        )

    # ========================================================
    # DUMP
    # ========================================================

    def dump(
        self,
        limit: Optional[int] = None,
    ) -> None:
        """
        Print trace output.
        """

        print(
            "================ CPU TRACE ================"
        )

        print(
            self.format(
                limit=limit
            )
        )

        print(
            "============================================"
        )

    # ========================================================
    # LENGTH
    # ========================================================

    def __len__(
        self,
    ) -> int:

        return len(
            self.entries
        )

    # ========================================================
    # ITERATION
    # ========================================================

    def __iter__(
        self,
    ):

        return iter(
            self.entries
        )

    # ========================================================
    # INDEXING
    # ========================================================

    def __getitem__(
        self,
        index,
    ):

        return self.entries[
            index
        ]

    # ========================================================
    # REPRESENTATION
    # ========================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"Trace("
            f"entries={len(self)}, "
            f"enabled={self.enabled}, "
            f"max_entries="
            f"{self.max_entries}"
            f")"
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "TraceEntry",
    "Trace",
]


# ============================================================
# BASIC TEST
# ============================================================

if __name__ == "__main__":

    print(
        "MiniCPU 8-bit Execution Trace"
    )

    print()

    trace = Trace(
        enabled=True,
        max_entries=10,
    )

    trace.record(
        pc=0x00,
        instruction="LOAD",
        opcode=0x10,
        operands=[0x20],
        registers={
            "A": 0x00,
        },
    )

    trace.record(
        pc=0x02,
        instruction="ADD",
        opcode=0x30,
        operands=[0x21],
        registers={
            "A": 0x10,
        },
    )

    trace.record(
        pc=0x04,
        instruction="HALT",
        opcode=0xF0,
        halted=True,
    )

    trace.dump()

    print()

    print(
        "Total entries:",
        len(trace),
    )

    print()

    print(
        "Latest entry:",
        trace.latest(),
    )

    print()

    print(
        "LOAD instructions:",
        trace.find_by_instruction(
            "LOAD"
        ),
    )
