import base64
import datetime
from io import BytesIO
import json
import pandas as pd
import streamlit as st

from modules.utils import load_duration, total_duration

def display_chart(data: dict):
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

if "data" not in st.session_state:
    st.session_state.data = None

with st.sidebar:
    if archive:= st.file_uploader("Upload a JSON file", type=["json"]):
        st.session_state.data = json.loads(archive.read())
        image = st.session_state.data.get('image_data') 
        st.image(BytesIO(base64.b64decode(image)))
    else:
        st.session_state.data = None

    st.write("---")

st.write("## :material/visibility: Viewer")

if st.session_state.data is None:
    st.write("Please upload a JSON file")
else:
    json_name = archive.name
    date = datetime.datetime.fromisoformat(st.session_state.data['date']).strftime('%Y-%m-%d %H:%M:%S')
    image_name = st.session_state.data['image_name']
    st.write("---")
    st.write(f"JSON Name: _{json_name}_  \nDate: _{date}_  \nImage Name: _{image_name}_")
    st.write("---")

    display_chart(data=st.session_state.data)

    for model in st.session_state.data['models']:
        with st .expander(model['name']):
            st.write(f"### Model: {model['name']}")
            for prompt in model['prompts']:
                st.write(f"#### Prompt: {prompt['prompt']}")
                st.write(prompt['response'])

                done = [
                    prompt['done']['total_duration'] / 10**9,
                    prompt['done']['load_duration'] / 10**9,
                    prompt['done']['prompt_eval_count'],
                    prompt['done']['prompt_eval_duration'] / 10**9,
                    prompt['done']['eval_count'],
                    prompt['done']['eval_duration'] / 10**9
                ]

                df = pd.DataFrame([done], columns= ["total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration", "eval_count", "eval_duration"])
                st.dataframe(
                df, 
                column_config={
                    "total_duration": st.column_config.NumberColumn(
                        "Total Duration",
                        format="%.2f s"
                    ),
                    "load_duration": st.column_config.NumberColumn(
                        "Load Duration",
                        format="%.2f s"
                    ),
                    "prompt_eval_count": st.column_config.NumberColumn(
                        "Prompt Eval Count"
                    ),
                    "prompt_eval_duration": st.column_config.NumberColumn(
                        "Prompt Eval Duration",
                        format="%.2f s"
                    ),
                    "eval_count": st.column_config.NumberColumn(
                        "Eval Count"
                    ),
                    "eval_duration": st.column_config.NumberColumn(
                        "Eval Duration",
                        format="%.2f s"
                    )
                }, 
                hide_index=True
            )
