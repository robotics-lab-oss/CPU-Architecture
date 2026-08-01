# parser.py

from opcode import OPCODES, OPERAND_INSTRUCTIONS


class Parser:

    def __init__(self):

        self.machine_code = []


    def reset(self):

        self.machine_code = []


    # --------------------------
    # Number Parser
    # --------------------------

    def parse_number(self, value):

        value = value.strip()

        # Hex
        if value.startswith(("0x", "0X")):
            return int(value, 16)

        # Binary
        if value.startswith(("0b", "0B")):
            return int(value, 2)

        # Decimal
        return int(value)


    # --------------------------
    # Parse
    # --------------------------

    def parse(self, tokens, symbol_table=None):

        self.reset()

        if symbol_table is None:
            symbol_table = {}

        for token in tokens:

            line = token["line"]

            instruction = token["instruction"]

            operand = token["operand"]


            # Label only
            if instruction is None:
                continue


            # Unknown instruction
            if instruction not in OPCODES:

                raise Exception(
                    f"Line {line}: Unknown instruction '{instruction}'"
                )


            # Opcode
            opcode = OPCODES[instruction]

            self.machine_code.append(opcode)


            # Operand Instructions
            if instruction in OPERAND_INSTRUCTIONS:

                if operand is None:

                    raise Exception(
                        f"Line {line}: Missing operand"
                    )


                # Label Operand
                if operand.upper() in symbol_table:

                    value = symbol_table[
                        operand.upper()
                    ]

                else:

                    value = self.parse_number(
                        operand
                    )


                if not (0 <= value <= 255):

                    raise Exception(
                        f"Line {line}: Operand out of range (0-255)"
                    )


                self.machine_code.append(value)


            # Unexpected Operand
            else:

                if operand is not None:

                    raise Exception(
                        f"Line {line}: '{instruction}' takes no operand"
                    )


        return self.machine_code


    # --------------------------
    # Hex Dump
    # --------------------------

    def hex_dump(self):

        return " ".join(
            f"{byte:02X}"
            for byte in self.machine_code
        )


    # --------------------------
    # Binary Dump
    # --------------------------

    def binary_dump(self):

        return " ".join(
            f"{byte:08b}"
            for byte in self.machine_code
        )


if __name__ == "__main__":

    sample_tokens = [

        {
            "line": 1,
            "instruction": "LOAD",
            "operand": "5"
        },

        {
            "line": 2,
            "instruction": "ADD",
            "operand": "3"
        },

        {
            "line": 3,
            "instruction": "OUT",
            "operand": None
        },

        {
            "line": 4,
            "instruction": "HALT",
            "operand": None
        }

    ]

    parser = Parser()

    code = parser.parse(sample_tokens)

    print("Machine Code :")
    print(code)

    print()

    print("Hex :")
    print(parser.hex_dump())

    print()

    print("Binary :")
    print(parser.binary_dump())
