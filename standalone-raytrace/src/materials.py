import csv
import numpy as np

class Material():
    def __init__(self, name, color, surfaces):
        self.name = name
        self.color = np.array(color)
        self.surfaces = np.array(surfaces)

    def includes(self, surface_index):
        return surface_index in self.surfaces
        

class MaterialAtlas():
    def __init__(self, material_file_path):
        self.materials = []
        with open(material_file_path) as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in spamreader:
                name, colorR,colorG,colorB,colorA, *surfaces = row
                self.materials.append(Material(name,list(map(int, [colorR, colorG, colorB, colorA])), list(map(int, surfaces))))
    
    def get_material(self, surface_index):
        for material in self.materials:
            if material.includes(surface_index):
                return material
        return None