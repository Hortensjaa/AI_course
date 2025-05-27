def coords_to_text(cords: tuple[int, int]):
    x, y = cords
    return chr(y + ord("a")) + str(x + 1)

class GameState:
    turn: str
    w_king: tuple[int, int]
    w_rook: tuple[int, int]
    b_king: tuple[int, int]

    def __init__(self, turn: str, w_king, w_rook, b_king):
        self.turn = turn
        self.w_king = w_king
        self.w_rook = w_rook
        self.b_king = b_king

    def __str__(self):
        return (f'{self.turn} '
                f'{coords_to_text(self.w_king)} '
                f'{coords_to_text(self.w_rook)} '
                f'{coords_to_text(self.b_king)}')

    def __eq__(self, other):
        if not isinstance(other, GameState):
            return False
        return (self.turn == other.turn and
                self.w_king == other.w_king and
                self.w_rook == other.w_rook and
                self.b_king == other.b_king)

    def __hash__(self):
        return hash((self.turn, tuple(self.w_king), tuple(self.w_rook), tuple(self.b_king)))
