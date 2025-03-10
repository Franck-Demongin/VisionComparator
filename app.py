import streamlit as st

from modules.utils import init_prompts
from variables import PROMPT_DEFAULT_PATH, PROMPT_USER_PATH, VERSION


st.set_page_config(
    page_title="Vision Comparator",
    page_icon=":eyes:",
    layout="wide"
)

init_prompts(PROMPT_USER_PATH, PROMPT_DEFAULT_PATH)

#########
# STYLE #
#########
css = """
<style>
    button[title="View fullscreen"] {
        top: 0.5rem !important;
        right: 0.5rem !important;
    }  

</style>
"""
st.html(css)

pg = st.navigation(
    [
        st.Page("pages_/home.py", title="Comparator", icon=":material/compare_arrows:"),
        st.Page("pages_/models.py", title="Models", icon=":material/settings:"),
        st.Page("pages_/prompts.py", title="Prompts", icon=":material/settings:")
    ]
)
pg.run()

with st.sidebar:
    st.write(f"Version: {VERSION}")