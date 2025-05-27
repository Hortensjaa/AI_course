def opt_dist(bits, D):
    n = len(bits)
    if D == 0:
        return sum(bits)

    min_changes = float('inf')

    for i in range(n - D + 1):
        window = bits[i:i + D]
        changes = D - sum(window) + sum(bits[:i]) + sum(bits[i+D:])
        min_changes = min(min_changes, changes)

    return min_changes


assert opt_dist([0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 5) == 3
assert opt_dist([0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 4) == 4
assert opt_dist([0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 3) == 3
assert opt_dist([0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 2) == 2
assert opt_dist([0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 1) == 1
assert opt_dist([0, 0, 1, 0, 0, 0, 1, 0, 0, 0], 0) == 2
