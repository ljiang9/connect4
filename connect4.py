"""Connect Four vs AI - 四子棋人机对战."""
from __future__ import annotations

import random

ROWS, COLS = 6, 7
EMPTY, HUMAN, AI = 0, 1, 2
PIECE = {EMPTY: "·", HUMAN: "●", AI: "○"}

# 列首选顺序：中间优先（配合 minimax tie-breaking）
PREFERRED = [3, 2, 4, 1, 5, 0, 6]


class Connect4:
    """6x7 四子棋棋盘逻辑."""

    def __init__(self) -> None:
        self.board = [[EMPTY] * COLS for _ in range(ROWS)]

    def copy(self) -> "Connect4":
        g = Connect4()
        g.board = [row[:] for row in self.board]
        return g

    def valid_columns(self) -> list[int]:
        return [c for c in range(COLS) if self.board[0][c] == EMPTY]

    def drop(self, col: int, player: int) -> bool:
        """在 col 列落子，满列返回 False."""
        for r in range(ROWS - 1, -1, -1):
            if self.board[r][col] == EMPTY:
                self.board[r][col] = player
                return True
        return False

    def full(self) -> bool:
        return all(self.board[0][c] != EMPTY for c in range(COLS))

    def winner(self) -> int | None:
        """返回获胜方（HUMAN/AI），无胜负返回 None."""
        b = self.board
        # 横向
        for r in range(ROWS):
            for c in range(COLS - 3):
                w = [b[r][c + i] for i in range(4)]
                if w[0] != EMPTY and w[0] == w[1] == w[2] == w[3]:
                    return w[0]
        # 纵向
        for c in range(COLS):
            for r in range(ROWS - 3):
                w = [b[r + i][c] for i in range(4)]
                if w[0] != EMPTY and w[0] == w[1] == w[2] == w[3]:
                    return w[0]
        # 对角线 \ (左上到右下)
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                w = [b[r + i][c + i] for i in range(4)]
                if w[0] != EMPTY and w[0] == w[1] == w[2] == w[3]:
                    return w[0]
        # 对角线 / (右上到左下)
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                w = [b[r - i][c + i] for i in range(4)]
                if w[0] != EMPTY and w[0] == w[1] == w[2] == w[3]:
                    return w[0]
        return None

    def is_terminal(self) -> bool:
        return self.winner() is not None or self.full()

    def render(self) -> str:
        lines = ["  " + " ".join(str(c + 1) for c in range(COLS))]
        for r in range(ROWS):
            lines.append("  " + " ".join(PIECE[self.board[r][c]] for c in range(COLS)))
        return "\n".join(lines)


def _score_window(window: list[int], piece: int) -> int:
    opp = HUMAN if piece == AI else AI
    n_piece = window.count(piece)
    n_opp = window.count(opp)
    n_empty = window.count(EMPTY)
    if n_piece == 4:
        return 100
    if n_piece == 3 and n_empty == 1:
        return 5
    if n_piece == 2 and n_empty == 2:
        return 2
    if n_opp == 3 and n_empty == 1:
        return -4
    return 0


def evaluate(game: Connect4) -> int:
    """静态评估：AI 视角的分数."""
    w = game.winner()
    if w == AI:
        return 1_000_000
    if w == HUMAN:
        return -1_000_000
    b = game.board
    score = 0
    # 中心列偏好：控制中心通常更强
    center_count = sum(1 for r in range(ROWS) if b[r][3] == AI)
    score += center_count * 3
    # 水平
    for r in range(ROWS):
        for c in range(COLS - 3):
            score += _score_window([b[r][c + i] for i in range(4)], AI)
    # 垂直
    for c in range(COLS):
        for r in range(ROWS - 3):
            score += _score_window([b[r + i][c] for i in range(4)], AI)
    # 对角线 \
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            score += _score_window([b[r + i][c + i] for i in range(4)], AI)
    # 对角线 /
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            score += _score_window([b[r - i][c + i] for i in range(4)], AI)
    return score


def minimax(game: Connect4, depth: int, alpha: float, beta: float,
            maximizing: bool) -> tuple[float, int | None]:
    """带 alpha-beta 剪枝的 minimax。返回 (score, best_col)."""
    if depth == 0 or game.is_terminal():
        return evaluate(game), None
    best_col = None
    if maximizing:
        best = float("-inf")
        for col in PREFERRED:
            if game.board[0][col] != EMPTY:
                continue
            child = game.copy()
            child.drop(col, AI)
            val, _ = minimax(child, depth - 1, alpha, beta, False)
            if val > best:
                best, best_col = val, col
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best, best_col
    else:
        best = float("inf")
        for col in PREFERRED:
            if game.board[0][col] != EMPTY:
                continue
            child = game.copy()
            child.drop(col, HUMAN)
            val, _ = minimax(child, depth - 1, alpha, beta, True)
            if val < best:
                best, best_col = val, col
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best, best_col


def ai_move(game: Connect4, depth: int = 4) -> int:
    """AI 选择一列：深度受限 minimax（带 alpha-beta）。"""
    _, col = minimax(game, depth, float("-inf"), float("inf"), True)
    if col is None:  # 棋盘已满或异常，回退到任意合法列
        cols = game.valid_columns()
        return random.choice(cols) if cols else 0
    return col


def easy_move(game: Connect4) -> int:
    """简单 AI：随机走."""
    return random.choice(game.valid_columns())


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="四子棋人机对战（vs AI）")
    parser.add_argument("--easy", action="store_true", help="简单 AI（随机走棋）")
    parser.add_argument("--demo", action="store_true", help="演示模式：AI 自走一局")
    parser.add_argument("--selfplay", action="store_true",
                        help="自我对战：强 AI（先手）对随机 AI，统计胜率")
    parser.add_argument("--depth", type=int, default=4,
                        help="AI 搜索深度（默认 4）")
    args = parser.parse_args(argv)

    if args.selfplay:
        return _selfplay(args.depth)
    if args.demo:
        return _demo(args.depth, args.easy)
    return _interactive(args.depth, args.easy)


def _selfplay(depth: int) -> int:
    wins = draws = losses = 0
    games = 20
    for i in range(games):
        game = Connect4()
        first, second = AI, HUMAN  # 强 AI 先手，随机 AI 后手
        random.seed(1000 + i)
        turn = first
        while not game.is_terminal():
            col = ai_move(game, depth) if turn == AI else easy_move(game)
            game.drop(col, turn)
            turn = second if turn == first else AI
        w = game.winner()
        if w == AI:
            wins += 1
        elif w is None:
            draws += 1
        else:
            losses += 1
    print(f"自我对战 {games} 局：强 AI 胜 {wins}，平 {draws}，负 {losses}")
    return 0


def _demo(depth: int, easy: bool) -> int:
    game = Connect4()
    turn, turn_name = AI, "AI(○)"
    random.seed(42)
    while not game.is_terminal():
        col = easy_move(game) if (easy and turn == AI) else ai_move(game, depth)
        game.drop(col, turn)
        print(f"{turn_name} 走第 {col + 1} 列")
        print(game.render())
        print()
        turn = HUMAN if turn == AI else AI
        turn_name = "对手(●)" if turn == HUMAN else "AI(○)"
    w = game.winner()
    print("AI 获胜！" if w == AI else ("对手获胜！" if w == HUMAN else "平局！"))
    return 0


def _interactive(depth: int, easy: bool) -> int:
    game = Connect4()
    print("欢迎来到四子棋！你是 ●，AI 是 ○。输入 1-7 选择列，q 退出。\n")
    print(game.render())
    print()
    while not game.is_terminal():
        # 人类回合
        while True:
            try:
                raw = input("轮到你了，请输入列号 (1-7): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n游戏结束，谢谢游玩！")
                return 0
            if raw.lower() in ("q", "quit", "退出"):
                print("游戏结束，谢谢游玩！")
                return 0
            if not raw.isdigit() or not 1 <= int(raw) <= 7:
                print("请输入 1-7 的数字。")
                continue
            col = int(raw) - 1
            if not game.drop(col, HUMAN):
                print("这一列已经满了，请换一列。")
                continue
            break
        print(game.render())
        print()
        w = game.winner()
        if w == HUMAN:
            print("恭喜，你赢了！🎉")
            return 0
        if game.full():
            print("平局！")
            return 0
        # AI 回合
        col = easy_move(game) if easy else ai_move(game, depth)
        game.drop(col, AI)
        print(f"AI 走第 {col + 1} 列")
        print(game.render())
        print()
    w = game.winner()
    print("AI 获胜！" if w == AI else "平局！")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
