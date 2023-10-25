use super::element::{Element, MaterialProperties, ViewFactors};
use super::engine::{FEMOrbitParameters, FEMProblem};
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

#[derive(Debug, Deserialize)]
pub struct ParserElementCsv {
    _id: u32,
    nodeidx1: u32,
    nodeidx2: u32,
    nodeidx3: u32,
}

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
pub struct ParserNode {
    id: u32,
    x: f64,
    y: f64,
    z: f64,
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesMaterialsDetails {
    thermal_conductivity: f64,
    density: f64,
    specific_heat: f64,
    initial_temperature: f64, //TODO: Remove in final version
                              //flux: f64,                //TODO: Remove in final version
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

pub fn fem_results_to_vtk(
    results_path: String,
    points: &Vec<Point>,
    elements: &Vec<Element>,
    results: &Vector,
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
                    .with_data(results.iter().map(|&x| x).collect::<Vec<f64>>())],
                cell: vec![],
            },
        }),
    };

    let _ = vtk_data.export_ascii(results_path + ".vtk");

    Ok(())
}

pub fn fem_multiple_results_to_vtk(
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
        fem_results_to_vtk(file_path, points, elements, result)?;
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

pub fn fem_results_to_csv(results_path: String, results: &Vector) -> Result<()> {
    let r: Vec<FEMResult> = results
        .iter()
        .enumerate()
        .map(|(i, &x)| FEMResult {
            id: i as u32,
            temp: x,
        })
        .collect();

    // Serialize the data to CSV
    let mut writer = csv::WriterBuilder::new()
        .has_headers(false)
        .from_path(results_path + ".csv")?;

    // Serialize and write each Result struct
    for result in r.iter() {
        writer.serialize(result)?;
    }

    // Finish writing and flush the file
    writer.flush()?;

    Ok(())
}

pub fn fem_multiple_results_to_csv(
    directory_path: String,
    file_name: String,
    format: String,
    results: &Vec<Vector>,
) -> Result<()> {
    std::fs::create_dir_all(&directory_path)?;
    for (i, result) in results.iter().enumerate() {
        let file_path = format!("{}/{}_{}.{}", directory_path, file_name, i, format);
        fem_results_to_csv(file_path, result)?;
    }
    Ok(())
}

pub fn fem_problem_from_csv(
    elements_path: String,
    nodes_path: String,
    initial_temp: HashMap<u32, f64>,
) -> FEMProblem {
    //Alumium
    let conductivity = 237.0;
    let density = 2700.0;
    let specific_heat = 900.0;
    let thickness = 0.1;
    let alpha_sun = 1.0;
    let alpha_ir = 1.0;
    let solar_intensity = 300.0;
    let betha = 0.1;
    let albedo_factor = 0.1;
    let altitude = 2000.0; //km
    let orbit_period = 100000.0; //s

    let orbit_parameters = FEMOrbitParameters {
        betha,
        altitude,
        orbit_period,
    };

    let mut reader = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_path(nodes_path)
        .unwrap();

    let mut points: Vec<Point> = Vec::new();

    for result in reader.deserialize() {
        let pnode: ParserNode = result.unwrap();
        let temp = initial_temp.get(&pnode.id).unwrap_or(&273f64);
        points.push(Point::new(
            Vector::from_row_slice(&[pnode.x, pnode.y, pnode.z]),
            *temp,
            pnode.id,
            0,
        ));
    }

    points.sort_by_key(|p| p.global_id);

    let mut elements: Vec<Element> = Vec::new();

    let mut reader = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_path(elements_path)
        .unwrap();

    let mut elements_count = 0;
    for result in reader.deserialize() {
        let _: ParserNode = result.unwrap();
        elements_count += 1;
    }

    let _ = reader.seek(csv::Position::new());

    for result in reader.deserialize() {
        let pelement: ParserElementCsv = result.unwrap();
        let p1 = points[pelement.nodeidx1 as usize].clone();
        let p2 = points[pelement.nodeidx2 as usize].clone();
        let p3 = points[pelement.nodeidx3 as usize].clone();

        let props = MaterialProperties {
            conductivity,
            density,
            specific_heat,
            thickness,
            alpha_sun,
            alpha_ir,
        };

        let factors = ViewFactors {
            earth: 1.0,
            sun: 1.0,
            elements: vec![0.1f64; elements_count],
        };

        elements.push(Element::new(
            p1,
            p2,
            p3,
            props,
            factors,
            solar_intensity,
            betha,
            albedo_factor,
            0.0,
        ));
    }

    FEMProblem {
        simulation_time: 0.0,
        time_step: 0.0,
        elements,
        snapshot_period: 0.0,
        orbit_parameters,
    }
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

    let thickness = 0.1; //Add to global properties
    let alpha_sun = 1.0; //Add to global properties
    let alpha_ir = 1.0; //Add to global properties

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
            thickness,
            alpha_sun,
            alpha_ir,
        };
        for element_id in material_elements {
            parser_elements[element_id as usize].material = material_properties.clone();
            parser_elements[element_id as usize].initial_temperature =
                file_material_properties.initial_temperature; //TODO: Remove in final version
                                                              //parser_elements[element_id as usize].flux = file_material_properties.flux;
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
        simulation_time: 0.0,
        time_step: 0.0,
        elements,
        snapshot_period: 0.0,
        orbit_parameters,
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
