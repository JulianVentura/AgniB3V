import numpy as np      
import json

class PropertiesAtlas():
    """
    Implements a class that loads the properties of the materials from a json file.
    """

    def __init__(self, elements_amount, material_file_path):
        """
        Receives the amount of elements and the path to the json file.
        It loads the json file and creates a list of materials and a list of
        materials by element.
        """
        self.material_by_element = np.full(elements_amount,-1)
        self.materials = []

        material_file = open(material_file_path)
        self.material_json = json.load(material_file)

        material_json_props = self.material_json["materials"]["properties"]
        material_json_elements = self.material_json["materials"]["elements"]
        for material_name, material_elements in material_json_elements.items():
            material_idx = len(self.materials)
            self.materials.append(material_json_props[material_name])
            for element_id in material_elements:
                self.material_by_element[element_id] = material_idx
        
        for element_id, material_id in enumerate(self.material_by_element):
            if (material_id < 0):
                print(f"Warning: Element {element_id} does not have a material")

    def get_material_props(self, element_index):
        """
        Recieven an index and returns the properties of the material of the element
        with the given index.
        """
        return self.materials[self.material_by_element[element_index]]
    
    def add_prop(self, key, data):
        """
        Receives a key and data and adds it to the material json.
        """
        self.material_json[key] = data

    def dump(self, output_path):
        """
        Recieves an output path and dumps the material json to a file.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
	        json.dump(self.material_json, f, ensure_ascii=True)