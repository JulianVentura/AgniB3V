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
    
    # Copy templates
    templatesDirectory = os.path.join(os.path.dirname(__file__), "../templates")
    templates = ["gmat.script", "agni.FCStd"]
    for template in templates:
        shutil.copyfile(os.path.join(templatesDirectory, template), os.path.join(directory, template))

    # Replace paths in gmat.script
    with open(os.path.join(directory, "gmat.script"), "r") as f:
        script = f.read()
        script = script.replace(
            "Create EclipseLocator EclipseLocator;\n",
            f"Create EclipseLocator EclipseLocator;\nGMAT EclipseLocator.Filename = {directory}/EclipseLocator.txt;\n",
        )
        script = script.replace(
            "Create ReportFile ReportFile;\n",
            f"Create ReportFile ReportFile;\nGMAT ReportFile.Filename = {directory}/ReportFile.txt;\n",
        )
        
    with open(os.path.join(directory, "gmat.script"), "w") as f:
        f.write(script)
    
    return True