import random
import ollama
import streamlit as st

from variables import PROMPT_DEFAULT_PATH, PROMPT_USER_PATH
from modules.utils import get_prompt, get_models, load_prompt, init_prompts

def stream_data():
    """
    Stream data from ollama.

    Yields:
        str: The content of each chunk of data.
    """
    try:
        prompt = st.session_state.prompt
        if st.session_state.prompt is None or st.session_state.prompt == "":
            prompt = ' '
        
        stream = ollama.generate(
            model=st.session_state.active_model,
            system=st.session_state.system,
            prompt=prompt,
            images=[st.session_state.image],
            stream=True,
            format='',
            keep_alive=0,
            options={
                "temperature": st.session_state.temperature,
                "seed": st.session_state.last_seed
            }
        )
        # Iterate over each chunk of data
        for chunk in stream:
            if chunk.done:
                st.session_state.done = chunk
            yield chunk.response

    except ollama.ResponseError as e:
        st.error(f"Error: {e}")

def use_last_seed() -> None:
    '''Last seed'''
    if st.session_state['last_seed']:
        st.session_state['seed'] = st.session_state['last_seed']

@st.fragment()
def display_options() -> None:
    col1, col2, col3 = st.columns([3,3,1], vertical_alignment="bottom")
    with col1:
        st.number_input("Temperature", min_value=0.0, max_value=1.0, step=0.1, value=0.0, key="temperature", help="Temperature  \n0.0: less creative  \n1.0: more creative")
    with col2:
        st.number_input("Seed", min_value=-1, key="seed", help="Seed  \n-1: random seed")
    with col3:
        st.button(":material/sync:", key="button_last_seed", type="primary", use_container_width=True, on_click=use_last_seed, help="Use last seed")

if 'done' not in st.session_state:
    st.session_state['done'] = None    
if 'active_model' not in st.session_state:
    st.session_state['active_model'] = None
if 'prompt' not in st.session_state:
    st.session_state['prompt'] = None
if 'system' not in st.session_state:
    st.session_state['system'] = None
if 'image' not in st.session_state:
    st.session_state['image'] = None
if 'seed' not in st.session_state:
    st.session_state['seed'] = 42
if 'last_seed' not in st.session_state:
    st.session_state['last_seed'] = st.session_state.seed

prompts = load_prompt(PROMPT_USER_PATH)
prompts = [prompt['name'] for prompt in prompts]
with st.sidebar:
    
    display_options()

    if "image_uploader" in st.session_state and st.session_state.image_uploader is not None:
        st.image(st.session_state.image_uploader)

st.title(":material/compare_arrows: Vision Comparator")
models = get_models()

models_selected = st.multiselect("Select a model", placeholder="Select a model", options=models, key="models_selected", label_visibility="collapsed")

image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="image_uploader", label_visibility="collapsed")

col1, col2 = st.columns([5,1], vertical_alignment="bottom")
with col1:
    prompt_name = st.selectbox("Select a prompt", prompts, key="prompt_selected")
    prompt_selected = get_prompt(prompt_name)
    system = None
    prompt = None
    if prompt_name is not None and prompt_name != "None":
        system = prompt_selected['system']
        prompt = prompt_selected['prompt']
with col2:
    disabled = True
    if len(models_selected) > 0 and image is not None:
        disabled = False
    compare = st.button("Compare", disabled=disabled, key="compare", use_container_width=True, type="primary")

if compare:
    bytes_data = image.getvalue()

    st.session_state.prompt = prompt
    st.session_state.system = system
    st.session_state.image = bytes_data

    if st.session_state.seed == -1:
        st.session_state.last_seed = random.randint(0, 2**32 - 1)
    else:
        st.session_state.last_seed = st.session_state.seed

    for model in models_selected:
        st.session_state.active_model = model
        st.write(f"### {model}")
        st.write_stream(stream_data)
        st.write("<hr style='margin: 0;'>", unsafe_allow_html=True)
        if st.session_state.done is not None:
            st.write(f"<p style='color: #999; font-size: .9em; text-align: right;'>Done in {st.session_state.done['total_duration'] / 10**9:.2f}s - Tokens: {st.session_state.done['eval_count']} - Speed {st.session_state.done['eval_count'] / st.session_state.done['eval_duration'] * 10**9:.2f} tokens/s - Seed {st.session_state.last_seed} - Temperature {round(st.session_state.temperature, 2)}</p>", unsafe_allow_html=True)
