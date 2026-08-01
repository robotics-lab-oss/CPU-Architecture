# cpu.py

from registers import Registers
from memory import Memory
from alu import ALU


class CPU:

    def __init__(self):

        self.registers = Registers()
        self.memory = Memory()
        self.alu = ALU()

        self.running = True

    def reset(self):

        self.registers.reset()
        self.memory.reset()

        self.running = True

    def load_program(self, program):

        self.memory.load_program(program)

    def fetch(self):

        pc = self.registers.PC

        instruction = self.memory.read(pc)

        self.registers.IR = instruction

        self.registers.PC += 1

    def decode_execute(self):

        instruction = self.registers.IR

        opcode = (instruction >> 4) & 0x0F
        operand = instruction & 0x0F

        if opcode == 0x0:
            pass

        elif opcode == 0x1:        # LOAD
            self.registers.ACC = operand

        elif opcode == 0x4:        # ADD

            result = self.alu.execute(
                "ADD",
                self.registers.ACC,
                operand
            )

            self.registers.ACC = result
            self.registers.FLAGS = self.alu.get_flags()

        elif opcode == 0x5:        # SUB

            result = self.alu.execute(
                "SUB",
                self.registers.ACC,
                operand
            )

            self.registers.ACC = result
            self.registers.FLAGS = self.alu.get_flags()

        elif opcode == 0xF:        # HALT

            self.running = False

        else:

            print(f"Unknown Opcode : {opcode:X}")

            self.running = False

    def step(self):

        self.fetch()
        self.decode_execute()

    def run(self):

        while self.running:
            self.step()

    def dump(self):

        self.registers.dump()
