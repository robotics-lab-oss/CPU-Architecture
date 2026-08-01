# registers.py

class Registers:

    def __init__(self):

        self.reset()


    def reset(self):

        # General Registers
        self.A = 0        # Accumulator
        self.B = 0        # General Purpose


        # CPU Control Registers
        self.PC = 0       # Program Counter
        self.IR = 0       # Instruction Register


        # Flags
        self.Z = 0        # Zero Flag
        self.C = 0        # Carry Flag
        self.N = 0        # Negative Flag



    def dump(self):

        print("--------------------")

        print(f"A   : {self.A:02X}")
        print(f"B   : {self.B:02X}")

        print(f"PC  : {self.PC:02X}")
        print(f"IR  : {self.IR:02X}")

        print(
            f"FLAGS Z:{self.Z} C:{self.C} N:{self.N}"
        )

        print("--------------------")
