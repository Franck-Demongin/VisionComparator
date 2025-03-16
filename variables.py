import os

VERSION = "0.2.0"

MODELS_AVAILABLE_PATH = os.path.join(os.path.dirname(__file__), "models.txt")
PROMPT_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "prompts_default.json")
PROMPT_USER_PATH = os.path.join(os.path.dirname(__file__), "prompts_user.json")