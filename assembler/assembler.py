from opcode import OPCODES

def assemble(line):
    parts = line.strip().split()

    if len(parts) == 0:
        return None

    instruction = parts[0].upper()

    opcode = OPCODES[instruction]

    operand = 0

    if len(parts) > 1:
        operand = int(parts[1].replace("#", ""))

    machine = (opcode << 4) | operand

    return machine

program = [
    "LOAD #5",
    "ADD #3",
    "HALT"
]

for line in program:
    code = assemble(line)

    if code is not None:
        print(f"{line:10} -> {code:08b}")
