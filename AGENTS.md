# AGENTS.md — 2026MD

## What this is

Lecture repository for **Media creation Data design 1 (MD1)** — a first-year Python/py5 course at Musashino University taught by Ryo Nakamura. Two independent sub-projects live side-by-side here.

## Sub-projects

| Area | Type | Entrypoint |
|------|------|-----------|
| `docs/` | HTML lecture slides (dark theme, Japanese) | `docs/week*.html` |
| Root `.py` files | py5 demos (ship tracker, ocean drift) | `moving_circles.py`, `ocean_drift_lab.py` |
| `MD/`, `No?/`, `no?/` | Per-week student code templates | `MD/step1-1.py` etc. |
| `slack-class-bot/` | Slack bot (Bolt JS + Google APIs + Panopto) | `slack-class-bot/app.js` |

## Developer commands

```bash
# ---- Python py5 demos ----
source py5_env/bin/activate
pip install py5 websocket-client requests numpy Pillow
python3 moving_circles.py
python3 ocean_drift_lab.py

# ---- Node.js Slack bot ----
cd slack-class-bot && npm install
npm start        # node app.js
npm run dev      # node --watch app.js
```

## Lecture HTML workflow

1. Each `docs/week*.html` is a standalone page using `_template_head.html` (embedded CSS) and `_template_foot.html`
2. Answer sections live inside `<div id="answers-content">` and are **encrypted** before publishing
3. **Encrypt answers**: `node docs/encrypt-answers.js <password> docs/weekX.html`
4. **Decrypt answers**: `node docs/decrypt-answers.js <password> docs/weekX.html`
5. Encrypted answers use PBKDF2(100k) + AES-256-GCM; client-side `docs/answer-gate.js` controls release-by-date or password unlock
6. Each week should use a **different password** — do not use `--all` for production
7. `docs/week01-02.html` and `docs/_template_*` are gitignored

## Git conventions

```
feat(weekX): <Japanese description>
fix(weekX):  <Japanese description>
docs(weekX): <Japanese description>
```

## Course policy to remember

> AI use is always permitted. What matters is not "can you make it?" but "can you explain it?"

Three deliverables per session: code + rationale memo + input/expected-output table.

## Environment quirks

- Multiple venvs scattered: `py5_env/` (root), `MD/.venv/`, `No3/.venv/`, `no4/.venv/`
- No `requirements.txt` — install deps manually per sub-project
- No CI, no test framework, no linter config (Ruff cache dir exists but no config)
- `slack-class-bot/` is gitignored but files are tracked (added before `.gitignore` entry)
- Bot server: `202.240.109.50`, runs via `nohup node app.js >> bot.log 2>&1 &`
- Panopto token renewal: auth locally, `scp panopto-token.json <server>`
- Student toolchain: Homebrew → uv → Python 3.12 → JDK (Temurin 21) → py5 → VS Code
