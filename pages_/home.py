import ollama
import streamlit as st

from variables import PROMPT_DEFAULT_PATH, PROMPT_USER_PATH
from modules.utils import get_prompt, get_models, load_prompt, init_prompts

def generate(model: str, image: bytes, system: str, prompt: str) -> dict:
    response = ollama.generate(
        model=model,
        system=system,
        prompt=prompt,
        images=[image],
        stream=False,
        keep_alive=0,
        format=''
    )
    return response['response']

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
            format=''
        )

        # Iterate over each chunk of data
        for chunk in stream:
            if chunk.done:
                st.session_state.done = chunk
            yield chunk.response

    except Exception as e:
        print(e)

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

# init_prompts(PROMPT_USER_PATH, PROMPT_DEFAULT_PATH)
prompts = load_prompt(PROMPT_USER_PATH)
prompts = [prompt['name'] for prompt in prompts]
with st.sidebar:
    # if image_uploader := st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="image_uploader"):
    #     st.image(image_uploader)

    if "image_uploader" in st.session_state and st.session_state.image_uploader is not None:
        st.image(st.session_state.image_uploader)

st.title(":material/compare_arrows: Vision Comparator")
models = get_models()

models_selected = st.multiselect("Select a model", placeholder="Select a model", options=models, key="models_selected", label_visibility="collapsed")

image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="image_uploader", label_visibility="collapsed")
# st.image(image_uploader)

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

    for model in models_selected:
        st.session_state.active_model = model
        st.write(f"### {model}")
        st.write_stream(stream_data)
        st.write("<hr style='margin: 0;'>", unsafe_allow_html=True)
        if st.session_state.done is not None:
            st.write(f"<p style='color: #999; font-size: .9em; text-align: right;'>Done in {st.session_state.done['total_duration'] / 10**9:.2f}s - Tokens: {st.session_state.done['eval_count']} - Speed {st.session_state.done['eval_count'] / st.session_state.done['eval_duration'] * 10**9:.2f} tokens/s</p>", unsafe_allow_html=True)

