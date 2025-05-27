from itertools import combinations
from random import choice


# {0: pusta, 1: pełna, 2: gwarantowana}

# # https://towardsdatascience.com/solving-nonograms-with-120-lines-of-code-a7c6e0f627e4/
def calculate_guaranteed_cells(blocks: [int], n: int) -> [int]:
    guaranteed = [2 for _ in range(n)]  # na początku ustawiam wszystkie pola jako pewne
    # na koniec każdego bloku dodaję dodatkowe, zajęte pole (bo ono musi być puste)
    fixed_blocks = [blocks[i] + 1 for i in range(len(blocks) - 1)] + [blocks[-1]]
    free_places = n - sum(fixed_blocks)
    # możliwe pozycje startowe wg algorytmu z linku - na każdej z nich możemy ustawic początek bloku lub zostawić pustą
    positions = range(len(fixed_blocks) + free_places)
    combs = combinations(positions, len(fixed_blocks))
    # teraz w pętli rzutuję wszystkie kombinacje na listę gwarantowanych; przekręcam wolne pola na 0
    all_combs = []
    for c in combs:
        line = [0 for _ in range(n)]
        pointer = 0
        block_num = 0
        # odzyskiwanie linii z opisu kombinacji
        for i in range(len(fixed_blocks) + free_places):
            if i in c:
                for j in range(pointer, pointer + blocks[block_num]):
                    line[j] = 1
                pointer += blocks[block_num] + 1
                block_num += 1
            else:
                pointer += 1
        all_combs.append(line)
        for k in range(n):
            if line[k] == 0:
                guaranteed[k] = 0
    return guaranteed, all_combs

def calculate_line_score(line: [int], blocks: [int], combs: [[int]]) -> int:
    n = len(line)
    # teraz w pętli rzutuję wszystkie kombinacje na aktualną linię
    best_match = float("-inf")
    for c in combs:
        # porównanie linii do aktualnej
        score = 0
        for k in range(n):
            if (line[k] >= 1) == (c[k] >= 1):
                score += 1
        best_match = max(best_match, score)
    return best_match

def str_cell(cell: int):
    if cell > 0:
        return "#"
    return "."


