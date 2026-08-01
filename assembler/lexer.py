# lexer.py

class Lexer:

    def __init__(self):
        self.tokens = []


    def reset(self):
        self.tokens = []


    def remove_comment(self, line):

        if ";" in line:
            line = line.split(";", 1)[0]

        return line.strip()


    def tokenize_line(self, line):

        # Comma को space में बदलो
        line = line.replace(",", " ")

        # Tabs हटाओ
        line = line.replace("\t", " ")

        # Extra spaces हटाओ
        parts = line.split()

        return parts


    def tokenize(self, source):

        self.reset()

        lines = source.splitlines()

        for line_number, line in enumerate(lines, start=1):

            line = self.remove_comment(line)

            # Empty line
            if line == "":
                continue

            parts = self.tokenize_line(line)

            if len(parts) == 0:
                continue

            entry = {
                "line": line_number,
                "raw": line,
                "label": None,
                "instruction": None,
                "operand": None
            }

            # ---------------------
            # Label
            # Example:
            # LOOP:
            # ---------------------

            if parts[0].endswith(":"):

                entry["label"] = parts[0][:-1].upper()

                parts = parts[1:]

                if len(parts) == 0:
                    self.tokens.append(entry)
                    continue

            # ---------------------
            # Instruction
            # ---------------------

            entry["instruction"] = parts[0].upper()

            # ---------------------
            # Operand
            # ---------------------

            if len(parts) > 1:

                entry["operand"] = " ".join(parts[1:])

            self.tokens.append(entry)

        return self.tokens


if __name__ == "__main__":

    source = """

; Example Program

START:

LOAD 5

ADD 3

SUB 2

OUT

HALT

"""

    lexer = Lexer()

    tokens = lexer.tokenize(source)

    for token in tokens:

        print(token)
