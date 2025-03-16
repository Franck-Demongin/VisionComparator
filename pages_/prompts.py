import json
import time
import streamlit as st

from modules.utils import get_available_models, get_models, load_prompt
from variables import MODELS_AVAILABLE_PATH, PROMPT_DEFAULT_PATH, PROMPT_USER_PATH

css = """
<style>
    .st-key-edit_models {
        text-align: right;
    }  

</style>
"""
st.html(css)

st.write("## :material/article: Prompts")

def reset_prompts(prompt_path: str, default_path: str) -> None:
    with open(prompt_path, "w") as f:
        f.write(json.dumps(load_prompt(default_path)))
    
    st.cache_data.clear()
    st.session_state.tab = "Prompts"

def add_prompt() -> None:
    if len(st.session_state.prompt_name.strip()) == 0:
        st.toast(f":red[_**Name**_ cannot be empty]", icon=":material/warning:")
        return
    prompts = load_prompt(PROMPT_USER_PATH)
    prompts = [prompt for prompt in prompts if prompt['name'] != st.session_state.prompt_name]
    prompts.append({
        "name": st.session_state.prompt_name,
        "description": st.session_state.prompt_description,
        "system": st.session_state.prompt_system,
        "prompt": st.session_state.prompt_prompt
    })
    with open(PROMPT_USER_PATH, "w") as f:
        f.write(json.dumps(prompts))

    st.cache_data.clear()

def edit_prompt(index: int, prompt_name: str, prompt_description: str, prompt_system: str, prompt_prompt: str) -> None:
    if len(prompt_name.strip()) == 0:
        st.toast(f"_**Name**_ cannot be empty", icon=":material/warning:")
        return
    prompts = load_prompt(PROMPT_USER_PATH)
    if prompt_name in [prompt['name'] for prompt in prompts if prompt_name.lower() != prompts[index]['name'].lower()]:
        st.toast(f"Prompt with name {prompt_name} already exists", icon=":material/warning:")
        return
    prompts[index] = {
        "name": prompt_name,
        "description": prompt_description,
        "system": prompt_system,
        "prompt": prompt_prompt
    }

    with open(PROMPT_USER_PATH, "w") as f:
        f.write(json.dumps(prompts))

    st.cache_data.clear()
    st.toast("Prompt saved", icon=":material/check:")

def delete_prompt(prompt_name: str) -> None:
    print(prompt_name)
    prompts = load_prompt(PROMPT_USER_PATH)
    prompts = [prompt for prompt in prompts if prompt['name'] != prompt_name]
    with open(PROMPT_USER_PATH, "w") as f:
        f.write(json.dumps(prompts))

    st.cache_data.clear()


_, col2, col3 = st.columns([15, 1, 1], vertical_alignment="center")
# with col1:
#     st.write("### Prompts")
with col2:
    st.button(
        ":material/sync:", 
        key="reset_prompt", 
        on_click=reset_prompts, 
        args=(PROMPT_USER_PATH, PROMPT_DEFAULT_PATH), 
        type="secondary", 
        use_container_width=True,
        help="Reset prompts to default.  \n:red[:material/warning: _this will delete all your custom prompts_]"
    )    
with col3:
    prompt_add = st.button(
        ":material/add:", 
        key="add_prompt", 
        type="secondary", 
        use_container_width=True,
        help="Add a new prompt"
    )
prompts = load_prompt(PROMPT_USER_PATH)

placeholder = st.empty()

if prompt_add:
    with placeholder:
        with st.container(border=True):
            col1, col2 = st.columns([15, 1], vertical_alignment="center")
            with col1:
                st.write("#### Add prompt")
            with col2:
                close_add_prompt = st.button(":material/close:", key="close_add_prompt", type="tertiary", use_container_width=True)
            
            if close_add_prompt:
                placeholder.empty()

            with st.form("add_prompt", border=False):
                prompt_name = st.text_input("Name", key="prompt_name")
                prompt_description = st.text_area("Description", key="prompt_description")
                prompt_system = st.text_area("System", key="prompt_system")
                prompt_prompt = st.text_area("Prompt", key="prompt_prompt")

                save = st.form_submit_button("Save", on_click=add_prompt, type="primary", use_container_width=False)

                if save:
                    print("save")
                    time.sleep(2)
                    st.rerun()


for prompt in prompts:
    if f"edit_{prompt['name']}" not in st.session_state:
        st.session_state[f"edit_{prompt['name']}"] = False

for index, prompt in enumerate(prompts):
    with st.expander(label=f"_**{prompt['name']}**_"):
        col1, col2, col3 = st.columns([20, 1, 1], vertical_alignment="center")
        with col1:
            st.write(f"### {prompt['name']}")
        with col2:
            if st.session_state[f"edit_{prompt['name']}"]:
                label = ":material/close:"
                key = f"edit_{index}"
                help = "Exit"
            else:
                label = ":material/edit:"
                key = f"edit_{index}"
                help = "Edit prompt"
            
            if action:= st.button(label, key=key, type="tertiary", use_container_width=True, help=help):
                st.session_state[f"edit_{prompt['name']}"] =  not st.session_state[f"edit_{prompt['name']}"]
                st.rerun()

        with col3:
            prompt_delete = st.button(":red[:material/delete:]", key=f"del_{prompt['name']}", on_click=delete_prompt, args=(prompt['name'],), type="tertiary", use_container_width=True, help="Delete prompt")
        
        if prompt_delete:
            st.rerun()
        
        if st.session_state[f"edit_{prompt['name']}"]:
            with st.form(f"form_{prompt['name']}", border=False):
                prompt_name = prompt['name'] = st.text_input("Name", value=prompt['name'], key=f"edit_{prompt['name']}_name")
                prompt_description = prompt['description'] = st.text_area("Description", value=prompt['description'], key=f"edit_{prompt['name']}_description")
                prompt_system = prompt['system'] = st.text_area("System", value=prompt['system'], key=f"edit_{prompt['name']}_system")
                prompt_prompt = prompt['prompt'] = st.text_area("Prompt", value=prompt['prompt'], key=f"edit_{prompt['name']}_prompt")
                
                saved = st.form_submit_button("Save", type="primary")
                
                if saved:
                    edit_prompt(index, prompt_name, prompt_description, prompt_system, prompt_prompt)
                    time.sleep(2)
                    st.session_state[f"edit_{prompt['name']}"] = False
                    st.rerun()

        else:
            st.write(prompt['description'])
            st.write("<h3 style='margin: 0 0 20px 0; border-bottom: 1px solid rgba(128, 128, 128, 0.3);'>System Prompt</h3>", unsafe_allow_html=True)
            st.write(prompt['system'])
            st.write("<h3 style='margin: 0 0 20px 0; border-bottom: 1px solid rgba(128, 128, 128, 0.3);'>Prompt</h3>", unsafe_allow_html=True)
            st.write(prompt['prompt'])