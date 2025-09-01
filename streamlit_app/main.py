import streamlit as st

from streamlit_app.display import AppDisplay

st.set_page_config(page_title="Across the Board", page_icon="🧩", layout="wide")

st.title("🧩 Across the Board")
st.write("Learn with a custom crossword puzzle!")

app_display = AppDisplay()
app_display.draw()
