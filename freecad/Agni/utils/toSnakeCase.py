import re

def toSnakeCase(s):
    """
    Receives a string in the format "camelCase"
    and returns "camel_case"
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
