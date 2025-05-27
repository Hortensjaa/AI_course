from z3 import eval_hand, Card

assert eval_hand([
    Card(10, -1), Card(9, -1), Card(8, -1), Card(7, -1), Card(6, -1)
]) == 1

assert eval_hand([
    Card(10, -1), Card(10, -2), Card(10, -3), Card(10, -4), Card(6, -1)
]) == 2

assert eval_hand([
    Card(10, -1), Card(10, -2), Card(10, -3), Card(6, -4), Card(6, -1)
]) == 3

assert eval_hand([
    Card(3, -1), Card(5, -1), Card(7, -1), Card(9, -1), Card(11, -1)
]) == 4

assert eval_hand([
    Card(5, -1), Card(6, -2), Card(7, -3), Card(8, -4), Card(9, -1)
]) == 5

assert eval_hand([
    Card(10, -1), Card(10, -2), Card(10, -3), Card(6, -4), Card(8, -1)
]) == 6

assert eval_hand([
    Card(10, -1), Card(10, -2), Card(6, -3), Card(6, -4), Card(8, -1)
]) == 7

assert eval_hand([
    Card(10, -1), Card(10, -2), Card(3, -3), Card(6, -4), Card(8, -1)
]) == 8

assert eval_hand([
    Card(2, -1), Card(5, -2), Card(7, -3), Card(9, -4), Card(12, -1)
]) == 9