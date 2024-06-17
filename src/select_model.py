from os import environ
from litellm import validate_environment
import warnings

def select_model(incognito=True):
    model = "groq/llama3-70b-8192" if environ.get("GROQ_API_KEY") and incognito is False else environ.get("MODEL", "ollama/llama3")
    litellm_validation = validate_environment(model)
    if litellm_validation.get('keys_in_environment') is False:
        raise EnvironmentError({
            "errno": 1, 
            "strerr": f"missing environment variables for model {model}", 
            "missing_keys": ','.join(litellm_validation.get("missing_keys"))
        })
    if "ollama" not in model:
        warnings.warn(f"sending the contents of your files to {model}!")
    return model