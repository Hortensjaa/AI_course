"""
Sztuczna Inteligencja lista 1, Julia Kulczycka
Implementuję zasady porównywania układów (pełne nie są może potrzebne, bo gracze losują z różnych talii i figurarz
może wylosować tylko niektóre układy). Następnie eksperymentalnie testuję prawdopodobieństwo wybranej blotkarza.
Przeprowadzam eksperymenty dla różnych wariantów jego talii (maksymalizującej szansę na wysokie układy)
"""


from collections import namedtuple, Counter
from random import sample

Card = namedtuple("card", ["rank", "suit"])

figures = [11, 12, 13, 14]  # J, Q, K, A
blots = [2, 3, 4, 5, 6, 7, 8, 9, 10]
suits = [-1, -2, -3, -4]

fig_deck = [Card(r, s) for r in figures for s in suits]
blot_deck = [Card(r, s) for r in blots for s in suits]


def eval_hand(hand):
    colors = set([c.suit for c in hand])
    values = Counter(c.rank for c in hand)
    hand.sort()
    if hand[0].rank + 4 == hand[1].rank + 3 == hand[2].rank + 2 == hand[3].rank + 1 == hand[4].rank:
        if len(colors) == 1:
            return 1  # poker
        else:
            return 5  # strit
    if len(colors) == 1:
        return 4  # kolor
    if 4 in values.values():
        return 2  # kareta
    if 3 in values.values():
        if 2 in values.values():
            return 3  # full
        else:
            return 6  # trójka
    if list(values.values()).count(2) == 2:
        return 7  # dwie pary
    if 2 in values.values():
        return 8  # para
    return 9


def experiment(b_deck=blot_deck):
    f = sample(fig_deck, k=5)
    b = sample(b_deck, k=5)
    if eval_hand(b) < eval_hand(f):
        return 1  # wygrana blotkarza
    return 0


def case(b_deck=blot_deck, n=100000):
    s = 0
    for _ in range(n):
        s += experiment(b_deck)
    return s / n


def always_win():
    poker_only = [Card(2, -1), Card(3, -1), Card(4, -1), Card(5, -1), Card(6, -1)]
    return case(poker_only)


def one_color():
    color = [Card(r, -1) for r in blots]
    return case(color)


def two_quads():
    quads = [Card(r, s) for r in [9, 10] for s in suits]
    return case(quads)


def three_quads():
    quads = [Card(r, s) for r in [8, 9, 10] for s in suits]
    return case(quads)


print(f"All cards: {case()}")
# print(f"5 cards: {always_win()}")
# print(f"9 cards: {one_color()}")
# print(f"8 cards: {two_quads()}")
# print(f"12 cards: {three_quads()}")
