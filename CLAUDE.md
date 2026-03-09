# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Single-file web game: `tictactoe.html` — a fully self-contained Tic Tac Toe game with no build step, no dependencies, and no package manager.

## Running the Project

Open `tictactoe.html` directly in a browser:
```bash
start tictactoe.html
```

## Architecture

Everything lives in one file (`tictactoe.html`):
- **HTML** — 3×3 board as `div.cell[data-i]` elements, score boxes, and control buttons
- **CSS** — dark theme (`#1a1a2e` background), grid layout, win highlight via `.win` class
- **JavaScript** — inline `<script>` at bottom of body

### Key JS State
- `board` — 9-element array (`''`, `'X'`, or `'O'`)
- `current` — whose turn (`'X'` or `'O'`)
- `vsComputer` — boolean toggle for AI mode
- `scores` — `{ X, O, T }` persisted across games in memory

### Game Logic
- `makeMove(i)` — handles a move, checks result, triggers computer move if needed
- `checkWinner()` — checks `WINS` (8 win combos) against live `board`
- `checkWinnerBoard(b)` — pure version used by minimax
- `minimax(b, isMax)` — recursive minimax AI (plays perfectly as `'O'`)
- `computerMove()` — picks best move via minimax with 300ms delay

## GitHub
Repository: https://github.com/Maghrur13/CluadeTest

Auto-commit hook is active — every file Write/Edit is automatically committed and pushed to GitHub.
