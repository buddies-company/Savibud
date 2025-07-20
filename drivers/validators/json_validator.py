import json


def check_valid_dict_str(value: str):
    """Check that string value is in json format"""
    try:
        json.loads(value)
    except ValueError as exc:
        raise ValueError("Invalid json format") from exc
    return value
