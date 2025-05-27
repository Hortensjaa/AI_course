from random import random

fd = open("zad2_words.txt")
ft = open("pantadeusz.txt")

dictionary = set([x.strip() for x in fd.readlines()])


def is_word(t):
    return t in dictionary


def text_reconstruction(text):
    dp = [0] * (len(text) + 1)
    dp[0] = 0
    prev = [0] * (len(text) + 1)

    # wyliczanie maksymalnych wartości prefiksów (dp[]) razem z zapisywaniem tablicy do rekonstrukcji
    for i in range(1, len(text) + 1):
        for j in range(i):
            if is_word(text[j:i]):
                if dp[i] < dp[j] + len(text[j:i]) ** 2:
                    dp[i] = dp[j] + len(text[j:i]) ** 2
                    prev[i] = j

    # rekonstrukcja tekstu
    i = len(prev) - 1
    reconstruction = []
    while i > 0:
        j = prev[i]
        reconstruction.append(text[j:i])
        i = j

    return " ".join(reconstruction[::-1])

def random_text_reconstruction(text, max_attempts=1000):
    for _ in range(max_attempts):
        prev = [-1] * (len(text) + 1)
        prev[0] = 0

        for i in range(1, len(text) + 1):
            j = 0
            while j < i:
                if j-i > 25:
                    j = 0
                elif is_word(text[j:i]) and (j == 0 or prev[j] != -1):
                    if random() > 0.6:
                        prev[i] = j
                j += 1

        if prev[len(text)] != -1:
            i = len(text)
            reconstruction = []
            while i > 0:
                j = prev[i]
                reconstruction.append(text[j:i])
                i = j

            return " ".join(reconstruction[::-1])

    return None