from solver import CommandoSolver


# Read input
def read_and_parse(file: str):
    with open("zad_input.txt", 'r') as file:
        file = file.readlines()

    data = [x.strip() for x in file]

    return data

board = read_and_parse("zad_input1.txt")

solver = CommandoSolver(board)

with open("zad_output.txt", 'w') as file:
    file.write(solver.solve())

