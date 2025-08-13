import streamlit as st

# Global page config for the app
st.set_page_config(
    page_title="2025 U.S. Amateur Championship Dashboard",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add Open Graph meta tags for URL previews in iMessage and social media
st.markdown("""
<head>
    <meta property="og:title" content="2025 U.S. Amateur Championship Dashboard" />
    <meta property="og:description" content="Live insights and analytics for the 2025 U.S. Amateur Golf Championship. Track stroke play rounds, match play brackets, and player performance." />
    <meta property="og:image" content="https://2025-us-amatuer-insights.streamlit.app/~/+/media/assets/olympic-club-logo.png" />
    <meta property="og:url" content="https://2025-us-amatuer-insights.streamlit.app/" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="U.S. Amateur Championship Dashboard" />
    
    <!-- Twitter Card meta tags -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="2025 U.S. Amateur Championship Dashboard" />
    <meta name="twitter:description" content="Live insights and analytics for the 2025 U.S. Amateur Golf Championship. Track stroke play rounds, match play brackets, and player performance." />
    <meta name="twitter:image" content="https://2025-us-amatuer-insights.streamlit.app/~/+/media/assets/olympic-club-logo.png" />
    
    <!-- Additional meta tags for better SEO -->
    <meta name="description" content="Live insights and analytics for the 2025 U.S. Amateur Golf Championship. Track stroke play rounds, match play brackets, and player performance." />
    <meta name="keywords" content="U.S. Amateur, Golf Championship, 2025, Analytics, Dashboard, Olympic Club" />
</head>
""", unsafe_allow_html=True)

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


