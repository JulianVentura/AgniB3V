import re

def camelCaseToLabel(s: str):
    """
    Receives a string in the format "camelCase" 
    and returns "Camel Case"
    """
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', s).title()
