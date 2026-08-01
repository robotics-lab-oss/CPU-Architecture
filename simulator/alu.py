# alu.py

class ALU:

    def __init__(self):
        self.reset()


    def reset(self):

        # Flags
        self.Z = 0      # Zero
        self.C = 0      # Carry
        self.N = 0      # Negative


    # -------------------------
    # Flag Update
    # -------------------------

    def update_flags(self, result, carry=0):

        result &= 0xFF

        self.Z = 1 if result == 0 else 0

        self.C = carry

        self.N = 1 if (result & 0x80) else 0

        return result


    # -------------------------
    # ADD
    # -------------------------

    def add(self, a, b):

        result = a + b

        carry = 1 if result > 0xFF else 0

        return self.update_flags(result, carry)


    # -------------------------
    # SUB
    # -------------------------

    def sub(self, a, b):

        result = a - b

        borrow = 1 if result < 0 else 0

        return self.update_flags(result, borrow)


    # -------------------------
    # AND
    # -------------------------

    def AND(self, a, b):

        result = a & b

        return self.update_flags(result)


    # -------------------------
    # OR
    # -------------------------

    def OR(self, a, b):

        result = a | b

        return self.update_flags(result)


    # -------------------------
    # XOR
    # -------------------------

    def XOR(self, a, b):

        result = a ^ b

        return self.update_flags(result)


    # -------------------------
    # INC
    # -------------------------

    def INC(self, value):

        return self.add(value, 1)


    # -------------------------
    # DEC
    # -------------------------

    def DEC(self, value):

        return self.sub(value, 1)


    # -------------------------
    # CMP
    # -------------------------

    def CMP(self, a, b):

        result = a - b

        borrow = 1 if result < 0 else 0

        self.update_flags(result, borrow)

        return result & 0xFF


    # -------------------------
    # NOT
    # (Future Use)
    # -------------------------

    def NOT(self, value):

        result = (~value) & 0xFF

        return self.update_flags(result)
