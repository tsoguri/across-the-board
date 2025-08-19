from typing import List, Optional

import numpy as np
import pandas as pd
import streamlit as st

from app.constants import BLOCK_TOKEN, CHAT_TYPE, CLAUDE_MODELS, DIFFICULTY_LEVEL
from src.chat.chat_service import ChatService
from src.crossword.clue_generator import ClueGenerator
from src.crossword.crossword_generator import (
    CrosswordClue,
    CrosswordGenerator,
    Placement,
)


class AppDisplay:
    def __init__(self):
        self.init_session_states()

    def draw(self):
        submitted = self.display_crossword_form()
        if submitted:
            self.generate_crossword()
        if (
            st.session_state.grid is not None
            and st.session_state.placements is not None
        ):
            st.success("Generated crossword successfully")
            col1, col2 = st.columns(2)
            with col1:
                self.display_crossword()
            with col2:
                self.display_chat()
        elif submitted:
            st.error("Could not generate crossword; please try again")

    def init_session_states(self):
        for k, v in [
            ("topics", ""),
            ("difficulty_level", DIFFICULTY_LEVEL[0]),
            ("grid", None),
            ("placements", None),
            ("show_answers", False),
            ("clue_model", CLAUDE_MODELS[0]),
            ("num_clues", 30),
            ("editable", True),
            ("user_grid", None),
            ("chat_type", CHAT_TYPE[0]),
            ("prev_chat_type", CHAT_TYPE[0]),
            ("chat_history", []),
            ("selected_clue", None),
            ("last_selected_clue_idx", None),
            ("pending_clue_response", False),
        ]:
            if k not in st.session_state:
                st.session_state[k] = v

    def display_crossword_form(self):
        with st.form("crossword_form", clear_on_submit=False):
            topics = st.text_input(
                "Enter any topics you want to learn about (comma-separated)",
                value=st.session_state.topics,
                placeholder="e.g. Classical Music, Theoretical Physics, Gastronomy",
                help="What do you want your crossword to be about?",
            )
            difficulty_level = st.selectbox(
                "Select difficulty level",
                options=DIFFICULTY_LEVEL,
                index=DIFFICULTY_LEVEL.index(st.session_state.difficulty_level),
                help="How difficult do you want your crossword to be?",
            )
            with st.expander("Advanced Settings"):
                clue_model = st.selectbox(
                    "Select clue generation model",
                    options=CLAUDE_MODELS,
                    index=CLAUDE_MODELS.index(st.session_state.clue_model),
                )
                num_clues = st.number_input(
                    label="Number of clues to generate",
                    min_value=10,
                    max_value=50,
                    value=st.session_state.num_clues,
                    step=1,
                )
            submitted = st.form_submit_button("Generate Crossword")
        if submitted:
            st.session_state.topics = topics
            st.session_state.difficulty_level = difficulty_level
            st.session_state.clue_model = clue_model
            st.session_state.num_clues = num_clues
        return submitted

    def reset_non_form_states(self):
        """Reset all session states except the form-driving ones."""
        preserved_keys = {"topics", "difficulty_level", "clue_model", "num_clues"}
        defaults = {
            "grid": None,
            "placements": None,
            "show_answers": False,
            "editable": True,
            "user_grid": None,
            "chat_type": CHAT_TYPE[0],
            "prev_chat_type": CHAT_TYPE[0],
            "chat_history": [],
            "selected_clue": None,
            "last_selected_clue_idx": None,
            "pending_clue_response": False,
        }
        for k, v in defaults.items():
            if k not in preserved_keys:
                st.session_state[k] = v

    def generate_crossword(self):
        self.reset_non_form_states()
        with st.spinner("Setting up your crossword..."):
            clue_generator = ClueGenerator(model=st.session_state.clue_model)
        with st.spinner("Generating clues..."):
            clue_response = clue_generator.generate_clues(
                topic_str=st.session_state.topics,
                difficulty=st.session_state.difficulty_level,
                num_clues=st.session_state.num_clues,
            )
        if clue_response:
            with st.spinner("Creating crossword..."):
                crossword_generator = CrosswordGenerator(clues=clue_response.clues)
                grid, placements = crossword_generator.generate()
                st.session_state.grid = grid
                st.session_state.placements = sorted(
                    sorted(placements, key=lambda x: x.col), key=lambda x: x.row
                )
                st.session_state.user_grid = None
        else:
            st.session_state.grid = None
            st.session_state.placements = None
            st.session_state.user_grid = None

    def display_crossword(self):
        st.write("### ✍️ Crossword")
        col1, col2, _ = st.columns([1, 1, 3])

        # Modified: Remove the on_change callbacks that were causing the issue
        st.session_state.editable = col1.toggle(
            "Editable grid",
            value=st.session_state.editable,
            key="editable_toggle",
        )
        col2.toggle(
            "Show answers",
            key="show_answers",
        )

        self.render_crossword(
            st.session_state.grid,
            show_answer=st.session_state.show_answers,
            editable=st.session_state.editable,
        )

        self.render_placements(
            st.session_state.placements, show_answer=st.session_state.show_answers
        )

    def display_chat(self):
        st.write("### 📚 Learn")
        self.render_chat_settings()

        if not st.session_state.selected_clue:
            st.info("Select a clue above to start a conversation.")
            return

        chat_service = ChatService(model=CLAUDE_MODELS[1])
        if st.session_state.pending_clue_response:
            self._get_opener_response(chat_service=chat_service)

        messages_container = st.container(height=500, border=True)
        self.render_messages(messages_container)
        user_text = st.chat_input("Ask me anything!", key="chat_input_main")
        if user_text:
            self.render_chat_response(chat_service, messages_container, user_text)
            st.rerun()

    def render_chat_response(self, chat_service, messages_container, user_text):
        with messages_container.chat_message("user"):
            st.session_state.chat_history.append({"role": "user", "content": user_text})
            st.write(user_text)

        with messages_container.chat_message("assistant"):
            with st.spinner("Generating response..."):
                response = chat_service.generate_response(
                    user_input=user_text,
                    clue=st.session_state.selected_clue,
                    type=st.session_state.chat_type,
                    historical_messages=st.session_state.chat_history,
                )
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )
            st.write(response)

    def render_messages(self, messages_container):
        for msg in st.session_state.chat_history:
            with messages_container.chat_message(msg["role"]):
                st.write(msg["content"])

    def _get_opener_response(self, chat_service):
        opener = (
            (
                "Give me an initial direction how to think about the clue. "
                "Ask me what I know / think I know about this clue already."
            )
            if st.session_state.chat_type == CHAT_TYPE[0]
            else (
                "Provide me a brief intellectual, academic overview of this topic. "
                "Ask me if there's anything specific I want to know about this topic."
            )
        )
        response = chat_service.generate_response(
            user_input=opener,
            clue=st.session_state.selected_clue,
            type=st.session_state.chat_type,
            historical_messages=st.session_state.chat_history,
        )
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.session_state.pending_clue_response = False

    def render_chat_settings(self):
        col1, col2 = st.columns(2, vertical_alignment="bottom")
        with col1:
            chat_type = st.selectbox(
                "Type",
                options=CHAT_TYPE,
                index=CHAT_TYPE.index(st.session_state.chat_type),
                key="chat_type_select",
            )
        self._reset_chat_on_type_change(chat_type)
        with col2:
            if st.button("Clear Chat", key="clear_chat_btn"):
                st.session_state.chat_history = []
        st.session_state.chat_type = chat_type
        if st.session_state.chat_type == "Get a Hint":
            label = "some help for"
        else:
            label = "to learn more about"

        clue_options = [clue.clue for clue in st.session_state.placements]
        options = [-1] + list(range(len(clue_options)))
        if st.session_state.get("last_selected_clue_idx") is None:
            default_index = 0
        else:
            default_index = st.session_state.last_selected_clue_idx + 1

        selected_clue_idx = st.selectbox(
            label=f"Select the clue you would like {label}",
            options=options,
            index=default_index,
            format_func=lambda x: "" if x == -1 else clue_options[x],
            key="clue_select",
        )

        if selected_clue_idx != -1:  # Only set if user actually picked one
            selected_clue = st.session_state.placements[selected_clue_idx]
            st.session_state.selected_clue = CrosswordClue(
                clue=selected_clue.clue, answer=selected_clue.word
            )
            if st.session_state.last_selected_clue_idx != selected_clue_idx:
                st.session_state.chat_history = []
                st.session_state.last_selected_clue_idx = selected_clue_idx
                st.session_state.pending_clue_response = True
        elif not st.session_state.selected_clue:
            st.session_state.selected_clue = None
        elif selected_clue_idx == -1:
            st.session_state.selected_clue = None

    def _reset_chat_on_type_change(self, new_chat_type: str):
        """If the user switches chat type, clear chat and trigger a fresh opener."""
        prev = st.session_state.get("prev_chat_type", new_chat_type)
        if new_chat_type != prev:
            st.session_state.chat_history = []
            st.session_state.pending_clue_response = True
        st.session_state.prev_chat_type = new_chat_type

    def _sync_user_grid(
        self, grid: pd.DataFrame, editor_key: str = "grid_editor"
    ) -> None:
        """Callback: convert what's shown in the editor back into the internal user_grid."""
        if editor_key not in st.session_state:
            return

        raw_val = st.session_state.get(editor_key)
        if raw_val is None:
            return

        try:
            edited_df = pd.DataFrame(raw_val, index=grid.index, columns=grid.columns)
            mask_blocks = grid == CrosswordGenerator.EMPTY
            new_user = edited_df.copy()
            new_user[mask_blocks] = CrosswordGenerator.EMPTY
            non_blocks = ~mask_blocks
            cleaned = new_user.where(non_blocks)
            cleaned = cleaned.replace({BLOCK_TOKEN: ""}).fillna("")
            new_user[non_blocks] = cleaned[non_blocks].astype(str)

            st.session_state.user_grid = new_user
        except Exception:
            pass

    def render_crossword(
        self, grid: pd.DataFrame, show_answer: bool = False, editable: bool = False
    ) -> None:
        """Render the crossword grid with optional editing & answer reveal."""
        need_init = (
            "user_grid" not in st.session_state
            or st.session_state.user_grid is None
            or not isinstance(st.session_state.user_grid, pd.DataFrame)
            or st.session_state.user_grid.shape != grid.shape
        )
        if need_init:
            st.session_state.user_grid = pd.DataFrame(
                np.where(
                    grid.values != CrosswordGenerator.EMPTY,
                    "",
                    CrosswordGenerator.EMPTY,
                ),
                index=grid.index,
                columns=grid.columns,
            )

        n_rows = grid.shape[0]
        row_heights = (n_rows + 1) * 35

        def color_cells(val: Optional[str]) -> str:
            if val in (CrosswordGenerator.EMPTY, BLOCK_TOKEN):
                return "background-color: black; color: black"
            return "background-color: white; color: black; text-align: center"

        if editable:
            if show_answer:
                display_df = grid.replace(CrosswordGenerator.EMPTY, BLOCK_TOKEN)
                disabled = True
            else:
                display_df = st.session_state.user_grid.mask(
                    grid == CrosswordGenerator.EMPTY, BLOCK_TOKEN
                )
                disabled = False

            col_config = {
                col: st.column_config.Column(width=45) for col in display_df.columns
            }
            if disabled:
                st.data_editor(
                    display_df,
                    height=row_heights,
                    key="grid_editor",
                    disabled=disabled,
                    column_config=col_config,
                    hide_index=False,
                )
            else:
                st.data_editor(
                    display_df,
                    height=row_heights,
                    key="grid_editor",
                    disabled=disabled,
                    column_config=col_config,
                    hide_index=False,
                )
                if "grid_editor" in st.session_state:
                    self._sync_user_grid(grid, "grid_editor")

        else:
            if show_answer:
                df = grid
            else:
                df = pd.DataFrame(
                    np.where(
                        grid.values != CrosswordGenerator.EMPTY,
                        "",
                        CrosswordGenerator.EMPTY,
                    ),
                    index=grid.index,
                    columns=grid.columns,
                )

            styled = df.style.applymap(color_cells)
            st.dataframe(styled, height=row_heights)

    def render_placements(self, placements: List[Placement], show_answer: bool = False):
        """Display the crossword clues in Streamlit, split into Across and Down."""
        st.write("### 🔍 Clues")
        across = [p for p in placements if p.direction == "across"]
        down = [p for p in placements if p.direction == "down"]
        col1, col2 = st.columns(2)

        def render(title: str, items: List[Placement]):
            st.write(f"**{title}**")
            c1, c2, c3 = st.columns([2, 2, 10])
            c1.caption("Row")
            c2.caption("Col")
            c3.caption("Description")
            for p in items:
                c1, c2, c3 = st.columns([2, 2, 10])
                c1.write(p.row)
                c2.write(p.col)
                if show_answer:
                    clue_text = f"{p.clue} ({p.word})"
                else:
                    clue_text = p.clue
                c3.write(clue_text)

        with col1:
            render("Across", across)
        with col2:
            render("Down", down)
