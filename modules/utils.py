import os
from variables import MODELS_AVAILABLE_PATH, PROMPT_USER_PATH
from streamlit import cache_data
# import streamlit as st
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
def get_models():
    return [model['model'] for model in ollama.list()['models']
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