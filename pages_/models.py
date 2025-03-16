import datetime
import time
import ollama
import streamlit as st

from modules.utils import get_available_models, get_models, get_sizes, get_modified_at
from variables import MODELS_AVAILABLE_PATH, PROMPT_DEFAULT_PATH, PROMPT_USER_PATH

css = """
<style>
    .st-key-edit_models {
        text-align: right;
    }  

</style>
"""
st.html(css)

st.write("## Models")

def read_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()
    
def save_models(file_path: str) -> None:
    with open(file_path, "w") as f:
        f.write(st.session_state.list_models.strip())
    st.cache_data.clear()
    st.session_state.edit_models = False


def delete_model(model_name: str) -> None:
    ollama.delete(model=model_name)
    st.cache_data.clear()

def reload_model(model_name: str, placeholder) -> None:
    st.session_state.pull_model_name = model_name
    pull_model(reload=False, placeholder=placeholder)

def pull_model(placeholder, reload: bool = True) -> None:
    try:
        stream = ollama.pull(model=st.session_state.pull_model_name, stream=True)
        sections = []
        progress = {}

        with placeholder.container():
            for chunk in stream:
                print(chunk)
                if chunk.status not in sections:
                    sections.append(chunk.status)
                        
                    col1, col2 = st.columns([1, 5], vertical_alignment="bottom")
                    if chunk.status != "success":
                        with col1:
                            st.write(chunk['status'])
                    else:
                        st.success(f"Model {st.session_state.pull_model_name} successfully pulled")

                if 'completed' in chunk:
                    if chunk.status not in progress:
                        with col2:
                            progress[chunk.status] = st.progress(chunk['completed']*100//chunk['total'], text=f"{chunk['completed']/1e9:.3f} / {chunk['total']/1e9:.2f} GB")
                    else:
                        progress[chunk.status].progress(chunk['completed']*100//chunk['total'], text=f"{chunk['completed']/1e9:.3f} / {chunk['total']/1e9:.2f} GB")
            


        st.cache_data.clear()
        st.session_state.clear()
        st.toast("Model successfully pulled")
        if reload:
            time.sleep(2)
            st.rerun()
        else:
            st.session_state.pull_model_name = ""

    except ollama.ResponseError as e:
        placeholder.error(e)
        time.sleep(2)
        placeholder.empty()

col1, col2 = st.columns([7, 1], vertical_alignment="center")
with col1:
    st.write("### List of models with vision support")
with col2:
    edit = st.toggle("Edit", key="edit_models")

if edit:
    with st.form("edit_models", border=False):
        list_models = st.text_area("Models", value=read_file(MODELS_AVAILABLE_PATH), height=200, key="list_models")
        st.form_submit_button("Save", on_click=save_models, args=(MODELS_AVAILABLE_PATH,), type="primary")
else:
    content = get_available_models(MODELS_AVAILABLE_PATH)
    st.write(", ".join(content), unsafe_allow_html=True)

st.write("### Models available")
models = get_models()
sizes = get_sizes()
modified_at = get_modified_at()

col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
with col1:
    pull1 = st.text_input("Pull model", key="pull_model_name", placeholder="Enter model name")
with col2:
    disabled = pull1 == ""
    pull2 = st.button("Pull model", key="pull_model_button", disabled=disabled, type="primary", use_container_width=True)

placeholder = st.empty()

col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 1, 1], vertical_alignment="center")
with col1:
    st.write("**Model name**")
with col2:
    st.write("**Size**")
with col3:
    st.write("**Modified**")
with col4:
    st.write("**Reload**")
with col5:
    st.write("**Delete**")

st.write("<hr style='margin: 0; border-width: 1px; border-bottom-color: #1c83e1;'>", unsafe_allow_html=True)


for size, model, modified in zip(sizes, models, modified_at):
    col1, col2, col3, col4, col5 = st.columns([4, 2, 2, 1, 1], vertical_alignment="center")
    with col1:
        st.write(model)
    with col2:
        st.write(f"{size / 1e9:.2f} GB")
    with col3:
        st.write(modified.strftime("%Y-%m-%d %H:%M:%S"))
    with col4:
        st.button(":material/sync:", key=f"reload_{model}", on_click=reload_model, args=(model, placeholder), type="tertiary", use_container_width=True)
    with col5:
        st.button(":red[:material/delete:]", key=f"del_{model}", on_click=delete_model, args=(model,), type="tertiary", use_container_width=True)
    st.write("<hr style='margin: 0;'>", unsafe_allow_html=True)

if pull2:
    pull_model(placeholder)
