import re


def get_str_from_food_dict(food_dict: dict):
    result = ", ".join([f"{int(value)} {key}" for key,
                       value in food_dict.items()])
    return result


def extract_session_id(session_str: str):
    """
    Extracts the session ID from a given session string.

    Args:
        session_str (str): The session string from which the session ID is to be extracted.

    Returns:
        str: The extracted session ID. If no session ID is found, an empty string is returned.
    """
    match = re.search(r"/sessions/(.*?)/contexts/", session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string

    return ""
