import streamlit as st

from app.display import display_crossword, display_placements
from src.crossword.clue_generator import ClueGenerator
from src.crossword.crossword_generator import CrosswordGenerator

st.set_page_config(page_title="Across the Board", page_icon="🧩", layout="centered")

st.title("🧩 Across the Board")
st.write("Learn with a custom crossword puzzle!")


if "topics" not in st.session_state:
    st.session_state.topics = ""
if "difficulty_level" not in st.session_state:
    st.session_state.difficulty_level = "Easy"
if "grid" not in st.session_state:
    st.session_state.grid = None
if "placements" not in st.session_state:
    st.session_state.placements = None
if "show_answers" not in st.session_state:
    st.session_state.show_answers = False


with st.form("crossword_form", clear_on_submit=False):
    topics = st.text_input(
        "Enter any topics you want to learn about (comma-separated)",
        value=st.session_state.topics,
        placeholder="e.g. Classical Music, Theoretical Physics, Famous Chefs",
        help="What do you want your crossword to be about? Comma-separated topics are best.",
    )
    difficulty_level = st.selectbox(
        "Select difficulty level",
        options=["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty_level),
        help="How difficult do you want your crossword to be?",
    )
    submitted = st.form_submit_button("Generate Crossword")

if submitted:
    st.session_state.topics = topics
    st.session_state.difficulty_level = difficulty_level
    with st.spinner("Setting up your crossword..."):
        clue_generator = ClueGenerator()
        clue_response = clue_generator.generate_clues(
            topic_str=st.session_state.topics,
            difficulty=st.session_state.difficulty_level,
        )
        if clue_response:
            crossword_generator = CrosswordGenerator(clues=clue_response.clues)
            grid, placements = crossword_generator.generate()
            st.session_state.grid = grid
            st.session_state.placements = placements
        else:
            st.session_state.grid = None
            st.session_state.placements = None


if st.session_state.grid is not None and st.session_state.placements is not None:
    st.success("Generated crossword successfully")
    display_crossword(st.session_state.grid, show_answer=st.session_state.show_answers)
    display_placements(
        st.session_state.placements, show_answer=st.session_state.show_answers
    )
    if st.session_state.show_answers:
        if st.button("Hide Answers"):
            st.session_state.show_answers = False
            st.rerun()
    else:
        if st.button("Show Answers"):
            st.session_state.show_answers = True
            st.rerun()

elif submitted:
    st.error("Could not generate crossword; please try again")
