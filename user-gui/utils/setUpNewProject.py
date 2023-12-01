import os
import shutil

def setUpNewProject(directory: str) -> bool:
    """
    Given a directory, set up the project structure.
    """
    # Create project directory
    try:
        os.mkdir(directory)
    except:
        return False
    
    # Create project subdirectories
    subdirectories = ["data", "models", "notebooks", "reports"]
    for subdirectory in subdirectories:
        try:
            os.mkdir(os.path.join(directory, subdirectory))
        except:
            return False
    
    # Copy templates
    templatesDirectory = os.path.join(os.path.dirname(__file__), "templates")
    templates = ["README.md", "requirements.txt"]
    for template in templates:
        shutil.copyfile(os.path.join(templatesDirectory, template), os.path.join(directory, template))
    
    return True