from os import path

public_path = path.dirname(path.realpath(__file__))
icons_path = path.join(public_path, 'icons')

def iconPath(name):
    f = path.join(icons_path, name)

    return f
