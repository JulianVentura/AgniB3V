import re

def toCamelCase(s):
    """
    Receives a string in the format "camel_case"
    and returns "camelCase"
    """
    return re.sub('_(.)', lambda x: x.group(1).upper(), s)
