# assembler.py

from opcode import OPCODES
from lexer import tokenize
from parser import parse
from symbol_table import SymbolTable


class Assembler:

    def __init__(self):
        self.symbols = SymbolTable()
        self.machine_code = []

    def first_pass(self, source):

        address = 0

        for line in source:

            line = line.strip()

            if not line:
                continue

            tokens = tokenize(line)

            if not tokens:
                continue

            if tokens[0][0] == "LABEL":
                self.symbols.add(tokens[0][1], address)
                continue

            address += 1

    def second_pass(self, source):

        for line in source:

            line = line.strip()

            if not line:
                continue

            tokens = tokenize(line)

            if not tokens:
                continue

            if tokens[0][0] == "LABEL":
                continue

            inst = parse(line)

            opcode = OPCODES[inst["opcode"]]

            operand = 0

            if inst["operand"] is not None:

                if inst["operand_type"] == "IMMEDIATE":
                    operand = int(inst["operand"])

                elif inst["operand_type"] == "ADDRESS":
                    operand = int(inst["operand"],16)

                elif inst["operand_type"] == "REGISTER":
                    operand = int(inst["operand"][1])

            machine = (opcode << 4) | operand

            self.machine_code.append(machine)

    def dump(self):

        print("Machine Code")

        print("----------------")

        for code in self.machine_code:
            print(f"{code:08b}")


if __name__ == "__main__":

    source = [

        "START:",
        "LOAD #5",
        "ADD #3",
        "STORE 0x20",
        "HALT"

    ]

    asm = Assembler()

    asm.first_pass(source)

    asm.second_pass(source)

    asm.symbols.dump()

    print()

    asm.dump()
