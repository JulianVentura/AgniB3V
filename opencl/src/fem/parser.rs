use super::element::{Element, MaterialProperties, ViewFactors};
use super::engine::{FEMOrbitParameters, FEMParameters};
use super::point::Point;
use super::structures::Vector;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use serde_json;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use vtkio::model::DataSet;
use vtkio::model::*;

//Todo: Delete
use std::path::PathBuf;

#[allow(dead_code)]
#[derive(Debug)]
pub struct FEMProblem {
    pub elements: Vec<Element>,
    pub parameters: FEMParameters,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct ParserElement {
    id: u32,
    nodeidx1: u32,
    nodeidx2: u32,
    nodeidx3: u32,
    material: MaterialProperties,
    initial_temperature: f64, //TODO: Remove in final version
    flux: f64,                //TODO: Remove in final version
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesMaterialsDetails {
    thermal_conductivity: f64,
    density: f64,
    specific_heat: f64,
    thickness: f64,
    alpha_sun: f64,
    alpha_ir: f64,
    initial_temperature: f64, //TODO: Remove in final version
    flux: f64,                //TODO: Remove in final version
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesMaterials {
    properties: HashMap<String, ParserPropertiesMaterialsDetails>,
    elements: HashMap<String, Vec<u32>>,
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesViewFactors {
    earth: Vec<f64>,
    sun: Vec<f64>,
    elements: Vec<Vec<f64>>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub struct ParserGlobalProperties {
    beta_angle: f64,
    orbit_height: f64,
    orbital_period: f64,
    albedo: f64,
    earth_ir: f64,
    solar_constant: f64,
    space_temperature: f64,
    initial_temperature: f64,
    time_step: f64,
    snap_period: f64,
    simulation_time: f64,
}

#[derive(Debug, Deserialize)]
pub struct ParserProperties {
    global_properties: ParserGlobalProperties,
    materials: ParserPropertiesMaterials,
    view_factors: ParserPropertiesViewFactors,
}

#[derive(Serialize)]
struct FEMResult {
    id: u32,
    temp: f64,
}

#[derive(Serialize, Deserialize)]
struct VTKSeriesContent {
    name: String,
    time: f64,
}

#[derive(Serialize, Deserialize)]
struct VTKSeries {
    #[serde(rename = "file-series-version")]
    file_series_version: String,
    files: Vec<VTKSeriesContent>,
}

fn result_to_vtk(
    results_path: String,
    points: &Vec<Point>,
    elements: &Vec<Element>,
    result: &Vector,
) -> Result<()> {
    let vtk_data = Vtk {
        version: Version { major: 4, minor: 2 },
        title: String::new(),
        byte_order: ByteOrder::BigEndian,
        file_path: None,
        data: DataSet::inline(UnstructuredGridPiece {
            points: IOBuffer::F64(
                points
                    .iter()
                    .map(|point| [point.position[0], point.position[1], point.position[2]])
                    .flatten()
                    .collect(),
            ),
            cells: Cells {
                cell_verts: VertexNumbers::XML {
                    connectivity: elements
                        .iter()
                        .map(|element| {
                            [
                                element.p1.global_id as u64,
                                element.p2.global_id as u64,
                                element.p3.global_id as u64,
                            ]
                        })
                        .flatten()
                        .collect(),
                    offsets: elements
                        .iter()
                        .enumerate()
                        .map(|(i, _)| (i as u64 + 1) * 3)
                        .collect(),
                },
                types: vec![CellType::Triangle; elements.len()],
            },
            data: Attributes {
                point: vec![Attribute::scalars("Temperature", 1)
                    .with_data(result.iter().map(|&x| x).collect::<Vec<f64>>())],
                cell: vec![],
            },
        }),
    };

    let _ = vtk_data.export_ascii(results_path + ".vtk");

    Ok(())
}

pub fn fem_result_to_vtk(
    directory_path: String,
    file_name: String,
    points: &Vec<Point>,
    elements: &Vec<Element>,
    results: &Vec<Vector>,
    snap_time: f64,
) -> Result<()> {
    std::fs::create_dir_all(&directory_path)?;
    for (i, result) in results.iter().enumerate() {
        let file_path = format!("{}/{}_{}", directory_path, file_name, i);
        result_to_vtk(file_path, points, elements, result)?;
    }
    let mut files_data: Vec<VTKSeriesContent> = Vec::new();
    for (i, _) in results.iter().enumerate() {
        let file_name = format!("{}_{}.vtk", file_name, i);
        files_data.push(VTKSeriesContent {
            name: file_name,
            time: snap_time * i as f64,
        });
    }
    let data = VTKSeries {
        file_series_version: String::from("1.0"),
        files: files_data,
    };

    let vtk_series_path = format!("{}/{}.vtk.series", directory_path, file_name);
    let file = File::create(vtk_series_path)?;
    serde_json::to_writer(file, &data)?;

    Ok(())
}

pub fn fem_problem_from_vtk(
    vtk_file_path: String,
    properties_file_path: String,
    initial_temp: HashMap<u32, f64>,
) -> FEMProblem {
    let file_path = PathBuf::from(vtk_file_path);
    let vtk_file = Vtk::import(&file_path).expect(&format!("Failed to load file: {:?}", file_path));

    let mut points: Vec<Point> = Vec::new();
    let mut parser_elements: Vec<ParserElement> = Vec::new();

    if let DataSet::UnstructuredGrid { meta: _, pieces } = vtk_file.data {
        if let Piece::Inline(vtk_piece) = &pieces[0] {
            //Points
            if let IOBuffer::F32(vtk_points) = &vtk_piece.points {
                for (id, vtk_point) in vtk_points.chunks(3).enumerate() {
                    assert!(vtk_point.len() == 3);
                    let temp = initial_temp.get(&(id as u32)).unwrap_or(&273f64);
                    points.push(Point::new(
                        Vector::from_row_slice(&[
                            vtk_point[0] as f64,
                            vtk_point[1] as f64,
                            vtk_point[2] as f64,
                        ]),
                        *temp,
                        id as u32,
                        0,
                    ));
                }
            }

            // Partial Elements
            if let VertexNumbers::Legacy {
                num_cells: _,
                vertices,
            } = &vtk_piece.cells.cell_verts
            {
                for (id, vtk_element) in vertices.chunks(3).enumerate() {
                    assert!(vtk_element.len() == 3);
                    parser_elements.push(ParserElement {
                        id: id as u32,
                        nodeidx1: vtk_element[0],
                        nodeidx2: vtk_element[1],
                        nodeidx3: vtk_element[2],
                        material: MaterialProperties::default(),
                        initial_temperature: 0.0, //TODO: Remove in final version
                        flux: 0.0,                //TODO: Remove in final version
                    });
                }
            }
        }
    }

    //Elements
    let properties_reader =
        BufReader::new(File::open(properties_file_path).expect("Couldn't read properties file"));
    let properties_json: ParserProperties =
        serde_json::from_reader(properties_reader).expect("Couldn't parse properties file");

    let mut global_properties = properties_json.global_properties;
    global_properties.beta_angle = global_properties.beta_angle.to_radians();

    // Add to model
    // global.properties.earth_ir
    // global.properties.space_temperature
    // global.properties.initial_temperature

    let orbit_parameters = FEMOrbitParameters {
        betha: global_properties.beta_angle,
        altitude: global_properties.orbit_height,
        orbit_period: global_properties.orbital_period,
    };

    for (material_name, material_elements) in properties_json.materials.elements {
        let file_material_properties = &properties_json.materials.properties[&material_name];
        let material_properties = MaterialProperties {
            conductivity: file_material_properties.thermal_conductivity,
            density: file_material_properties.density,
            specific_heat: file_material_properties.specific_heat,
            thickness: file_material_properties.thickness,
            alpha_sun: file_material_properties.alpha_sun,
            alpha_ir: file_material_properties.alpha_ir,
        };
        for element_id in material_elements {
            parser_elements[element_id as usize].material = material_properties.clone();
            parser_elements[element_id as usize].initial_temperature =
                file_material_properties.initial_temperature; //TODO: Remove in final version
            parser_elements[element_id as usize].flux = file_material_properties.flux;
            //TODO: Remove in final version
        }
    }

    let mut elements: Vec<Element> = Vec::new();

    //TODO: Remove in final version
    let initial_temperatures: HashMap<u32, (f64, u32)> =
        calculate_node_initial_temperatures(&parser_elements);

    for (parser_element_id, parser_element) in parser_elements.iter().enumerate() {
        let mut p1 = points[parser_element.nodeidx1 as usize].clone();
        let mut p2 = points[parser_element.nodeidx2 as usize].clone();
        let mut p3 = points[parser_element.nodeidx3 as usize].clone();

        //TODO: Remove in final version
        p1.temperature = initial_temperatures[&parser_element.nodeidx1].0
            / initial_temperatures[&parser_element.nodeidx1].1 as f64;
        p2.temperature = initial_temperatures[&parser_element.nodeidx2].0
            / initial_temperatures[&parser_element.nodeidx2].1 as f64;
        p3.temperature = initial_temperatures[&parser_element.nodeidx3].0
            / initial_temperatures[&parser_element.nodeidx3].1 as f64;

        let factors = ViewFactors {
            earth: properties_json.view_factors.earth[parser_element_id as usize],
            sun: properties_json.view_factors.sun[parser_element_id as usize],
            elements: properties_json.view_factors.elements[parser_element_id as usize].clone(),
        };

        elements.push(Element::new(
            p1,
            p2,
            p3,
            parser_element.material.clone(),
            factors,
            global_properties.solar_constant,
            global_properties.beta_angle,
            global_properties.albedo,
            parser_element.flux,
        ));
    }

    FEMProblem {
        parameters: FEMParameters {
            simulation_time: global_properties.simulation_time,
            time_step: global_properties.time_step,
            snapshot_period: global_properties.snap_period,
            orbit: orbit_parameters,
        },
        elements,
    }
}

//TODO: Remove in final version
fn calculate_node_initial_temperatures(
    parser_elements: &Vec<ParserElement>,
) -> HashMap<u32, (f64, u32)> {
    let mut initial_temperatures: HashMap<u32, (f64, u32)> = HashMap::new();
    for (_, parser_element) in parser_elements.iter().enumerate() {
        update_initial_temperatures(
            &mut initial_temperatures,
            parser_element.nodeidx1,
            parser_element.initial_temperature,
        );
        update_initial_temperatures(
            &mut initial_temperatures,
            parser_element.nodeidx2,
            parser_element.initial_temperature,
        );
        update_initial_temperatures(
            &mut initial_temperatures,
            parser_element.nodeidx3,
            parser_element.initial_temperature,
        );
    }
    initial_temperatures
}

fn update_initial_temperatures(
    initial_temperatures: &mut HashMap<u32, (f64, u32)>,
    node: u32,
    temperature: f64,
) {
    let entry = initial_temperatures.entry(node).or_insert((0.0, 0));
    *entry = (entry.0 + temperature, entry.1 + 1);
}
