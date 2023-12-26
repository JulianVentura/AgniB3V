import FreeCAD
import os
import json
import re
from utils.jsonToCamelCase import dictToCamelCase
from utils.firstForCondition import firstForCondition
from public.utils import iconPath
from utils.CustomJsonEncoder import CustomJsonEncoder
from ui.DialogExport import DialogExport
from constants.material_properties import MATERIAL_PROPERTIES
from constants.condition_properties import CONDITION_PROPERTIES
import vtk
from constants import CONDITIONS_GROUP, CONFIG_GROUP, MATERIALS_GROUP

class CmdExportMesh:
    def __init__(self, workbench):
        self.workbench = workbench

    def Activated(self):
        """
        Executed when the command is activated
        """
        form = DialogExport(self.workbench, self.onExport)
        form.exec_()

    def IsActive(self):
        """
        Function to check if the command is active
        """
        isActiveDocument = bool(FreeCAD.activeDocument())
        configExists = bool(FreeCAD.activeDocument().getObject(CONFIG_GROUP))
        analysisExists = bool(self.getAnalysisObject(FreeCAD.activeDocument()))
        return isActiveDocument and configExists and analysisExists

    def GetResources(self):
        return {
            'MenuText': ("Export Mesh"),
            'ToolTip': ("Export Mesh"),
            'Pixmap': iconPath("Export.svg"),
        }
    
    # TODO: ¿move to DialogExport?
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
        
        FreeCAD.Console.PrintMessage("Getting condition objects\n")
        conditionObjects = self.getConditionObjects(analysisObject)
        if len(conditionObjects) == 0:
            FreeCAD.Console.PrintWarning("No Conditions found\n")
        
        # TODO: check if there is parts of the object with different materials
        # this can be done by checking if there are solid repeated or faces
        # repeated (for the faces we should check if there are solid and faces combined
        # and check the faces in the solid)
        # This is wrong, but user can set two materials to the same solid/face

        materials = self.getElementAndProperties(femMeshObject, materialObjects, MATERIAL_PROPERTIES)
        conditions = self.getElementAndProperties(femMeshObject, conditionObjects, CONDITION_PROPERTIES)

        # Writing path
        path = self.workbench.getExportPath()
        
        # Open file and write
        FreeCAD.Console.PrintMessage(f"Starting exporting to {path}\n")
        self.writeMaterialAsJson(materials, conditions, path)
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
    
    def getConditionObjects(self, analysisObject):
        """Returns a list of condition objects"""
        conditionsGroup = firstForCondition(
            analysisObject.Group,
            condition=lambda x: x.Name == CONDITIONS_GROUP,
        )
        conditionObjects = []
        for object in conditionsGroup.Group:
            if object.TypeId == "App::MaterialObjectPython":
                conditionObjects.append(object)
        return conditionObjects
    
    def getMaterialObjects(self, analysisObject):
        """Returns a list of material objects"""
        materialsGroup = firstForCondition(
            analysisObject.Group,
            condition=lambda x: x.Name == MATERIALS_GROUP,
        )
        materialObjects = []
        for object in materialsGroup.Group:
            if object.TypeId == "App::MaterialObjectPython":
                materialObjects.append(object)
        return materialObjects
    
    def getProperties(self, material, propertiesRequired):
        """Returns a dictionary of the neccessary properties of the material"""
        materialWithoutUnits = {}

        # Check if every material property exists in the material
        for propertyRequired in propertiesRequired:
            print(propertyRequired, getattr(material, propertyRequired, None))
            if getattr(material, propertyRequired, None) == None:
                return None
            materialWithoutUnits[propertyRequired] = getattr(material, propertyRequired, None)

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
        idOffset = min(shape.Faces)

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

    def getElementAndProperties(self, femMeshObject, materialObjects, propertiesRequired):
        """Returns a dictionary with the elements and the properties of the materials"""
        elements = {}
        properties = {}

        for materialObject in materialObjects:
            FreeCAD.Console.PrintMessage(f"Getting elements and properties for {materialObject.Label}\n")
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
            properties[materialObject.Name] = self.getProperties(materialObject, propertiesRequired)
            if not properties[materialObject.Name]:
                FreeCAD.Console.PrintError(f"Some of the material properties are missing in {materialObject.Label}\n")
                # console the missing properties
                for property in propertiesRequired:
                    if not getattr(materialObject, property, None):
                        FreeCAD.Console.PrintError(f"  Missing property: {property}\n")
                return
        
        return { "elements": elements, "properties": properties }
    
    def writeFemMeshAsVtk(self, femMeshObject, path):
        """Writes the mesh as a vtk file"""
        meshPath = os.path.join(path, "mesh.vtk")
        
        FreeCAD.Console.PrintMessage(f"Writing to file {meshPath}\n")
        femMeshObject.FemMesh.write(meshPath)
        FreeCAD.Console.PrintMessage(f"Modifying file {meshPath}\n")

        reader = vtk.vtkGenericDataObjectReader()
        reader.SetFileName(meshPath)
        reader.Update()

        # Access the data object
        dataObject = reader.GetOutput()

        # Divide every node by 1000
        points = dataObject.GetPoints()
        numPoints = points.GetNumberOfPoints()
        for i in range(numPoints):
            point = points.GetPoint(i)
            point = [coord / 1000 for coord in point]
            points.SetPoint(i, point)

        # Modify the version of the VTK file as needed
        # Write the modified VTK file
        # TODO: write vtk using data from workbench and not from file
        writer = vtk.vtkUnstructuredGridWriter()
        writer.SetFileName(meshPath)
        writer.SetInputData(dataObject)
        writer.SetFileVersion(42)
        writer.Write()

        FreeCAD.Console.PrintMessage(f"Exported mesh to file {meshPath}\n")

    def writeMaterialAsJson(self, materials, conditions, path):
        """Writes the material as a json file"""
        materialPath = os.path.join(path, "properties.json")
        globalProperties = self.workbench.getGlobalPropertiesValues()
        globalProperties = {key: globalProperties[key]["value"] for key in globalProperties}
        dataToUpdate = {
            "globalProperties": globalProperties,
            "materials": materials,
            "conditions": conditions,
        }

        FreeCAD.Console.PrintMessage(f"Checking if {materialPath} exists\n")
        if os.path.exists(materialPath):
            FreeCAD.Console.PrintMessage(f"File {materialPath} exists\n")
            with open(materialPath, "r") as file:
                loadedData = dictToCamelCase(json.load(file))
                dataToUpdate["globalProperties"] = loadedData["globalProperties"]
                dataToUpdate["globalProperties"].update(globalProperties)
        else:
            FreeCAD.Console.PrintMessage(f"File {materialPath} does not exists\n")

        FreeCAD.Console.PrintMessage(f"Writing to file {materialPath}\n")
        with open(materialPath, "w") as file:
            json.dump(
                dataToUpdate,
                file,
                indent=4,
                cls=CustomJsonEncoder,
            )

        FreeCAD.Console.PrintMessage(f"Exported mesh to file {materialPath}\n")

