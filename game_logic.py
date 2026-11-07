"""Luật Caro độc lập với giao diện, có thể kiểm thử bằng Python."""

from dataclasses import dataclass, field

SIZE = 10
MIN_SIZE = 5
MAX_SIZE = 20
WIN_LENGTH = 5
EMPTY = ""
HUMAN = "X"
AI = "O"
MODE_AI = "Đấu AI"
MODE_PVP = "Hai người (1 vs 1)"
GAME_MODES = (MODE_AI, MODE_PVP)
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))
Board = list[list[str]]
Move = tuple[int, int]


def create_board(size: int = SIZE) -> Board:
    if type(size) is not int or not MIN_SIZE <= size <= MAX_SIZE:
        raise ValueError(f"Kích thước bàn cờ phải là số nguyên từ {MIN_SIZE} đến {MAX_SIZE}.")
    return [[EMPTY for _ in range(size)] for _ in range(size)]


def in_bounds(board: Board, row: int, col: int) -> bool:
    return 0 <= row < len(board) and 0 <= col < len(board[row])


def is_valid_move(board: Board, row: int, col: int) -> bool:
    return in_bounds(board, row, col) and board[row][col] == EMPTY


def legal_moves(board: Board) -> list[Move]:
    return [(r, c) for r, row in enumerate(board) for c, cell in enumerate(row) if cell == EMPTY]


def check_win(board: Board, row: int, col: int) -> list[Move]:
    """Đếm cả hai phía từ quân vừa đặt; trả về cả chuỗi khi dài hơn 5."""
    if not in_bounds(board, row, col) or board[row][col] == EMPTY:
        return []
    player = board[row][col]
    for dr, dc in DIRECTIONS:
        line = [(row, col)]
        for sign in (-1, 1):
            r, c = row + sign * dr, col + sign * dc
            while in_bounds(board, r, c) and board[r][c] == player:
                line.append((r, c))
                r, c = r + sign * dr, c + sign * dc
        if len(line) >= WIN_LENGTH:
            return sorted(line)
    return []


def is_draw(board: Board) -> bool:
    """Bàn đầy và không có bên nào thắng (kể cả dữ liệu bàn cờ nhập sẵn)."""
    return not legal_moves(board) and not any(
        check_win(board, r, c) for r, row in enumerate(board) for c in range(len(row))
    )


@dataclass
class Game:
    board: Board = field(default_factory=create_board)
    turn: str = HUMAN
    finished: bool = False
    winner: str | None = None
    winning_cells: list[Move] = field(default_factory=list)
    history: list[tuple[int, int, str]] = field(default_factory=list)
    difficulty: str = "Vừa"
    game_id: int = 0
    mode: str = MODE_AI

    def play(self, row: int, col: int, player: str) -> bool:
        # Kiểm tra lại trong logic, không chỉ dựa vào nút bị khóa trên giao diện.
        if self.finished or player != self.turn or player not in (HUMAN, AI):
            return False
        if not is_valid_move(self.board, row, col):
            return False
        self.board[row][col] = player
        self.history.append((row, col, player))
        self.winning_cells = check_win(self.board, row, col)
        if self.winning_cells:
            self.finished, self.winner = True, player
        elif not legal_moves(self.board):
            self.finished = True
        else:
            self.turn = AI if player == HUMAN else HUMAN
        return True
