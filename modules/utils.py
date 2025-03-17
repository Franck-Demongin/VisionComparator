import os

import pandas as pd
from variables import MODELS_AVAILABLE_PATH, PROMPT_USER_PATH
from streamlit import cache_data
import ollama
import json

@cache_data
def get_available_models(models_list: str) -> list:
    try:
        with open(models_list, "r") as f:
            models = f.readlines()
            models = [model.strip() for model in models if not model.startswith("#")]

        return models
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {models_list}")

@cache_data
def get_models() -> list:
    return [model['model'] for model in ollama.list()['models']
            if model['model'].split(':')[0] in get_available_models(MODELS_AVAILABLE_PATH)]

@cache_data
def get_sizes() -> list:
    return [model['size'] for model in ollama.list()['models']
            if model['model'].split(':')[0] in get_available_models(MODELS_AVAILABLE_PATH)]

@cache_data
def get_modified_at() -> list:
    return [model['modified_at'] for model in ollama.list()['models']
            if model['model'].split(':')[0] in get_available_models(MODELS_AVAILABLE_PATH)]

@cache_data
def load_prompt(prompt_path: str) -> list:
    try:
        with open(prompt_path, "r") as f:
            prompts = json.load(f)
        return prompts
    except FileNotFoundError:
        print(f"Prompt file not found: {prompt_path}")
        return []

def init_prompts(prompt_path: str, default_path: str) -> None:
    if not os.path.exists(prompt_path):
        with open(prompt_path, "w") as f:
            f.write(json.dumps(load_prompt(default_path)))
    
def get_prompt(prompt_name: str) -> str:
    prompts = load_prompt(PROMPT_USER_PATH)
    for prompt in prompts:
        if prompt['name'] == prompt_name:
            return prompt
    return {}

def load_duration(data: dict) -> pd.DataFrame:
    data_duration = pd.DataFrame(
        {
            "models": [model['name'] for model in data['models']],
            "duration": [model['prompts'][0]['done']['load_duration'] if 'error' not in model['prompts'][0] or model['prompts'][0]['error'] is None else 0 / 10**9 for model in data['models'] ]
        }
    )
    return data_duration

def total_duration(data: dict) -> tuple[list[str], pd.DataFrame]:
    data_models = {}
    for model in data['models']:
        data_models[model['name']] = []
        for prompt in model['prompts']:
            data_models[model['name']].append(prompt['done']['eval_duration'] / 10**9 if 'error' not in model['prompts'][0] or model['prompts'][0]['error'] is None else 0)

    data_duration = pd.DataFrame(
        {
            "col1": [prompt['prompt'] for prompt in data['models'][0]['prompts']]
        }
    
    )
    data_duration = data_duration.join(pd.DataFrame(data_models))



    if len(data_models) == 1: 
        key = list(data_models.keys())[0]
        new_key = key.replace(':', '-')
        new_key = new_key.replace('.', '-')
        print(key, new_key)
        # new_key = "Test"
        keys = [new_key]
        data_duration[new_key] = data_duration[key]
        data_duration.pop(key)
    else:
        keys = list(data_models.keys())

    return keys, data_duration