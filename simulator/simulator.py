# simulator.py

from cpu import CPU


def main():

    cpu = CPU()

    cpu.reset()

    # Example Program
    #
    # LOAD #5
    # ADD  #3
    # SUB  #2
    # HALT
    #
    program = [

        0x15,   # LOAD 5
        0x43,   # ADD 3
        0x52,   # SUB 2
        0xF0    # HALT

    ]

    cpu.load_program(program)

    print("===================================")
    print("      MiniCPU 8-bit Simulator")
    print("===================================")

    cycle = 0

    while cpu.running:

        print(f"\nCycle {cycle}")

        print("----------------------------")

        cpu.step()

        cpu.dump()

        cycle += 1

    print("\n===================================")
    print("Simulation Finished")
    print("===================================")


if __name__ == "__main__":
    main()
