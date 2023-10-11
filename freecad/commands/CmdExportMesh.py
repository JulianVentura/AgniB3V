import FreeCAD
import os

class CmdExportMesh:
    def Activated(self):
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
        
        triangles = {}
        trianglesByNode = {}

        FreeCAD.Console.PrintMessage("Getting shape mesh object\n")
        shapeMeshObject = femMeshObject.FemMesh
        if shapeMeshObject.FaceCount == 0:
            FreeCAD.Console.PrintError("No faces found in mesh\n")
            FreeCAD.Console.PrintError("This is probably because mesh was generated with 3D shape\n")
            return
        
        for face in shapeMeshObject.Faces:
            triangleNodes = shapeMeshObject.getElementNodes(face)
            triangles[face] = triangleNodes
            for node in triangleNodes:
                trianglesByNode[node] = trianglesByNode.get(node, []) + [face]
        
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

        meshNodes = shapeMeshObject.Nodes
        nodesByMaterial = {}
        trianglesByMaterial = {}
        materialPropsDict = {}

        FreeCAD.Console.PrintMessage("Getting elements with material\n")
        for materialObject in materialObjects:
            elementsWithMaterial = self.getElementsWithMaterial(materialObject)
            if len(elementsWithMaterial) == 0:
                FreeCAD.Console.PrintError(f"No elements found with material {materialObject.Label}\n")
                return

            FreeCAD.Console.PrintMessage("Getting nodes from elements\n")
            nodesWithMaterial = self.getNodesFromElements(elementsWithMaterial, femMeshObject)
            if len(nodesWithMaterial) == 0:
                FreeCAD.Console.PrintError(f"No nodes found with material {materialObject.Label}\n")
                return
            
            trianglesWithMaterial = self.getTrianglesFromElements(elementsWithMaterial, femMeshObject)
            if len(trianglesWithMaterial) == 0:
                FreeCAD.Console.PrintError(f"No triangles found with material {materialObject.Label}\n")
                return
            
            # TODO: is better key to be the name, label, id or something else?
            nodesByMaterial[materialObject.Name] = nodesWithMaterial
            trianglesByMaterial[materialObject.Name] = trianglesWithMaterial
            materialPropsDict[materialObject.Name] = materialObject.Material

        # writing path
        path = os.path.dirname(document.FileName)
        FreeCAD.Console.PrintMessage(f"Writing to file {path}/mesh.txt\n")
        # Open file and write
        with open("mesh.txt", "w") as file:
            file.write("--Material properties--\n")
            for material in materialPropsDict:
                file.write(f"{material}: {materialPropsDict[material]}\n")
            
            file.write("\n--Nodes--\n")
            for node in meshNodes:
                file.write(f"N{node}: {list(shapeMeshObject.getNodeById(node))}\n")

            file.write("\n--Triangles--\n")
            for triangle in triangles:
                file.write(f"T{triangle}: {[f'N{n}' for n in triangles[triangle]]}\n")

            file.write("\n--Triangles by nodes--\n")
            for node in sorted(trianglesByNode):
                file.write(f"N{node}: {[f'T{t}' for t in trianglesByNode[node]]}\n")

            file.write("\n--Nodes by material--\n")
            for material in nodesByMaterial:
                file.write(f"{material}: {[f'N{n}' for n in nodesByMaterial[material]]}\n")

            file.write("\n--Triangles by material--\n")
            for material in nodesByMaterial:
                file.write(f"{material}: {[f'T{t}' for t in trianglesByMaterial[material]]}\n")

        FreeCAD.Console.PrintMessage("Exported mesh to mesh.txt\n")

        FreeCAD.Console.PrintMessage(f"Writing to file {path}/mesh.vtk\n")
        femMeshObject.FemMesh.write("mesh.vtk")

    def IsActive(self):
        return bool(FreeCAD.activeDocument())
        
    def GetResources(self):
        return {
            'MenuText': ("Set Global Properties"),
            'ToolTip': ("Set Global Properties"),
            'Pixmap': "./public/icons/Export.svg",
        }
    
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
    
    def getElementsWithMaterial(self, materialObject):
        """Returns a list of elements (solid or faces) with the material"""
        references = materialObject.References
        elementsWithMaterial = []

        for reference in references:
            part, elementNames = reference
            for elementName in elementNames:
                # TODO: is okay to assume getSubObject exists in part?
                element = part.getSubObject(elementName)
                elementsWithMaterial.append(element)

        return elementsWithMaterial
    
    def getNodesFromElements(self, elements, femMeshObject):
        """Returns a list of nodes from a list of elements"""
        nodes = []
        shape = femMeshObject.FemMesh

        for element in elements:
            if element.ShapeType == "Solid":
                nodes.extend(shape.getNodesBySolid(element))
            elif element.ShapeType == "Face":
                nodes.extend(shape.getNodesByFace(element))
            else:
                FreeCAD.Console.PrintError(f"Element {element.Name} is not a solid or face\n")
                FreeCAD.Console.PrintError(f"This could be causing an error on the mesh generation\n")

        return nodes
    
    def getTrianglesFromElements(self, elements, femMeshObject):
        """Returns a list of triangles from a list of elements"""
        triangles = []
        shape = femMeshObject.FemMesh

        # In a FreeCAD Fem Mesh, a face is a triangle
        # While a face in a FreeCAD solid is a face of the solid
        for element in elements:
            if element.ShapeType == "Solid":
                faces = element.Faces
                for face in faces:
                    triangles.extend(shape.getFacesByFace(face))
            elif element.ShapeType == "Face":
                triangles.extend(shape.getFacesByFace(element))
            else:
                FreeCAD.Console.PrintError(f"Element {element.Name} is not a solid or face\n")
                FreeCAD.Console.PrintError(f"This could be causing an error on the mesh generation\n")

        return triangles
