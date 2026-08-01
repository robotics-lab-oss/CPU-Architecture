# symbol_table.py

from opcode import OPERAND_INSTRUCTIONS


class SymbolTable:

    def __init__(self):
        self.reset()


    def reset(self):
        self.symbols = {}


    # -------------------------
    # First Pass
    # -------------------------

    def build(self, tokens):

        self.reset()

        address = 0

        for token in tokens:

            label = token["label"]
            instruction = token["instruction"]

            # Label
            if label is not None:

                if label in self.symbols:

                    raise Exception(
                        f"Duplicate label: {label}"
                    )

                self.symbols[label] = address

            # Label only line
            if instruction is None:
                continue

            # Instruction Size

            if instruction in OPERAND_INSTRUCTIONS:

                address += 2

            else:

                address += 1

        return self.symbols


    # -------------------------
    # Get Label Address
    # -------------------------

    def get(self, label):

        label = label.upper()

        if label not in self.symbols:

            raise Exception(
                f"Undefined label: {label}"
            )

        return self.symbols[label]


    # -------------------------
    # Exists
    # -------------------------

    def exists(self, label):

        return label.upper() in self.symbols


    # -------------------------
    # Dump
    # -------------------------

    def dump(self):

        print("------ SYMBOL TABLE ------")

        for name in sorted(self.symbols):

            print(
                f"{name:<15} "
                f"{self.symbols[name]:02X}"
            )

        print("--------------------------")


if __name__ == "__main__":

    tokens = [

        {
            "line": 1,
            "label": "START",
            "instruction": "LOAD",
            "operand": "5"
        },

        {
            "line": 2,
            "label": "LOOP",
            "instruction": "ADD",
            "operand": "1"
        },

        {
            "line": 3,
            "label": None,
            "instruction": "JMP",
            "operand": "LOOP"
        },

        {
            "line": 4,
            "label": None,
            "instruction": "HALT",
            "operand": None
        }

    ]

    table = SymbolTable()

    table.build(tokens)

    table.dump()
