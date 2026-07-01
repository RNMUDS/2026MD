"""soccer.csv を pandas + matplotlib で分析・可視化する（10例）。
ウプサラ大学 David Sumpter の講座スタイル。ホーム/アウェイのフィールド利用
ヒートマップなど、サッカーピッチ上に描画する。

使い方（第3回の手順で pandas と matplotlib を入れてから）:
    uv pip install pandas matplotlib
    python soccer_analysis.py            # soccer.csv と同じフォルダで実行
→ anal_01.png 〜 anal_10.png が生成される。

※ soccer.csv は教材用の合成サンプル。本物のトラッキングデータ（Metrica など）でも、
   列名・単位を合わせれば同じコードで分析できる。
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# 日本語フォント（環境に合わせて。Windows は "Meiryo"、Linux は "IPAexGothic" など）
plt.rcParams["font.family"] = ["Hiragino Sans", "Meiryo", "IPAexGothic", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("soccer.csv")
home = df[df["team"] == "home"]
away = df[df["team"] == "away"]
ball = df[df["team"] == "ball"]

BLUE, RED = "#2196f3", "#f44336"
L, W = 52.5, 34.0   # ピッチ半分（105m × 68m、中心が原点）


def draw_pitch(ax, bg="#2e7d32", line="white"):
    """緑のサッカーピッチと白線を描く。"""
    ax.add_patch(Rectangle((-L, -W), 105, 68, facecolor=bg, edgecolor=line, lw=1.6, zorder=0))
    ax.plot([0, 0], [-W, W], color=line, lw=1.4, zorder=2)            # ハーフウェイライン
    ax.add_patch(Circle((0, 0), 9.15, fill=False, ec=line, lw=1.4, zorder=2))  # センターサークル
    ax.add_patch(Circle((0, 0), 0.5, color=line, zorder=2))
    for s in (-L, L - 16.5):                                          # ペナルティエリア
        ax.add_patch(Rectangle((s, -20.16), 16.5, 40.32, fill=False, ec=line, lw=1.4, zorder=2))
    for s in (-L, L - 5.5):                                           # ゴールエリア
        ax.add_patch(Rectangle((s, -9.16), 5.5, 18.32, fill=False, ec=line, lw=1.4, zorder=2))
    ax.set_xlim(-56, 56); ax.set_ylim(-38, 38)
    ax.set_aspect("equal"); ax.axis("off")


def heatmap(sub, title, fname):
    """選手/ボールの位置を2次元ヒストグラムにして、ピッチ上にヒートマップ表示。"""
    fig, ax = plt.subplots(figsize=(7.2, 4.9))
    draw_pitch(ax)
    H, _, _ = np.histogram2d(sub["x"], sub["y"], bins=[42, 28],
                             range=[[-L, L], [-W, W]])
    H = np.where(H.T > 0, H.T, np.nan)          # 0のマスは透明に
    cmap = plt.get_cmap("YlOrRd").copy(); cmap.set_bad(alpha=0)
    ax.imshow(H, extent=[-L, L, -W, W], origin="lower", cmap=cmap,
              alpha=0.78, interpolation="bilinear", zorder=1)
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.savefig(fname, bbox_inches="tight", facecolor="white"); plt.close(fig)


# 1〜3: フィールド利用ヒートマップ（ホーム / アウェイ / ボール）
heatmap(home, "1. ホームチームのフィールド利用ヒートマップ", "anal_01.png")
heatmap(away, "2. アウェイチームのフィールド利用ヒートマップ", "anal_02.png")
heatmap(ball, "3. ボールのフィールド利用ヒートマップ", "anal_03.png")

# 4: 陣地の優勢（ホーム − アウェイの密度差）
fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax, bg="#20402a")
Hh, _, _ = np.histogram2d(home["x"], home["y"], bins=[42, 28], range=[[-L, L], [-W, W]])
Ha, _, _ = np.histogram2d(away["x"], away["y"], bins=[42, 28], range=[[-L, L], [-W, W]])
D = (Hh - Ha).T; m = np.max(np.abs(D)) or 1
ax.imshow(D, extent=[-L, L, -W, W], origin="lower", cmap="bwr_r",
          vmin=-m, vmax=m, alpha=0.8, interpolation="bilinear", zorder=1)
fig.suptitle("4. 陣地の優勢（青=ホーム / 赤=アウェイ）", fontsize=13, fontweight="bold")
fig.savefig("anal_04.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# 5・6: 平均フォーメーション（各選手の平均位置）
for team_df, col, title, fname in [
    (home, BLUE, "5. ホームの平均フォーメーション", "anal_05.png"),
    (away, RED, "6. アウェイの平均フォーメーション", "anal_06.png"),
]:
    fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax)
    g = team_df.groupby("id")[["x", "y"]].mean()
    ax.scatter(g["x"], g["y"], s=520, c=col, edgecolors="white", linewidths=1.5, zorder=3)
    for pid, row in g.iterrows():
        ax.text(row["x"], row["y"], str(int(pid)), color="white",
                ha="center", va="center", fontsize=9, fontweight="bold", zorder=4)
    fig.suptitle(title, fontsize=13, fontweight="bold")
    fig.savefig(fname, bbox_inches="tight", facecolor="white"); plt.close(fig)

# 7: 選手ごとの移動距離
def total_distance(sub):
    sub = sub.sort_values("frame")
    dx, dy = sub["x"].diff(), sub["y"].diff()
    return float(np.sqrt(dx * dx + dy * dy).sum())

rows = [(("H" if tm == "home" else "A") + str(int(pid)), tm, total_distance(sub))
        for (tm, pid), sub in df[df.team != "ball"].groupby(["team", "id"])]
dist = pd.DataFrame(rows, columns=["label", "team", "dist"]).sort_values("dist")
fig, ax = plt.subplots(figsize=(7.2, 5.2))
ax.barh(dist["label"], dist["dist"],
        color=[BLUE if t == "home" else RED for t in dist["team"]])
ax.set_xlabel("移動距離の合計 [m]"); ax.grid(axis="x", alpha=0.3)
fig.suptitle("7. 選手ごとの移動距離", fontsize=13, fontweight="bold")
fig.savefig("anal_07.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# 8: ボールの軌跡
fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax)
b = ball.sort_values("frame")
ax.plot(b["x"], b["y"], color="yellow", lw=0.8, alpha=0.8, zorder=2)
fig.suptitle("8. ボールの軌跡（90分）", fontsize=13, fontweight="bold")
fig.savefig("anal_08.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# 9: チーム重心Xの時間変化
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ch = home.groupby("frame")["x"].mean(); ca = away.groupby("frame")["x"].mean()
ax.plot(ch.index / 60, ch.values, color=BLUE, lw=1.2, label="ホーム重心X")
ax.plot(ca.index / 60, ca.values, color=RED, lw=1.2, label="アウェイ重心X")
ax.axhline(0, color="#888", lw=0.8)
ax.set_xlabel("試合時間 [分]"); ax.set_ylabel("重心のX座標 [m]")
ax.legend(); ax.grid(alpha=0.3)
fig.suptitle("9. チーム重心X の時間変化（攻め上がり／守り）", fontsize=13, fontweight="bold")
fig.savefig("anal_09.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

# 10: 両チーム重心の軌跡
fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax)
hx = home.groupby("frame")["x"].mean(); hy = home.groupby("frame")["y"].mean()
ax_ = away.groupby("frame")["x"].mean(); ay = away.groupby("frame")["y"].mean()
ax.plot(hx, hy, color=BLUE, lw=0.7, alpha=0.7)
ax.plot(ax_, ay, color=RED, lw=0.7, alpha=0.7)
fig.suptitle("10. 両チーム重心の軌跡", fontsize=13, fontweight="bold")
fig.savefig("anal_10.png", bbox_inches="tight", facecolor="white"); plt.close(fig)

print("done: anal_01.png 〜 anal_10.png を出力しました")
