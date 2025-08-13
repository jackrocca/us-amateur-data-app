import streamlit as st

# Global page config for the app
st.set_page_config(
    page_title="2025 U.S. Amateur Championship Dashboard",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Programmatic multi-page navigation
stroke_play = st.Page("pages/stroke_play.py", title="Stroke Play", icon="⛳")
round64 = st.Page("pages/round_of_64.py", title="Round of 64", icon=":material/flag:")
round32 = st.Page("pages/round_of_32.py", title="Round of 32", icon=":material/flag:")
round16 = st.Page("pages/round_of_16.py", title="Round of 16", icon=":material/flag:")
quarterfinals = st.Page("pages/quarterfinals.py", title="Quarterfinals", icon=":material/flag:")
semifinals = st.Page("pages/semifinals.py", title="Semifinals", icon=":material/flag:")
finals = st.Page("pages/finals.py", title="Finals", icon=":material/flag:")

navigation = st.navigation([
    stroke_play,
    round64,
    round32,
    round16,
    quarterfinals,
    semifinals,
    finals,
])

navigation.run()


