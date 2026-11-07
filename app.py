"""Giao diện tiếng Việt. Chạy: streamlit run app.py."""

import streamlit as st

from ai_engine import DIFFICULTIES, choose_move
from game_logic import AI, GAME_MODES, HUMAN, MAX_SIZE, MIN_SIZE, MODE_AI, MODE_PVP, Game, create_board, is_valid_move, legal_moves

st.set_page_config(page_title="Cờ Caro · AI & 1 vs 1", page_icon="❎", layout="wide")

CSS = """
<style>
.block-container {max-width:none; padding:2.2rem clamp(1rem,3vw,4rem) 2rem;}
.hero {background:#142c43; color:#fff; border-radius:22px; padding:30px 34px; margin-bottom:24px;}
.eyebrow {font-size:12px; letter-spacing:2px; color:#74d9c4; font-weight:700; margin-bottom:10px;}
.hero h1 {color:#fff; font-size:clamp(25px,4vw,38px); padding:0; letter-spacing:-1px;}
.hero p {color:#c1d0df; margin:12px 0 0; font-size:15px;}
.legend {display:flex; flex-wrap:wrap; gap:8px 20px; font-size:14px; margin:4px 0 16px; color:#53657a;}
.legend b {font-size:19px;} .human {color:#087f75;} .robot {color:#d06132;}
.st-key-board_scroll {overflow-x:auto; padding-bottom:4px;}
.st-key-board {min-width:420px; gap:4px !important;}
.st-key-board [data-testid="stHorizontalBlock"] {gap:4px !important; flex-wrap:nowrap !important;}
.st-key-board [data-testid="stColumn"] {min-width:0 !important; flex:1 1 0 !important; width:0 !important;}
.st-key-board .stButton button {aspect-ratio:1; width:100%; height:auto; min-height:0;
  padding:0; border:1px solid #dbe3ec; border-radius:7px; background:#fff;}
.st-key-board .stButton button p {font-size:clamp(19px,2.6vw,40px); font-weight:700; line-height:1;}
.st-key-board .stButton button:disabled {opacity:1; color:#718198;}
.st-key-board div[class*="_X"] button:disabled {color:#087f75; background:#e8f6f1;}
.st-key-board div[class*="_O"] button:disabled {color:#c75529; background:#fff0e7;}
.st-key-board div[class*="_win"] button:disabled {background:#d8f4ad; border:2px solid #619a26; color:#315c0c;}
.st-key-board div[class*="_last"] button:disabled {box-shadow:inset 0 0 0 2px #d8996b;}
.st-key-board .stButton button:hover:enabled {border-color:#087f75; background:#e8f6f1;}
.st-key-board .stButton button:focus-visible {outline:3px solid #087f75; outline-offset:1px;}
[data-testid="stMetric"] {background:#fff; border:1px solid #e3e9ef; border-radius:14px; padding:12px 16px;}
[data-testid="stMetricValue"] {font-size:27px;}
.footer-note {text-align:center; color:#7a8897; font-size:12px; margin-top:24px;}
/* Chỉ chia cột cho bố cục chính; các cột ô cờ vẫn giữ nguyên. */
@media(min-width:1001px) {
 .st-key-game_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {flex-wrap:nowrap;}
 .st-key-game_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child {
   flex:1 1 0; width:0; min-width:0;
 }
 .st-key-game_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
   flex:0 0 320px; width:320px; min-width:320px;
 }
}
@media(max-width:1000px) {
 .st-key-game_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {flex-wrap:wrap;}
 .st-key-game_layout > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
   flex:1 1 100%; width:100%; min-width:0;
 }
}
@media(max-width:640px) {
 .block-container {padding:4rem 0.8rem 2rem;} .hero {padding:23px 20px; border-radius:16px;}
 [data-testid="stMetric"] {padding:10px;} .st-key-score [data-testid="stHorizontalBlock"] {flex-wrap:nowrap;}
 .st-key-score [data-testid="stColumn"] {min-width:0 !important;}
}
</style>
"""


def initialize() -> None:
    if "game" not in st.session_state:
        st.session_state.game = Game()
        st.session_state.stats = {"wins": 0, "losses": 0, "draws": 0}
        st.session_state.counted_game = None
        st.session_state.next_difficulty = "Vừa"
    if "next_board_size" not in st.session_state:
        st.session_state.next_board_size = len(st.session_state.game.board)
    if "next_mode" not in st.session_state:
        st.session_state.next_mode = st.session_state.game.mode
    if "pvp_stats" not in st.session_state:
        st.session_state.pvp_stats = {HUMAN: 0, AI: 0, "draws": 0}


def start_game(use_selection: bool = True) -> None:
    old = st.session_state.game
    difficulty = st.session_state.next_difficulty if use_selection else old.difficulty
    size = st.session_state.next_board_size if use_selection else len(old.board)
    mode = st.session_state.next_mode if use_selection else old.mode
    st.session_state.game = Game(board=create_board(size), difficulty=difficulty, game_id=old.game_id + 1, mode=mode)


def human_move(row: int, col: int, game_id: int, revision: int) -> None:
    game = st.session_state.game
    # Nút chứa số ván và số nước: sự kiện bấm nhanh từ giao diện cũ sẽ bị bỏ qua.
    if game.game_id == game_id and len(game.history) == revision:
        player = game.turn if game.mode == MODE_PVP else HUMAN
        game.play(row, col, player)


def player_name(game: Game, player: str) -> str:
    if game.mode == MODE_PVP:
        return "Người chơi 1" if player == HUMAN else "Người chơi 2"
    return "Bạn" if player == HUMAN else "Máy"


def record_result() -> None:
    game = st.session_state.game
    if game.finished and st.session_state.counted_game != game.game_id:
        if game.mode == MODE_PVP:
            st.session_state.pvp_stats[game.winner or "draws"] += 1
        else:
            key = "wins" if game.winner == HUMAN else "losses" if game.winner == AI else "draws"
            st.session_state.stats[key] += 1
        st.session_state.counted_game = game.game_id


def render() -> None:
    initialize()
    record_result()
    game = st.session_state.game
    size = len(game.board)
    pvp = game.mode == MODE_PVP
    title = "CỜ CARO · 1 VS 1" if pvp else "CỜ CARO ĐẤU AI"
    description = "Hai người cùng chơi trên một thiết bị. X đi trước, O tiếp lời!" if pvp else "Một nước đi, một thử thách. Bạn có thể nối đủ 5 quân trước máy?"
    st.markdown(CSS, unsafe_allow_html=True)
    # Bàn lớn cuộn ngang, giữ các ô đủ rộng để bấm trên điện thoại.
    st.markdown(f"<style>.st-key-board {{min-width:{size * 42}px;}}</style>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="hero"><div class="eyebrow">GÓC TRÍ TUỆ · {size} × {size}</div>'
        f'<h1>{title}</h1><p>{description}</p></div>',
        unsafe_allow_html=True,
    )
    with st.container(key="score"):
        wins, losses, draws, moves = st.columns(4)
        wins.metric("X thắng" if pvp else "Thắng", st.session_state.pvp_stats[HUMAN] if pvp else st.session_state.stats["wins"])
        losses.metric("O thắng" if pvp else "Thua", st.session_state.pvp_stats[AI] if pvp else st.session_state.stats["losses"])
        draws.metric("Hòa", (st.session_state.pvp_stats if pvp else st.session_state.stats)["draws"])
        moves.metric("Số nước", len(game.history))
    st.write("")
    with st.container(key="game_layout"):
        board_column, panel = st.columns([4, 1], gap="large")
    with board_column, st.container(border=True):
        st.subheader(f"Bàn cờ {size} × {size} · Ván {game.game_id + 1}")
        opponent = player_name(game, AI) if pvp else f"Máy · {game.difficulty}"
        st.markdown(f'<div class="legend"><span><b class="human">X</b> {player_name(game, HUMAN)} · đi trước</span>'
                    f'<span><b class="robot">O</b> {opponent}</span></div>', unsafe_allow_html=True)
        if game.finished:
            if pvp and game.winner:
                st.success(f"{player_name(game, game.winner)} ({game.winner}) thắng! Đã nối ít nhất 5 quân.")
            elif game.winner == HUMAN:
                st.success("Bạn thắng! Năm quân đã nối thành hàng.")
            elif game.winner == AI:
                st.error("Máy thắng ván này. Thử lại một ván nhé!")
            else:
                st.info("Hòa! Bàn cờ đã kín.")
        elif pvp:
            st.info(f"Lượt {game.turn} · {player_name(game, game.turn)}, hãy chọn một ô trống.")
        elif game.turn == AI:
            st.info("Lượt O · Máy đang suy nghĩ…")
        else:
            st.info("Lượt X · Đến lượt bạn, hãy chọn một ô trống.")
        with st.container(key="board_scroll"), st.container(key="board"):
            for r in range(size):
                columns = st.columns(size, gap="small")
                for c, column in enumerate(columns):
                    value = game.board[r][c]
                    suffix = "_win" if (r, c) in game.winning_cells else ""
                    if game.history and (r, c) == game.history[-1][:2]:
                        suffix += "_last"
                    key = f"cell_{game.game_id}_{len(game.history)}_{r}_{c}_{value or 'empty'}{suffix}"
                    column.button(
                        value or "·", key=key, width="stretch",
                        help=f"Hàng {r + 1}, cột {c + 1}: {value or 'ô trống'}",
                        disabled=game.finished or (game.mode == MODE_AI and game.turn != HUMAN) or bool(value),
                        on_click=human_move, args=(r, c, game.game_id, len(game.history)),
                    )
        st.caption("Ô có viền cam là nước vừa đánh. Trên điện thoại, vuốt ngang bàn cờ nếu cần.")
    with panel:
        with st.container(border=True):
            st.subheader("Sẵn sàng thử sức?")
            st.selectbox("Chế độ cho trận mới", GAME_MODES, key="next_mode")
            st.selectbox(
                "Kích thước bàn cờ cho trận mới", range(MIN_SIZE, MAX_SIZE + 1),
                format_func=lambda n: f"{n} × {n}", key="next_board_size",
            )
            next_pvp = st.session_state.next_mode == MODE_PVP
            st.selectbox("Độ khó cho trận mới", DIFFICULTIES, key="next_difficulty", disabled=next_pvp)
            descriptions = {
                "Dễ": "Khởi động nhẹ nhàng: máy chọn ngẫu nhiên gần các quân đã đánh.",
                "Vừa": "Tập quan sát: máy tìm nước thắng, chặn bạn và tính điểm thế cờ.",
                "Khó": "Thử thách chiến thuật: máy tính trước 2–3 nước bằng minimax.",
            }
            st.caption("Hai bạn thay phiên bấm ô trên cùng thiết bị: người chơi 1 đánh X, người chơi 2 đánh O."
                       if next_pvp else descriptions[st.session_state.next_difficulty])
            st.button("Trận mới", type="primary", width="stretch", on_click=start_game, key="new_game")
            st.button("Chơi lại", width="stretch", on_click=start_game, args=(False,), key="replay")
            st.caption("Trận mới áp dụng chế độ, kích thước và độ khó đã chọn. Chơi lại giữ cài đặt của ván hiện tại. Bảng điểm được lưu riêng theo chế độ trong phiên.")
        with st.container(border=True):
            st.subheader("Cách chơi")
            instructions = ("1. Người chơi 1 cầm **X**, đi trước.\n2. Hai người luân phiên bấm ô trống: **X → O → X**.\n"
                            if pvp else "1. Bạn cầm **X** và luôn đi trước.\n2. Bấm ô trống; máy tự đáp **O**.\n")
            st.markdown(instructions +
                        "3. Nối **ít nhất 5 quân** ngang, dọc hoặc chéo để thắng.")
            st.caption("Bị chặn hai đầu vẫn thắng. Không có luật cấm. Hết ô mà chưa có ai thắng thì hòa.")
        if game.history:
            with st.expander("Xem các nước đã đi"):
                st.text("\n".join(f"{i}. {player_name(game, p)} ({p}) · hàng {r+1}, cột {c+1}"
                                  for i, (r, c, p) in enumerate(game.history, 1)))
    footer_mode = "Hai người cùng một thiết bị" if pvp else "AI chạy nội bộ"
    st.markdown(f'<div class="footer-note">Học chiến thuật qua từng ván · {footer_mode} · Không cần tài khoản</div>', unsafe_allow_html=True)
    # X đã được đặt bằng callback; AI chỉ chạy đúng khi đến lượt O ở lần rerun này.
    if game.mode == MODE_AI and not game.finished and game.turn == AI:
        with st.spinner("Máy đang chọn nước đi…"):
            move = choose_move(game.board, game.difficulty)
            if move is None or not is_valid_move(game.board, *move):
                available = legal_moves(game.board)
                move = available[0] if available else None
            if move is None:
                game.finished = True
            else:
                game.play(*move, AI)
        st.rerun()


if __name__ == "__main__":
    render()
