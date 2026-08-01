# registers.py

class Registers:

    def __init__(self):

        # General Purpose Registers
        self.R0 = 0
        self.R1 = 0
        self.R2 = 0
        self.R3 = 0

        # Accumulator
        self.ACC = 0

        # Program Counter
        self.PC = 0

        # Stack Pointer
        self.SP = 0x8F

        # Instruction Register
        self.IR = 0

        # Flags Register
        self.FLAGS = {
            "Z": 0,
            "C": 0,
            "N": 0,
            "O": 0
        }

    def reset(self):

        self.R0 = 0
        self.R1 = 0
        self.R2 = 0
        self.R3 = 0

        self.ACC = 0

        self.PC = 0

        self.SP = 0x8F

        self.IR = 0

        self.FLAGS = {
            "Z": 0,
            "C": 0,
            "N": 0,
            "O": 0
        }

    def dump(self):

        print("========== Registers ==========")

        print(f"ACC : {self.ACC:02X}")
        print(f"R0  : {self.R0:02X}")
        print(f"R1  : {self.R1:02X}")
        print(f"R2  : {self.R2:02X}")
        print(f"R3  : {self.R3:02X}")

        print(f"PC  : {self.PC:02X}")
        print(f"SP  : {self.SP:02X}")
        print(f"IR  : {self.IR:02X}")

        print()

        print("FLAGS")

        for flag, value in self.FLAGS.items():
            print(f"{flag} = {value}")


if __name__ == "__main__":

    cpu = Registers()

    cpu.dump()

    print()

    cpu.R0 = 10
    cpu.ACC = 25
    cpu.PC = 3

    cpu.FLAGS["Z"] = 1

    cpu.dump()
