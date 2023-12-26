from utils.toCamelCase import toCamelCase

def dictToCamelCase(data):
    """
    Receives a dictionary and returns a dictionary with the keys in camelCase
    """
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_data[toCamelCase(key)] = dictToCamelCase(value)
    elif isinstance(data, list):
        new_data = []
        for value in data:
            new_data.append(dictToCamelCase(value))
    else:
        new_data = data
    return new_data
