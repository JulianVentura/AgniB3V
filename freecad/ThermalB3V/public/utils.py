from os import path

workbench_path = path.dirname(path.dirname(path.realpath(__file__)))
public_path = path.dirname(path.realpath(__file__))
icons_path = path.join(public_path, 'icons')

def workbenchPath():
    return workbench_path

def iconPath(name):
    f = path.join(icons_path, name)

    return f
