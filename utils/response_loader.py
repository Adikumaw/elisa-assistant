import yaml
import random

# Load YAML responses once
with open("data/responses.yml", encoding='utf-8') as file:
    RESPONSES_YML = yaml.safe_load(file)

def get_random_response(action: str, response_type: str, **kwargs) -> dict:
    section = RESPONSES_YML.get(action, {}).get(response_type, {})
    responses = section.get("responses", [])
    continue_chat = section.get("continue", False)

    if not responses:
        return {"text": "Oops! Something went wrong.", "continue": False}

    response = random.choice(responses)
    return {
        "text": response.format(**kwargs),
        "continue": continue_chat
    }