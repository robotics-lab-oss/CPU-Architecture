# cpu.py

from registers import Registers
from memory import Memory
from alu import ALU


class CPU:

    def __init__(self):

        self.reg = Registers()
        self.memory = Memory()
        self.alu = ALU()

        self.running = False


    def reset(self):

        self.reg.reset()
        self.memory.reset()

        self.running = True



    def load_program(self, program):

        self.memory.load(program)



    # Fetch
    def fetch(self):

        opcode = self.memory.read(
            self.reg.PC
        )

        self.reg.IR = opcode

        self.reg.PC += 1

        return opcode



    # Read next byte
    def fetch_operand(self):

        value = self.memory.read(
            self.reg.PC
        )

        self.reg.PC += 1

        return value



    # Execute

    def execute(self, opcode):


        # 00 NOP
        if opcode == 0x00:

            pass



        # 10 LOAD immediate
        elif opcode == 0x10:

            value = self.fetch_operand()

            self.reg.A = value

            self.update_flags()



        # 20 STORE memory
        elif opcode == 0x20:

            address = self.fetch_operand()

            self.memory.write(
                address,
                self.reg.A
            )



        # 30 ADD
        elif opcode == 0x30:

            value = self.fetch_operand()

            self.reg.A = self.alu.add(
                self.reg.A,
                value
            )

            self.copy_flags()



        # 40 SUB
        elif opcode == 0x40:

            value = self.fetch_operand()

            self.reg.A = self.alu.sub(
                self.reg.A,
                value
            )

            self.copy_flags()



        # 50 AND
        elif opcode == 0x50:

            value = self.fetch_operand()

            self.reg.A = self.alu.AND(
                self.reg.A,
                value
            )

            self.copy_flags()



        # 60 OR
        elif opcode == 0x60:

            value = self.fetch_operand()

            self.reg.A = self.alu.OR(
                self.reg.A,
                value
            )

            self.copy_flags()



        # 70 XOR
        elif opcode == 0x70:

            value = self.fetch_operand()

            self.reg.A = self.alu.XOR(
                self.reg.A,
                value
            )

            self.copy_flags()



        # 80 JMP
        elif opcode == 0x80:

            address = self.fetch_operand()

            self.reg.PC = address



        # 90 JZ
        elif opcode == 0x90:

            address = self.fetch_operand()

            if self.reg.Z == 1:

                self.reg.PC = address



        # A0 OUT
        elif opcode == 0xA0:

            print(
                "OUTPUT:",
                self.reg.A
            )



        # B0 IN
        elif opcode == 0xB0:

            value = int(
                input("INPUT: ")
            )

            self.reg.A = value & 0xFF

            self.update_flags()



        # C0 INC
        elif opcode == 0xC0:

            self.reg.A = self.alu.INC(
                self.reg.A
            )

            self.copy_flags()



        # D0 DEC
        elif opcode == 0xD0:

            self.reg.A = self.alu.DEC(
                self.reg.A
            )

            self.copy_flags()



        # E0 CMP
        elif opcode == 0xE0:

            value = self.fetch_operand()

            self.alu.CMP(
                self.reg.A,
                value
            )

            self.copy_flags()



        # F0 HALT
        elif opcode == 0xF0:

            print("HALT")

            self.running = False



        else:

            raise Exception(
                f"Invalid Opcode {opcode:02X}"
            )



    # Update flags
    def copy_flags(self):

        self.reg.Z = self.alu.Z
        self.reg.C = self.alu.C
        self.reg.N = self.alu.N



    def update_flags(self):

        self.reg.Z = 1 if self.reg.A == 0 else 0

        self.reg.N = 1 if (
            self.reg.A & 0x80
        ) else 0



    # One CPU cycle

    def step(self):

        opcode = self.fetch()

        self.execute(opcode)



    def dump(self):

        self.reg.dump()
