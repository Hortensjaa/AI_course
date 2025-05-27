from copy import copy
from queue import Queue

from GameState import GameState
from typing import List


def get_rook_moves(pos: tuple[int, int]) -> set:
    x, y = pos
    v_fields = {(x, i) for i in range(8)}
    h_fields = {(i, y) for i in range(8)}

    return v_fields.union(h_fields)

def get_king_moves(pos: tuple[int, int]) -> set:
    x, y = pos
    directions = set()
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            directions.add((min(max(0, x + i), 7), (min(max(0, y + j), 7))))
    directions.remove((x, y))
    return directions

def is_checkmate(state: GameState):
    if state.turn == "white":
        return False

    w_king_pos = state.w_king
    rook_pos = state.w_rook
    b_king_pos = state.b_king

    w_king_fields = get_king_moves(w_king_pos)
    rook_fields = get_rook_moves(rook_pos)
    b_king_fields = get_king_moves(b_king_pos)

    if w_king_pos in b_king_fields and not w_king_pos in rook_fields:
        return False

    if rook_pos in b_king_fields and not rook_pos in w_king_fields:
        return False

    w_fields = w_king_fields.union(rook_fields)

    for f in b_king_fields:
        if f not in w_fields:
            return False
    return True


def find_next_moves(state: GameState) -> List[GameState]:
    w_king_fields = get_king_moves(state.w_king)
    rook_fields = get_rook_moves(state.w_rook)
    b_king_fields = get_king_moves(state.b_king)

    if state.turn == "white":
        invalid_states = {state}.union(b_king_fields)

        new_king_states = [GameState(
            "black",
            x,
            state.w_rook,
            state.b_king) for x in w_king_fields if x not in invalid_states]

        new_rook_states = [GameState(
            "black",
            state.w_king,
            x,
            state.b_king) for x in rook_fields if x not in invalid_states]

        return new_king_states + new_rook_states

    else:
        invalid_states = {state}.union(w_king_fields).union(rook_fields)
        return [GameState(
            "white",
            state.w_king,
            state.w_rook,
            x
        ) for x in b_king_fields if x not in invalid_states]


def get_move_history(l_state: GameState, checked_moves: dict):
    history = [l_state]
    while True:
        prev = checked_moves[history[-1]]
        if prev:
            history.append(prev)
        else:
            break

    return history


def find_ending(start_state: GameState, debug=False, history=True) -> int:
    checked_moves = {}
    move_history = {}

    initial_state = copy(start_state)
    queue = Queue()
    queue.put((initial_state, 0, None))
    min_moves = float('inf')
    ending_move = None

    while queue:
        el = queue.get()
        curr = el[0]
        curr_count = el[1]
        prev_state = el[2]

        if not curr in checked_moves:
            if debug:
                print(f'Checking move: {str(curr)}, moves: {curr_count}')

            # Check if checkmate
            if is_checkmate(curr):
                min_moves = curr_count
                ending_move = curr
                move_history[curr] = prev_state
                break

            # Add current state to checked moves and history
            checked_moves[curr] = curr_count
            move_history[curr] = prev_state

            # Find next moves
            next_moves = find_next_moves(curr)

            filtered_moves = [(x, curr_count + 1, curr) for x in next_moves if x not in checked_moves]

            for x in filtered_moves:
                queue.put(x)

    if not ending_move:
        return -1

    print(f"Ending move: {str(ending_move)}")

    # if history:
    #     history = get_move_history(ending_move, move_history)
    #     print('Moves history:')
    #     for move in history:
    #         print(str(move))

    return min_moves

