"""Metrica Sports の本物のトラッキングデータ（Sample Game 1）を分析・可視化する（10例）。
ホーム/アウェイのフィールド利用ヒートマップなどを、サッカーピッチ上に描画する。

■ データの入手（無料・公開データ）
  Metrica Sports が研究・教育向けに公開しているサンプルデータ。次の2ファイルを
  このスクリプトと同じフォルダに置く（ファイル名を home.csv / away.csv に変える）:
    home.csv ← Sample_Game_1_RawTrackingData_Home_Team.csv
    away.csv ← Sample_Game_1_RawTrackingData_Away_Team.csv
  取得元（どちらでも）:
    - GitHub: https://github.com/metrica-sports/sample-data （data/Sample_Game_1/）
    - Kaggle: https://www.kaggle.com/datasets/ekrembayar/metrica-sports-football-tracking-data
  ダウンロード例（ターミナル）:
    B=https://raw.githubusercontent.com/metrica-sports/sample-data/master/data/Sample_Game_1
    curl -L "$B/Sample_Game_1_RawTrackingData_Home_Team.csv" -o home.csv
    curl -L "$B/Sample_Game_1_RawTrackingData_Away_Team.csv" -o away.csv

■ 実行
    uv pip install pandas matplotlib
    python metrica_analysis.py       # anal_01.png 〜 anal_10.png が出力される

※ 生の座標は 0〜1 に正規化されている。メートル(中心が原点)に変換し、後半は
   攻撃方向がそろうように 180度回転してから集計する（分析の定番の前処理）。
"""
import csv, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

plt.rcParams["font.family"] = ["Hiragino Sans", "Meiryo", "IPAexGothic", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

FIELD = (105.0, 68.0)
L, W = FIELD[0] / 2, FIELD[1] / 2
BLUE, RED = "#2196f3", "#f44336"
STEP = 5   # 25fps → 5fps に間引き（軽くするため）


def read_team(fname, team):
    """Metrica形式のCSVを読み、メートル座標＋攻撃方向をそろえて返す。"""
    with open(fname) as fp:
        r = csv.reader(fp); next(r)
        jerseys = [x for x in next(r) if x != '']
        cols = next(r)
    for i, j in enumerate(jerseys):
        cols[i * 2 + 3] = team + "_" + j + "_x"
        cols[i * 2 + 4] = team + "_" + j + "_y"
    cols[-2], cols[-1] = "ball_x", "ball_y"
    df = pd.read_csv(fname, names=cols, skiprows=3)
    xs = [c for c in df.columns if c.endswith("_x")]
    ys = [c for c in df.columns if c.endswith("_y")]
    df[xs] = (df[xs] - 0.5) * FIELD[0]        # 0〜1 → メートル(中心が原点)
    df[ys] = -1 * (df[ys] - 0.5) * FIELD[1]
    df.loc[df.Period == 2, xs + ys] *= -1      # 後半は攻撃方向をそろえる
    return df


def melt(df, team):
    """各選手の (x,y) を縦に積んで long 形式 {frame,team,id,x,y} にする。"""
    out = []
    d = df.iloc[::STEP]
    for cx in [c for c in d.columns if c.startswith(team + "_") and c.endswith("_x")]:
        pid = int(cx.split("_")[1]); cy = cx[:-2] + "_y"
        s = d[["Frame", cx, cy]].dropna().rename(columns={"Frame": "frame", cx: "x", cy: "y"})
        s["team"] = team.lower(); s["id"] = pid
        out.append(s)
    return pd.concat(out, ignore_index=True)


H = read_team("home.csv", "Home")
A = read_team("away.csv", "Away")
home, away = melt(H, "Home"), melt(A, "Away")
ball = H.iloc[::STEP][["Frame", "ball_x", "ball_y"]].dropna() \
        .rename(columns={"Frame": "frame", "ball_x": "x", "ball_y": "y"})
ball["team"] = "ball"; ball["id"] = 0


def draw_pitch(ax, bg="#2e7d32", line="white"):
    ax.add_patch(Rectangle((-L, -W), 105, 68, facecolor=bg, edgecolor=line, lw=1.6, zorder=0))
    ax.plot([0, 0], [-W, W], color=line, lw=1.4, zorder=2)
    ax.add_patch(Circle((0, 0), 9.15, fill=False, ec=line, lw=1.4, zorder=2))
    ax.add_patch(Circle((0, 0), 0.5, color=line, zorder=2))
    for s in (-L, L - 16.5):
        ax.add_patch(Rectangle((s, -20.16), 16.5, 40.32, fill=False, ec=line, lw=1.4, zorder=2))
    for s in (-L, L - 5.5):
        ax.add_patch(Rectangle((s, -9.16), 5.5, 18.32, fill=False, ec=line, lw=1.4, zorder=2))
    ax.set_xlim(-56, 56); ax.set_ylim(-38, 38); ax.set_aspect("equal"); ax.axis("off")


def save(fig, name, title):
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(name, facecolor="white", bbox_inches="tight"); plt.close(fig)
    print("saved", name)


def heatmap(sub, name, title):
    fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax)
    Hh, _, _ = np.histogram2d(sub.x, sub.y, bins=[50, 32], range=[[-L, L], [-W, W]])
    Hm = np.where(Hh.T > 0, Hh.T, np.nan)
    c = plt.get_cmap("YlOrRd").copy(); c.set_bad(alpha=0)
    ax.imshow(Hm, extent=[-L, L, -W, W], origin="lower", cmap=c, alpha=0.8,
              vmax=np.nanpercentile(Hh[Hh > 0], 97), interpolation="bilinear", zorder=1)
    save(fig, name, title)


heatmap(home, "anal_01.png", "1. ホームのフィールド利用ヒートマップ（Metrica実データ）")
heatmap(away, "anal_02.png", "2. アウェイのフィールド利用ヒートマップ（Metrica実データ）")
heatmap(ball, "anal_03.png", "3. ボールのフィールド利用ヒートマップ（Metrica実データ）")

# 4. 陣地の優勢
fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax, bg="#20402a")
Hh, _, _ = np.histogram2d(home.x, home.y, bins=[50, 32], range=[[-L, L], [-W, W]])
Ha, _, _ = np.histogram2d(away.x, away.y, bins=[50, 32], range=[[-L, L], [-W, W]])
D = (Hh - Ha).T; m = np.nanpercentile(np.abs(D), 99) or 1
ax.imshow(D, extent=[-L, L, -W, W], origin="lower", cmap="bwr_r", vmin=-m, vmax=m,
          alpha=0.85, interpolation="bilinear", zorder=1)
ax.text(-L + 3, -W + 2, "青=ホーム優勢", color=BLUE, fontsize=9, fontweight="bold")
ax.text(L - 22, -W + 2, "赤=アウェイ優勢", color=RED, fontsize=9, fontweight="bold")
save(fig, "anal_04.png", "4. 陣地の優勢（ホーム − アウェイの密度差）")

# 5・6 平均ポジション（出場上位11人）
for tdf, col, name, title in [
    (home, BLUE, "anal_05.png", "5. ホームの平均ポジション（出場上位11人）"),
    (away, RED, "anal_06.png", "6. アウェイの平均ポジション（出場上位11人）"),
]:
    fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax)
    g = tdf[tdf.id.isin(tdf.id.value_counts().head(11).index)].groupby("id")[["x", "y"]].mean()
    ax.scatter(g.x, g.y, s=520, c=col, edgecolors="white", linewidths=1.5, zorder=3)
    for pid, row in g.iterrows():
        ax.text(row.x, row.y, str(int(pid)), color="white", ha="center", va="center",
                fontsize=9, fontweight="bold", zorder=4)
    save(fig, name, title)

# 7. 移動距離
def dist_by_id(tdf):
    res = {}
    for pid, s in tdf.sort_values("frame").groupby("id"):
        step = np.sqrt(s.x.diff() ** 2 + s.y.diff() ** 2)
        res[pid] = float(step[s.frame.diff() == STEP].sum())
    return res

rows = []
for tdf, tag in [(home, "H"), (away, "A")]:
    top = tdf[tdf.id.isin(tdf.id.value_counts().head(11).index)]
    for pid, v in dist_by_id(top).items():
        rows.append((tag + str(int(pid)), tag, v))
dist = pd.DataFrame(rows, columns=["label", "t", "dist"]).sort_values("dist")
fig, ax = plt.subplots(figsize=(7.2, 6.0))
ax.barh(dist.label, dist.dist / 1000, color=[BLUE if t == "H" else RED for t in dist.t])
ax.set_xlabel("移動距離の合計 [km]（5fpsでの概算・相対比較）"); ax.grid(axis="x", alpha=0.3)
save(fig, "anal_07.png", "7. 選手ごとの移動距離（青=ホーム / 赤=アウェイ）")

# 8. ボールの軌跡（前半15分）
fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax)
seg = ball[ball.frame < 25 * 60 * 15]
ax.plot(seg.x, seg.y, color="yellow", lw=0.5, alpha=0.7, zorder=2)
save(fig, "anal_08.png", "8. ボールの軌跡（試合開始〜15分）")

# 9. チーム重心Xの時間変化
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ch = home.groupby("frame").x.mean(); ca = away.groupby("frame").x.mean()
ax.plot(ch.index / 25 / 60, ch.values, color=BLUE, lw=0.5, alpha=0.85, label="ホーム重心X")
ax.plot(ca.index / 25 / 60, ca.values, color=RED, lw=0.5, alpha=0.85, label="アウェイ重心X")
ax.axhline(0, color="#888", lw=0.8)
ax.set_xlabel("試合時間 [分]"); ax.set_ylabel("重心のX座標 [m]"); ax.legend(); ax.grid(alpha=0.3)
save(fig, "anal_09.png", "9. チーム重心X の時間変化（攻め上がり／守り）")

# 10. 両チーム重心の軌跡
fig, ax = plt.subplots(figsize=(7.2, 4.9)); draw_pitch(ax)
ax.plot(home.groupby("frame").x.mean(), home.groupby("frame").y.mean(), color=BLUE, lw=0.3, alpha=0.5)
ax.plot(away.groupby("frame").x.mean(), away.groupby("frame").y.mean(), color=RED, lw=0.3, alpha=0.5)
save(fig, "anal_10.png", "10. 両チーム重心の軌跡（青=ホーム / 赤=アウェイ）")

print("done: anal_01.png 〜 anal_10.png を出力しました")
