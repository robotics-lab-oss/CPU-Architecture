# symbol_table.py

class SymbolTable:

    def __init__(self):
        self.table = {}

    def add(self, label, address):
        if label in self.table:
            raise ValueError(f"Duplicate label: {label}")

        self.table[label] = address

    def get(self, label):
        if label not in self.table:
            raise ValueError(f"Undefined label: {label}")

        return self.table[label]

    def exists(self, label):
        return label in self.table

    def remove(self, label):
        if label in self.table:
            del self.table[label]

    def clear(self):
        self.table.clear()

    def dump(self):
        print("Symbol Table")
        print("----------------------")

        for label, address in self.table.items():
            print(f"{label:10} -> 0x{address:02X}")


if __name__ == "__main__":

    symbols = SymbolTable()

    symbols.add("START", 0x00)
    symbols.add("LOOP", 0x05)
    symbols.add("END", 0x0A)

    symbols.dump()

    print()
    print("Address of LOOP =", hex(symbols.get("LOOP")))
