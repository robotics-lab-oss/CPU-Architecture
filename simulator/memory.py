# memory.py

class Memory:

    MEMORY_SIZE = 256

    def __init__(self):
        self.memory = [0] * self.MEMORY_SIZE

    def reset(self):
        self.memory = [0] * self.MEMORY_SIZE

    def read(self, address):

        self._check_address(address)

        return self.memory[address]

    def write(self, address, value):

        self._check_address(address)

        self.memory[address] = value & 0xFF

    def load_program(self, program, start_address=0):

        for i, byte in enumerate(program):
            self.write(start_address + i, byte)

    def dump(self, start=0, end=32):

        print("======= Memory Dump =======")

        for addr in range(start, min(end, self.MEMORY_SIZE)):
            print(f"{addr:02X}: {self.memory[addr]:02X}")

    def _check_address(self, address):

        if not (0 <= address < self.MEMORY_SIZE):
            raise ValueError(
                f"Memory address out of range: 0x{address:02X}"
            )


if __name__ == "__main__":

    mem = Memory()

    mem.write(0x00, 0x15)
    mem.write(0x01, 0x43)
    mem.write(0x02, 0xF0)

    print("Read Address 0x00 =", hex(mem.read(0x00)))

    print()

    mem.dump(0, 8)
