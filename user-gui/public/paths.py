from os import path

public_path = path.dirname(path.realpath(__file__))
icons_path = path.join(public_path, 'icons')

def iconPath(name):
    """
    It returns the icon path given the icon name
    """
    iconPath = path.join(icons_path, name)

    return iconPath
