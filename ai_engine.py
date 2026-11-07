"""Ba mức AI chạy nội bộ. Không dùng mạng, mô hình tải về hoặc khóa API."""

import random
from time import monotonic

from game_logic import AI, DIRECTIONS, EMPTY, HUMAN, Board, Move, check_win, in_bounds, legal_moves

DIFFICULTIES = ("Dễ", "Vừa", "Khó")
WIN_SCORE = 10_000_000
HARD_TIME_LIMIT = 0.8


def candidate_moves(board: Board, radius: int = 1) -> list[Move]:
    occupied = [(r, c) for r, row in enumerate(board) for c, cell in enumerate(row) if cell]
    if not occupied:
        return [(len(board) // 2, len(board[0]) // 2)]
    nearby = set()
    for r, c in occupied:
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                nr, nc = r + dr, c + dc
                if in_bounds(board, nr, nc) and board[nr][nc] == EMPTY:
                    nearby.add((nr, nc))
    return sorted(nearby) or legal_moves(board)


def winning_moves(board: Board, player: str, moves: list[Move]) -> list[Move]:
    wins = []
    for r, c in moves:
        board[r][c] = player
        try:
            if check_win(board, r, c):
                wins.append((r, c))
        finally:
            board[r][c] = EMPTY
    return wins


def line_score(length: int, openings: int) -> int:
    if length >= 5:
        return WIN_SCORE
    if openings == 0:
        return 0
    return (0, 2, 30, 600, 50_000)[length] * (4 if openings == 2 else 1)


def move_score(board: Board, move: Move, player: str) -> int:
    r, c = move
    total = 0
    for dr, dc in DIRECTIONS:
        length, openings = 1, 0
        for sign in (-1, 1):
            nr, nc = r + sign * dr, c + sign * dc
            while in_bounds(board, nr, nc) and board[nr][nc] == player:
                length += 1
                nr, nc = nr + sign * dr, nc + sign * dc
            if in_bounds(board, nr, nc) and board[nr][nc] == EMPTY:
                openings += 1
        total += line_score(length, openings)
    return total


def ranked_moves(board: Board, player: str, moves: list[Move]) -> list[Move]:
    opponent = HUMAN if player == AI else AI
    middle = (len(board) - 1) / 2
    return sorted(
        moves,
        key=lambda m: (
            move_score(board, m, player) + 1.15 * move_score(board, m, opponent),
            -abs(m[0] - middle) - abs(m[1] - middle),
        ),
        reverse=True,
    )


def evaluate(board: Board) -> int:
    score = 0
    for r, row in enumerate(board):
        for c, player in enumerate(row):
            if not player:
                continue
            for dr, dc in DIRECTIONS:
                pr, pc = r - dr, c - dc
                if in_bounds(board, pr, pc) and board[pr][pc] == player:
                    continue  # Chỉ đếm chuỗi từ đầu, tránh đếm một chuỗi nhiều lần.
                length, nr, nc = 0, r, c
                while in_bounds(board, nr, nc) and board[nr][nc] == player:
                    length += 1
                    nr, nc = nr + dr, nc + dc
                openings = int(in_bounds(board, pr, pc) and board[pr][pc] == EMPTY)
                openings += int(in_bounds(board, nr, nc) and board[nr][nc] == EMPTY)
                value = line_score(length, openings)
                score += value if player == AI else -value
    return score


class SearchTimeout(Exception):
    pass


def minimax(board: Board, depth: int, player: str, alpha: float, beta: float, deadline: float) -> int:
    if monotonic() >= deadline:
        raise SearchTimeout
    if depth == 0:
        return evaluate(board)
    moves = candidate_moves(board)
    if not moves:
        return 0
    wins = winning_moves(board, player, moves)
    if wins:
        return (WIN_SCORE + depth) * (1 if player == AI else -1)
    opponent = HUMAN if player == AI else AI
    blocks = winning_moves(board, opponent, moves)
    choices = ranked_moves(board, player, blocks or moves)[:8]
    best = -float("inf") if player == AI else float("inf")
    for r, c in choices:
        if monotonic() >= deadline:
            raise SearchTimeout
        board[r][c] = player
        try:
            value = minimax(board, depth - 1, opponent, alpha, beta, deadline)
        finally:
            board[r][c] = EMPTY  # Kể cả khi hết giờ, luôn trả lại bàn cờ ban đầu.
        if player == AI:
            best, alpha = max(best, value), max(alpha, value)
        else:
            best, beta = min(best, value), min(beta, value)
        if beta <= alpha:
            break
    return int(best)


def choose_move(board: Board, difficulty: str = "Vừa", *, time_limit: float = HARD_TIME_LIMIT) -> Move | None:
    if difficulty not in DIFFICULTIES:
        raise ValueError("Độ khó phải là Dễ, Vừa hoặc Khó.")
    # Tìm kiếm trên bản sao để tuyệt đối không thay đổi bàn cờ đang chơi.
    board = [row[:] for row in board]
    deadline = monotonic() + max(0, time_limit)
    moves = candidate_moves(board)
    if not moves:
        return None
    if difficulty == "Dễ":
        return random.choice(moves)
    wins = winning_moves(board, AI, moves)
    if wins:
        return wins[0]
    blocks = winning_moves(board, HUMAN, moves)
    ranked = ranked_moves(board, AI, blocks or moves)
    best_move = ranked[0]
    if difficulty == "Vừa" or blocks:
        return best_move
    # Đào sâu dần: chỉ nhận kết quả của một vòng tìm kiếm đã hoàn tất.
    choices = ranked[:10]
    for depth in (2, 3):
        round_best, round_score = best_move, -float("inf")
        alpha = -float("inf")
        try:
            for r, c in choices:
                if monotonic() >= deadline:
                    raise SearchTimeout
                board[r][c] = AI
                try:
                    value = minimax(board, depth - 1, HUMAN, alpha, float("inf"), deadline)
                finally:
                    board[r][c] = EMPTY
                if value > round_score:
                    round_best, round_score = (r, c), value
                alpha = max(alpha, round_score)
        except SearchTimeout:
            break
        best_move = round_best
    return best_move
