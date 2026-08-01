# alu.py

class ALU:

    def __init__(self):

        self.Z = 0   # Zero Flag
        self.C = 0   # Carry Flag
        self.N = 0   # Negative Flag


    def update_flags(self, result, carry=0):

        result = result & 0xFF

        self.Z = 1 if result == 0 else 0

        self.C = carry

        self.N = 1 if (result & 0x80) else 0


        return result


    # Addition
    def add(self, a, b):

        result = a + b

        carry = 1 if result > 0xFF else 0

        return self.update_flags(result, carry)



    # Subtraction
    def sub(self, a, b):

        result = a - b

        carry = 1 if result < 0 else 0

        return self.update_flags(result, carry)



    # Logic AND
    def AND(self, a, b):

        result = a & b

        return self.update_flags(result)



    # Logic OR
    def OR(self, a, b):

        result = a | b

        return self.update_flags(result)



    # Logic XOR
    def XOR(self, a, b):

        result = a ^ b

        return self.update_flags(result)



    # Increment
    def INC(self, a):

        return self.add(a, 1)



    # Decrement
    def DEC(self, a):

        return self.sub(a, 1)



    # Compare
    def CMP(self, a, b):

        result = a - b

        self.update_flags(result)

        return result & 0xFF
