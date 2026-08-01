# memory.py

class Memory:

    def __init__(self, size=256):

        self.size = size

        # 256 bytes memory
        self.data = [0] * self.size


    def reset(self):

        self.data = [0] * self.size


    # Memory Read
    def read(self, address):

        if 0 <= address < self.size:
            return self.data[address]

        raise Exception("Memory address out of range")


    # Memory Write
    def write(self, address, value):

        if 0 <= address < self.size:

            self.data[address] = value & 0xFF

        else:
            raise Exception("Memory address out of range")


    # Program load
    def load(self, program, start=0):

        for i, byte in enumerate(program):

            self.write(start + i, byte)


    # Memory dump
    def dump(self, start=0, end=32):

        print("---- MEMORY ----")

        for addr in range(start, end):

            print(
                f"{addr:02X}: {self.data[addr]:02X}"
            )

        print("----------------")
