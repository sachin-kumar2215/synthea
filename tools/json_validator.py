
import json

# --- JSON VALIDATOR TOOL ---
def validate_json(json_string: str) -> dict:
    if not isinstance(json_string, str):
        return {"is_valid": False, "reason": "Input was not a string."}
    try:
        json.loads(json_string)
        return {"is_valid": True, "reason": "String is a valid JSON object."}
    except json.JSONDecodeError as e:
        return {"is_valid": False, "reason": f"Invalid JSON format: {e}"}