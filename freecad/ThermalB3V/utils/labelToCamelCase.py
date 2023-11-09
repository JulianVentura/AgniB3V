def labelToCamelCase(s: str):
    """
    Receives a string in the format "label to Camel Case"
    and returns "labelToCamelCase"
    """
    sSplitBySpace = s.split(" ")
    sSplitCapitalized = [substring.capitalize() for substring in sSplitBySpace]
    sNotSpace = "".join(sSplitCapitalized).replace(" ", "")
    return sNotSpace[0].lower() + sNotSpace[1:]
