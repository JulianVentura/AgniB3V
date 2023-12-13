import os

def getFileWithExtension(extension: str, directory: str) -> str or None:
    """
    Given an extension and a directory, it looks for a file with that extension in the
    given directory and returns its path.
    """
    files = [os.path.join(directory, f) for f in os.listdir(directory)]
    for file in files:
        if file.endswith(extension):
            return file
    return None
