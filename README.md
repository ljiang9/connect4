# connect4 · 四子棋人机对战

一个纯本地的终端四子棋小游戏：你执 ●，AI 执 ○，轮流在 7×6 棋盘落子，先连成 4 子者获胜。

AI 用**带 alpha-beta 剪枝的深度受限 minimax**（默认深度 4）走棋，并偏好占据中心列。另有 `--easy` 纯随机 AI 适合新手练手。

## 运行要求

- Python 3.10+，仅标准库（`argparse`、`sys`、`random`），零依赖。

## 用法

```bash
# 交互对战（默认：强 AI，深度 4）
python3 -m connect4

# 简单模式：AI 随机走棋
python3 -m connect4 --easy

# 演示模式：双方 AI 自动下一局并打印棋盘
python3 -m connect4 --demo

# 自我对战：强 AI（先手） vs 随机 AI，打 20 局统计胜率
python3 -m connect4 --selfplay

# 调整搜索深度（越大越强、越慢）
python3 -m connect4 --depth 5
```

交互中输入 `1-7` 选择列落子，`q` 退出。满列会提示重选，不会吞掉你的回合。

## AI 说明

- 强 AI：深度 4 minimax + alpha-beta 剪枝 + 中心列偏好；走子前会先找“一步即胜”，也会封堵对手的“一步即胜”。
- 已验证：20 局自我对战（强 AI 先手 vs 随机 AI）强 AI 20 胜 0 平 0 负。
- 诚实声明：这是**深度受限**的搜索，不是完美解法。深度 4 看不到 5 步以上的陷阱，高手仍可能设局获胜；`--depth 5` 更强但每步明显变慢。

## 已知限制

- 终端字符界面，无图形化棋盘；棋子用 `●`/`○` 表示，需要终端支持 Unicode。
- 深度 5 以上在普通机器上每步可能耗时数秒，请按机器性能选择。
- 不支持悔棋、存档、双人对战。

## 文件

- `connect4.py` — 全部逻辑（棋盘、胜负判定、minimax AI、CLI）
- `__main__.py` — `python -m connect4` 入口
- `LICENSE` — MIT
