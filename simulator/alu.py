# alu.py

class ALU:

    def __init__(self):

        self.flags = {
            "Z": 0,
            "C": 0,
            "N": 0,
            "O": 0
        }

    def execute(self, opcode, a, b=0):

        self.flags = {
            "Z": 0,
            "C": 0,
            "N": 0,
            "O": 0
        }

        result = 0

        if opcode == "ADD":

            total = a + b
            result = total & 0xFF

            if total > 0xFF:
                self.flags["C"] = 1

        elif opcode == "SUB":

            result = (a - b) & 0xFF

            if a < b:
                self.flags["C"] = 1

        elif opcode == "AND":

            result = a & b

        elif opcode == "OR":

            result = a | b

        elif opcode == "XOR":

            result = a ^ b

        elif opcode == "NOT":

            result = (~a) & 0xFF

        elif opcode == "CMP":

            result = (a - b) & 0xFF

            if a < b:
                self.flags["C"] = 1

        else:
            raise ValueError(f"Unknown opcode: {opcode}")

        if result == 0:
            self.flags["Z"] = 1

        if result & 0x80:
            self.flags["N"] = 1

        return result

    def get_flags(self):
        return self.flags


if __name__ == "__main__":

    alu = ALU()

    result = alu.execute("ADD", 5, 3)

    print("Result =", result)

    print("Flags =", alu.get_flags())

    print()

    result = alu.execute("SUB", 3, 5)

    print("Result =", result)

    print("Flags =", alu.get_flags())
