from os import path

workbench_path = path.dirname(path.dirname(path.realpath(__file__)))
public_path = path.dirname(path.realpath(__file__))
icons_path = path.join(public_path, 'icons')

def workbenchPath():
    """
    It returns the workbench path
    """
    return workbench_path

def iconPath(name):
    """
    It returns the icon path given the icon name
    """
    iconPath = path.join(icons_path, name)

    return iconPath

def getWorkbenchSettingsPath(documentPath):
    """
    It returns the workbench settings path given the document path
    """
    # TODO: maybe is better to return a directory instead of a file
    workbenchSettingsPath = path.join(documentPath, 'workbenchSettings.json')

    return workbenchSettingsPath
