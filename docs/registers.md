# CPU Registers

## Version

v0.1

## Register Layout

| Register | Size | Description |
|----------|------|-------------|
| A | 8-bit | Accumulator |
| B | 8-bit | General Purpose Register |
| PC | 8-bit | Program Counter |
| IR | 8-bit | Instruction Register |
| SP | 8-bit | Stack Pointer |
| FLAGS | 8-bit | Status Flags |

---

## FLAGS Register

| Bit | Name | Description |
|-----|------|-------------|
| 0 | Z | Zero Flag |
| 1 | C | Carry Flag |
| 2 | N | Negative Flag |
| 3 | V | Overflow Flag |
| 4-7 | Reserved | Reserved for future use |

---

## Register Summary

- Total Registers: 6
- Register Size: 8-bit
- Address Width: 8-bit
