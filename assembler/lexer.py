# lexer.py

class Lexer:

    def __init__(self):
        self.tokens = []


    def tokenize(self, source):

        self.tokens = []

        lines = source.splitlines()

        for line_number, line in enumerate(lines, start=1):

            # Remove comments
            if ";" in line:
                line = line.split(";")[0]

            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Replace comma with space
            line = line.replace(",", " ")

            # Split into tokens
            parts = line.split()

            self.tokens.append({
                "line": line_number,
                "tokens": parts
            })

        return self.tokens
