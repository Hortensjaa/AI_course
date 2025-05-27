def get_blocks(line):
    blocks = []
    current_length = 0
    for i in line:
        if i == 1:
            current_length += 1
        else:
            if current_length > 0:
                blocks.append(current_length)
                current_length = 0

    if current_length > 0:
        blocks.append(current_length)

    return blocks

def check_line_quality(line, spec):
    line_blocks = get_blocks(line)

    # idealnie zgodna ze specyfikacją
    if line_blocks == [spec]:
        return 100

    # kara za brakujący blok zalezna od liczby oczekiwanych komorek
    if not line_blocks:
        return -10 * spec

    expected_size = spec if spec else 0

    # większa kara za za dużo bloków, żeby wymusić łączenie
    if len(line_blocks) > 1:
        return -10 * len(line_blocks)

    # mamy 1 blok, ale dajemy karę za złą długość
    actual_size = line_blocks[0]
    size_diff = abs(actual_size - expected_size)
    return 50 - (size_diff * 10)

def is_line_valid(line, spec):
    return get_blocks(line) == ([spec] if spec else [])

def parse_file(input_file):
    with open(input_file, 'r') as f:
        parts = f.readline().split()
        x_size, y_size = int(parts[0]), int(parts[1])

        rows = []
        for _ in range(x_size):
            rows.append(int(f.readline().strip()))

        cols = []
        for _ in range(y_size):
            cols.append(int(f.readline().strip()))
    return x_size, y_size, rows, cols


def save_solution(image, output_file):
    with open(output_file, 'w') as f:
        for row in image.grid:
            f.write(''.join('#' if cell else '.' for cell in row) + '\n')

