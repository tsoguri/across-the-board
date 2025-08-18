from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Tuple

from src.crossword.clue_generator import CrosswordClue


@dataclass
class Placement:
    word: str
    row: int
    col: int
    direction: Literal["across", "down"]
    clue: str


class CrosswordGenerator:
    EMPTY = "#"
    PADDING = 2
    MAX_SIZE_MULTIPLIER = 3

    def __init__(self, clues: List[CrosswordClue]):
        self.clues = sorted(clues, key=lambda x: len(x.answer.strip()), reverse=True)
        self.words: List[str] = [
            c.answer.strip().upper() for c in self.clues if c.answer.strip()
        ]
        if not self.words:
            raise ValueError("No valid words provided.")
        self.word_set = set(self.words)
        self.clue_map: Dict[str, str] = {
            c.answer.strip().upper(): c.clue for c in self.clues
        }

        self.longest = len(self.words[0])
        self.grid_size = max(self.longest + self.PADDING * 2, self.longest)
        self.grid_size = min(self.grid_size, self.longest * self.MAX_SIZE_MULTIPLIER)

        self.grid: List[List[str]] = [
            [self.EMPTY for _ in range(self.grid_size)] for _ in range(self.grid_size)
        ]
        self.placements: List[Placement] = []

    def generate(self) -> Tuple[List[List[str]], List[Placement]]:
        self._place_first()

        remaining = [w for w in self.words[1:]]
        progress = True

        while remaining and progress:
            progress = False
            next_remaining = []
            for word in remaining:
                if self._place_by_intersection(word):
                    progress = True
                else:
                    next_remaining.append(word)
            remaining = next_remaining
        return self.grid, self.placements

    def _place_first(self) -> None:
        first = self.words[0]
        row = self.grid_size // 2
        start_col = max(0, (self.grid_size - len(first)) // 2)
        start_col = min(start_col, self.grid_size - len(first))
        self._commit(first, row, start_col, direction="across")

    def _place_by_intersection(self, word: str) -> bool:
        for placed in self.placements:
            for i, ch in enumerate(word):
                for j, pc in enumerate(placed.word):
                    if pc != ch:
                        continue
                    if placed.direction == "across":
                        row = placed.row - i
                        col = placed.col + j
                        if self._can_place_intersecting(word, row, col, "down"):
                            self._commit(word, row, col, "down")
                            return True
                    else:
                        row = placed.row + j
                        col = placed.col - i
                        if self._can_place_intersecting(word, row, col, "across"):
                            self._commit(word, row, col, "across")
                            return True
        return False

    def _check_cell(self, cell, ch):
        if cell != self.EMPTY and cell != ch:
            return False
        return True

    def _can_place_intersecting(
        self, word: str, row: int, col: int, direction: str
    ) -> bool:
        """Strict validator: inside bounds, no conflicts, touches existing,
        no illegal side-adjacency, and all perpendicular runs (len>=2) form valid words.
        """
        if direction not in ("across", "down"):
            return False
        if row < 0 or col < 0:
            return False
        # Bounds check
        if direction == "across":
            if col + len(word) > self.grid_size:
                return False
        else:
            if row + len(word) > self.grid_size:
                return False

        temp_grid = [row[:] for row in self.grid]

        for k, ch in enumerate(word):
            r = row + (k if direction == "down" else 0)
            c = col + (k if direction == "across" else 0)
            cell = self.grid[r][c]
            if cell != self.EMPTY and cell != ch:
                return False
            temp_grid[r][c] = ch

        # Check cells before/after word boundaries to avoid butt-joins
        br, bc = (row, col - 1) if direction == "across" else (row - 1, col)
        ar, ac = (
            (row, col + len(word)) if direction == "across" else (row + len(word), col)
        )
        if self._in_bounds(br, bc) and self.grid[br][bc] != self.EMPTY:
            return False
        if self._in_bounds(ar, ac) and self.grid[ar][ac] != self.EMPTY:
            return False

        for r in range(self.grid_size):
            for c in range(self.grid_size):
                for axis in ["across", "down"]:
                    run = self._collect_run(r, c, axis, temp_grid)
                    if len(run) > 1:
                        if run not in self.word_set:
                            return False

        return True

    def _collect_run(self, r: int, c: int, axis: str, grid) -> str:
        # Gather contiguous filled letters along the given axis ("across" or "down")
        if axis == "across":
            # extend left
            cc = c
            while cc - 1 >= 0 and grid[r][cc - 1] != self.EMPTY:
                cc -= 1
            # build right
            letters = []
            while cc < self.grid_size and grid[r][cc] != self.EMPTY:
                letters.append(grid[r][cc])
                cc += 1
            return "".join(letters)
        else:  # down
            rr = r
            while rr - 1 >= 0 and grid[rr - 1][c] != self.EMPTY:
                rr -= 1
            letters = []
            while rr < self.grid_size and grid[rr][c] != self.EMPTY:
                letters.append(grid[rr][c])
                rr += 1
            return "".join(letters)

    def _commit(self, word: str, row: int, col: int, direction: str) -> None:
        for k, ch in enumerate(word):
            r = row + (k if direction == "down" else 0)
            c = col + (k if direction == "across" else 0)
            self.grid[r][c] = ch
        clue_text = self.clue_map.get(word, "")
        self.placements.append(Placement(word, row, col, direction, clue_text))

    def _in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.grid_size and 0 <= c < self.grid_size
