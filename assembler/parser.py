# parser.py

from lexer import tokenize

def parse(line):
    tokens = tokenize(line)

    if not tokens:
        return None

    instruction = {
        "opcode": None,
        "operand": None,
        "operand_type": None
    }

    # First token must be an instruction
    if tokens[0][0] != "INSTRUCTION":
        raise SyntaxError(f"Expected instruction: {line}")

    instruction["opcode"] = tokens[0][1]

    if len(tokens) > 1:

        token_type = tokens[1][0]
        token_value = tokens[1][1]

        instruction["operand_type"] = token_type
        instruction["operand"] = token_value

    return instruction


if __name__ == "__main__":

    program = [
        "LOAD #5",
        "ADD #3",
        "MOV R1",
        "STORE 0x20",
        "HALT"
    ]

    for line in program:
        print(parse(line))
