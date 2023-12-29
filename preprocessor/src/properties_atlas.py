import numpy as np
import json
from . import gmat_parser
from .custom_json_encoder import CustomJsonEncoder


class PropertiesAtlas:
    """
    Implements a class that loads the properties of the materials from a json file.
    """

    def _build_material_index(self, elements_amount, properties_json):
        self.materials = []
        self.material_by_element = np.full(elements_amount, -1)
        self.absortance_ir_by_element = np.zeros(elements_amount)

        material_json_props = properties_json["materials"]["properties"]
        material_json_elements = properties_json["materials"]["elements"]
        for material_name, material_elements in material_json_elements.items():
            material_idx = len(self.materials)
            self.materials.append(material_json_props[material_name])
            self.materials[-1]["name"] = material_name
            for element_id in material_elements:
                self.material_by_element[element_id] = material_idx
                self.absortance_ir_by_element[element_id] = self.materials[-1]["alpha_ir"]
        
        for element_id, material_id in enumerate(self.material_by_element):
            if material_id < 0:
                print(f"Warning: Element {element_id} does not have a material")

    def _build_condition_index(self, elements_amount, properties_json):
        self.two_sides_emission_by_element = np.zeros(elements_amount, dtype=bool)
    
        if not properties_json.get("conditions", None):
            return
        properties = properties_json["conditions"]["properties"]
        elements = properties_json["conditions"]["elements"]
        for condition_name, condition_props in properties.items():
            two_sides_emission = condition_props["two_sides_radiation"] if condition_props["two_sides_radiation"] else False
            for element_id in elements[condition_name]:
                self.two_sides_emission_by_element[element_id] = two_sides_emission

    def _add_global_orbit_properties(self):
        self.global_properties["beta_angle"] = self.orbit_properties.beta_angle
        self.global_properties["orbital_period"] = self.orbit_properties.period
        eclipse_start, eclipse_end = self.orbit_properties.eclipse_start_finish
        self.global_properties["eclipse_start"] = eclipse_start
        self.global_properties["eclipse_end"] = eclipse_end

    def __init__(
        self,
        elements_amount,
        props_file_path,
        orbit_report_file_path=None,
        orbit_eclipse_file_path=None,
    ):
        """
        Receives the amount of elements and the path to the json file.
        It loads the json file and creates a list of materials and a list of
        materials by element.
        """
        with open(props_file_path) as material_file:
            self.properties_json = json.load(material_file)
            self.global_properties = self.properties_json["global_properties"]
            if orbit_report_file_path and orbit_eclipse_file_path:
                self.orbit_properties = gmat_parser.parse_gmat(
                    orbit_report_file_path, orbit_eclipse_file_path
                )
            else:
                self.orbit_properties = None
            self._build_material_index(elements_amount, self.properties_json)
            self._build_condition_index(elements_amount, self.properties_json)

    def get_element_material(self, element_index):
        """
        Recieves an index and returns the properties of the material of the element
        with the given index.
        """
        return self.materials[self.material_by_element[element_index]]

    def dump(self, output_path):
        """
        Recieves an output path and dumps the properties json to a file.
        """
        output_json = self.properties_json
        if self.orbit_properties:
            self._add_global_orbit_properties()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                output_json,
                f,
                indent=4,
                ensure_ascii=True,
                cls=CustomJsonEncoder,
            )
