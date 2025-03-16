import base64
import datetime
from io import BytesIO
import json
import random
import ollama
import pandas as pd
import streamlit as st

from variables import PROMPT_DEFAULT_PATH, PROMPT_USER_PATH
from modules.utils import get_prompt, get_models, load_prompt, load_duration, total_duration

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
            keep_alive=-1,
            options={
                "temperature": st.session_state.temperature,
                "seed": st.session_state.last_seed
            }
        )
        
        response = ""
        done = {}
        for chunk in stream:
            if chunk.done:
                st.session_state.done = chunk
                done['total_duration'] = chunk.total_duration
                done['load_duration'] = chunk.load_duration
                done['prompt_eval_count'] = chunk.prompt_eval_count
                done['prompt_eval_duration'] = chunk.prompt_eval_duration
                done['eval_count'] = chunk.eval_count
                done['eval_duration'] = chunk.eval_duration

                st.session_state.response["models"][-1]["prompts"][-1]["response"] = response.strip()
                st.session_state.response["models"][-1]["prompts"][-1]["done"] = done
            else:
                response += chunk.response
            yield chunk.response

    except ollama.ResponseError as e:
        st.session_state.done = None
        st.session_state.response["models"][-1]["prompts"][-1]["error"] = str(e)
        st.error(f"Error: {e}")

def display_chart(data: dict):
    st.write("---")
    st.write("#### Stats")
    col1, col2 = st.columns(2)
    with col1:
        duration = load_duration(data=data)
        st.bar_chart(
            duration,   
            x="models",
            x_label="Model(s) Load Duration",
            y_label="Time (s)",
            horizontal=False
        )
    with col2:
        keys_, total = total_duration(data=data)
        st.bar_chart(
            total,
            x="col1",
            x_label="Prompt(s) Eval Duration",
            y=keys_,
            y_label="Time (s)",
            horizontal=False,
            stack=False,
        )
    st.write("---")

def use_last_seed() -> None:
    '''Last seed'''
    if st.session_state['last_seed']:
        st.session_state['seed'] = st.session_state['last_seed']

@st.fragment()
def display_options() -> None:
    st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.1, value=0.0, key="temperature", help="Temperature  \n0.0: less creative  \n1.0: more creative")
    col1, col2 = st.columns([4,1], vertical_alignment="bottom")
    with col1:
        st.number_input("Seed", min_value=-1, key="seed", help="Seed  \n-1: random seed")
    with col2:
        st.button(":material/sync:", key="button_last_seed", type="primary", use_container_width=True, on_click=use_last_seed, help="Use last seed")
    st.write("---")

@st.fragment()
def download_json() -> None:
    data = json.dumps(st.session_state.response)

    st.download_button(
        label=":material/save: Download JSON", 
        data=data,
        file_name=f"vision-comparator_{st.session_state.response['date'].replace(' ', '_')}.json", 
        key="download_json", 
        type="primary", 
        help="Download response as JSON"
    )

def free_memory(model: str) -> None:
    ollama.generate(model=model, keep_alive=0)

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
if 'response' not in st.session_state:
    st.session_state['response'] = {
        "models": []
    }

prompts = load_prompt(PROMPT_USER_PATH)
prompts = [prompt['name'] for prompt in prompts]
with st.sidebar:
    
    display_options()

    if "image_uploader" in st.session_state and st.session_state.image_uploader is not None:
        st.image(st.session_state.image_uploader)
        st.write("---")

st.title(":material/compare_arrows: Vision Comparator")
models = get_models()

models_selected = st.multiselect("Select model(s)", placeholder="Select model(s)", options=models, key="models_selected", label_visibility="visible", help="Select model(s) to compare")

col1, col2 = st.columns([1,1], vertical_alignment="top")

with col1:
    image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"], key="image_uploader", label_visibility="visible", help="Upload an image")
with col2:
    prompts_selected = st.multiselect("Select prompt(s)", placeholder="Select prompt(s)", options=prompts, key="prompt_selected", help="Select prompt(s) to use")
   
    disabled = True
    if len(models_selected) > 0 and image is not None and len(prompts_selected) > 0:
        disabled = False
    compare = st.button(":material/compare_arrows: Compare", disabled=disabled, key="compare", use_container_width=True, type="primary")

if compare:

    st.session_state.response = {
        "models": []
    }

    bytes_data = image.getvalue()

    st.session_state.image = bytes_data

    if st.session_state.seed == -1:
        st.session_state.last_seed = random.randint(0, 2**32 - 1)
    else:
        st.session_state.last_seed = st.session_state.seed

    placeholder_stats = st.empty()

    for model in models_selected:
        st.session_state.active_model = model
        st.write(f"### {model}")

        model_object = {
            "name": model,
            "prompts": [],
        }
        st.session_state.response["models"].append(model_object)

        for prompt_name in prompts_selected:

            st.session_state.response["models"][-1]["prompts"].append(
                {
                    "prompt": prompt_name,
                    "response": None,
                    "done": {}
                }
            )

            prompt = get_prompt(prompt_name)
            st.session_state.system = prompt['system']
            st.session_state.prompt = prompt['prompt']

            with st.expander(prompt_name):
                st.write(f"#### {prompt['name']}")
                st.write(prompt['description'])
                st.write(f"#### System Prompt")
                st.write(prompt['system'])
                st.write(f"#### Prompt")
                st.write(prompt['prompt'])

            st.write_stream(stream_data)
            st.write("<hr style='margin: 0;'>", unsafe_allow_html=True)
            if st.session_state.done is not None:
                st.write(f"<p style='color: #999; font-size: .9em; text-align: right;'>Done in {st.session_state.done['total_duration'] / 10**9:.2f}s - Tokens: {st.session_state.done['eval_count']} - Speed {st.session_state.done['eval_count'] / st.session_state.done['eval_duration'] * 10**9:.2f} tokens/s - Seed {st.session_state.last_seed} - Temperature {round(st.session_state.temperature, 2)}</p>", unsafe_allow_html=True)

    free_memory(model=st.session_state.active_model)

    st.write("<hr style='margin: 0;'>", unsafe_allow_html=True)

    st.session_state.response["date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.response["image_name"] = image.name
    st.session_state.response["image_data"] = base64.b64encode(bytes_data).decode("utf-8")

    col1, _ = st.columns([1,1], vertical_alignment="bottom")
    with col1:
        download_json()
    
    with placeholder_stats.container():
        display_chart(data=st.session_state.response)