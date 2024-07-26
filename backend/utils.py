import re


def get_str_from_food_dict(food_dict: dict):
    """
    Generates a string representation of a food dictionary.

    Args:
        food_dict (dict): A dictionary containing food items as keys and their quantities as values.

    Returns:
        str: A string containing the quantities and names of the food items in the dictionary, separated by commas.

    Example:
        >>> food_dict = {"apple": 2, "banana": 1, "orange": 3}
        >>> get_str_from_food_dict(food_dict)
        '2 apple, 1 banana, 3 orange'
    """
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
