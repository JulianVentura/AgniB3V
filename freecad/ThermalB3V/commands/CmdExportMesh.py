import FreeCAD
import os
import json
import re
from public.utils import iconPath
from utils.CustomJsonEncoder import CustomJsonEncoder
from ui.DialogExport import DialogExport

class CmdExportMesh:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        form = DialogExport(self.workbench, self.onExport)
        form.exec_()

    def IsActive(self):
        return bool(FreeCAD.activeDocument())

    def GetResources(self):
        return {
            'MenuText': ("Export mesh"),
            'ToolTip': ("Export mesh"),
            'Pixmap': iconPath("Export.svg"),
        }
    
    # TODO: ¿move to dialog?
    def onExport(self):
        FreeCAD.Console.PrintMessage("Getting document\n")
        document = FreeCAD.activeDocument()

        FreeCAD.Console.PrintMessage("Getting analysis object\n")
        analysisObject = self.getAnalysisObject(document)
        if analysisObject is None:
            FreeCAD.Console.PrintError("No Analysis object found\n")
            return
        
        FreeCAD.Console.PrintMessage("Getting mesh object\n")
        femMeshObject = self.getMeshObject(analysisObject)
        if femMeshObject is None:
            FreeCAD.Console.PrintError("No FEMMesh object found\n")
            return
        
        FreeCAD.Console.PrintMessage("Getting material objects\n")
        materialObjects = self.getMaterialObjects(analysisObject)
        if len(materialObjects) == 0:
            FreeCAD.Console.PrintError("No Materials found\n")
            return
        
        # TODO: check if there is parts of the object with different materials
        # this can be done by checking if there are solid repeated or faces
        # repeated (for the faces we should check if there are solid and faces combined
        # and check the faces in the solid)
        # This is wrong, but user can set two materials to the same solid/face

        elements = {}
        properties = {}

        FreeCAD.Console.PrintMessage("Getting elements with material\n")
        for materialObject in materialObjects:
            elementsWithMaterial = self.getElementsWithMaterial(materialObject)
            if len(elementsWithMaterial) == 0:
                FreeCAD.Console.PrintError(f"No elements found with material {materialObject.Label}\n")
                return
 
            trianglesWithMaterial = self.getTrianglesFromElements(elementsWithMaterial, femMeshObject)
            if len(trianglesWithMaterial) == 0:
                FreeCAD.Console.PrintError(f"No triangles found with material {materialObject.Label}\n")
                return
            
            # TODO: is better key to be the name, label, id or something else?
            elements[materialObject.Name] = trianglesWithMaterial
            properties[materialObject.Name] = self.getProperties(materialObject.Material)
            if not properties[materialObject.Name]:
                FreeCAD.Console.PrintError(f"Some of the material properties are missing in {materialObject.Label}\n")
                FreeCAD.Console.PrintError("The expected properties are: ThermalConductivity, SpecificHeat, Density, InitialTemperature\n")
                return

        # Writing path
        path = self.workbench.getExportPath()
        
        # Open file and write
        FreeCAD.Console.PrintMessage(f"Starting exporting to {path}\n")
        self.writeMaterialAsJson(properties, elements, path)
        self.writeFemMeshAsVtk(femMeshObject, path)
    
    def getAnalysisObject(self, document):
        """Returns the Analysis object or None if it does not exist"""
        objects = document.Objects
        for object in objects:
            if object.TypeId == "Fem::FemAnalysis":
                return object
        return None
    
    def getMeshObject(self, analysisObject):
        """Returns the mesh object or None if it does not exist"""
        objects = analysisObject.Group
        for object in objects:
            if object.TypeId == "Fem::FemMeshObjectPython":
                return object
        return None
    
    def getMaterialObjects(self, analysisObject):
        """Returns a list of material objects"""
        objects = analysisObject.Group
        materialObjects = []
        for object in objects:
            if object.TypeId == "App::MaterialObjectPython":
                materialObjects.append(object)
        return materialObjects
    
    def getProperties(self, material):
        """Returns a dictionary of the neccessary properties of the material"""
        # TODO: move to constants file
        MATERIAL_PROPERTIES = [
            "ThermalConductivity",
            "SpecificHeat",
            "Density",
            "InitialTemperature" # TODO: move initial temperature to another place
        ]

        # Check if every material property exists in the material
        for property in MATERIAL_PROPERTIES:
            if property not in material:
                return None

        # Format the material properties to remove units
        materialWithoutUnits = {}
        for property in MATERIAL_PROPERTIES:
            matches = re.findall(r"\d+.\d+|\d+", material[property])
            if matches:
                materialWithoutUnits[property] = float(matches[0])

        return materialWithoutUnits
    
    def getElementsWithMaterial(self, materialObject):
        """Returns a list of elements (solid or faces) with the material"""
        references = materialObject.References
        elementsWithMaterial = []

        for reference in references:
            part, elementNames = reference
            for elementName in elementNames:
                element = part.getSubObject(elementName)
                elementsWithMaterial.append(element)

        return elementsWithMaterial
        
    def getTrianglesFromElements(self, elements, femMeshObject):
        """Returns a list of triangles from a list of elements"""
        triangles = []
        shape = femMeshObject.FemMesh
        # The first n IDs are the edges of the shape
        # It start with ID 1, so we sum 1 to start in 0
        idOffset = shape.EdgeCount + 1

        # In a FreeCAD Fem Mesh, a face is a triangle
        # While a face in a FreeCAD solid is a face of the solid
        for element in elements:
            if element.ShapeType == "Solid":
                faces = element.Faces
                for face in faces:
                    triangles.extend([ id - idOffset for id in shape.getFacesByFace(face) ])
            elif element.ShapeType == "Face":
                triangles.extend([ id - idOffset for id in shape.getFacesByFace(element) ])
            else:
                FreeCAD.Console.PrintError(f"Element {element.Name} is not a solid or face\n")
                FreeCAD.Console.PrintError(f"This could be causing an error on the mesh generation\n")

        return triangles
    
    def writeFemMeshAsVtk(self, femMeshObject, path):
        """Writes the mesh as a vtk file"""
        meshPath = os.path.join(path, "mesh.vtk")
        
        FreeCAD.Console.PrintMessage(f"Writing to file {meshPath}\n")
        femMeshObject.FemMesh.write(meshPath)
        FreeCAD.Console.PrintMessage(f"Exported mesh to file {meshPath}\n")

    def writeMaterialAsJson(self, properties, elements, path):
        """Writes the material as a json file"""
        materialPath = os.path.join(path, "mesh.json")

        FreeCAD.Console.PrintMessage(f"Writing to file {materialPath}\n")
        with open(materialPath, "w") as file:
            json.dump(
                {
                    "global_properties": self.workbench.getGlobalPropertiesValues(),
                    "materials": {
                        "properties": properties,
                        "elements": elements
                    }
                },
                file,
                indent=4,
                cls=CustomJsonEncoder,
            )

        FreeCAD.Console.PrintMessage(f"Exported mesh to file {materialPath}\n")

