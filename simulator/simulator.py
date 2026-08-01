# simulator.py

from cpu import CPU


def main():

    cpu = CPU()

    cpu.reset()

    # ==========================
    # Example Program
    #
    # LOAD #5
    # ADD  #3
    # SUB  #2
    # OUT
    # HALT
    # ==========================

    program = [

        0x10, 0x05,     # LOAD #5
        0x30, 0x03,     # ADD  #3
        0x40, 0x02,     # SUB  #2
        0xA0,           # OUT
        0xF0            # HALT

    ]

    cpu.load_program(program)

    print("=" * 40)
    print("      MiniCPU 8-bit Simulator")
    print("=" * 40)

    cycle = 0

    while cpu.running:

        print(f"\nCycle {cycle}")
        print("-" * 40)

        cpu.step()

        cpu.dump()

        cycle += 1

    print("\n" + "=" * 40)
    print("Simulation Finished")
    print("=" * 40)


if __name__ == "__main__":
    main()
