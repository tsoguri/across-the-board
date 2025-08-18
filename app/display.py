from typing import List

import pandas as pd
import streamlit as st

from src.crossword.crossword_generator import CrosswordGenerator, Placement


def display_crossword(grid: List[List[str]], show_answer: bool = False):
    """Render the crossword grid as a colored dataframe in Streamlit."""
    if show_answer:
        df = pd.DataFrame(grid)
    else:
        empty_grid = [
            [cell if cell == CrosswordGenerator.EMPTY else "" for cell in row]
            for row in grid
        ]
        df = pd.DataFrame(empty_grid)

    def color_cells(val):
        if val == CrosswordGenerator.EMPTY:
            return "background-color: black; color: black"
        else:
            return "background-color: white; color: black; text-align: center"

    # df = df.replace(CrosswordGenerator.EMPTY, "⬛⬛")
    styled = df.style.applymap(color_cells)
    st.dataframe(styled, height=(len(df) + 1) * 35)
    # st.data_editor(df, height=(len(df) + 1) * 35)


def display_placements(placements: List[Placement], show_answer: bool = False):
    """Display the crossword clues in Streamlit, split into Across and Down."""

    st.write("### Clues")
    across = [p for p in placements if p.direction == "across"]
    down = [p for p in placements if p.direction == "down"]
    across.sort(key=lambda p: (p.row, p.col))
    down.sort(key=lambda p: (p.col, p.row))
    c1, c2 = st.columns(2)

    def render(title: str, items: List[Placement]):
        st.write(f"**{title}**")
        for p in items:
            clue_text = f"[Row {p.row}][Col {p.col}] {p.clue}"
            if show_answer:
                clue_text += f" ({p.word})"
            st.write(clue_text)

    with c1:
        render("Across", across)
    with c2:
        render("Down", down)
