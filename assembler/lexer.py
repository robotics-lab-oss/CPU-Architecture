# lexer.py

KEYWORDS = {
    "NOP",
    "LOAD",
    "STORE",
    "MOV",
    "ADD",
    "SUB",
    "AND",
    "OR",
    "XOR",
    "NOT",
    "CMP",
    "JMP",
    "JZ",
    "JNZ",
    "IN",
    "HALT"
}


def tokenize(line):
    # Remove comments
    line = line.split(";")[0].strip()

    if not line:
        return []

    tokens = []

    parts = line.replace(",", " ").split()

    for part in parts:

        upper = part.upper()

        if upper in KEYWORDS:
            tokens.append(("INSTRUCTION", upper))

        elif part.startswith("#"):
            tokens.append(("IMMEDIATE", part[1:]))

        elif part.startswith("R"):
            tokens.append(("REGISTER", part))

        elif part.startswith("0X"):
            tokens.append(("ADDRESS", part))

        elif part.endswith(":"):
            tokens.append(("LABEL", part[:-1]))

        else:
            tokens.append(("IDENTIFIER", part))

    return tokens


if __name__ == "__main__":

    program = [
        "START:",
        "LOAD #5",
        "ADD #3",
        "MOV R1",
        "STORE 0x20",
        "HALT"
    ]

    for line in program:
        print(line)
        print(tokenize(line))
        print()
