use super::constants::{MATERIALS_FILE_NAME, VIEW_FACTORS_FILE_NAME, VTK_FILE_NAME};
use super::element::{Element, MaterialProperties, ViewFactors};
use super::engine::FEMParameters;
use super::orbit_manager::{OrbitManager, OrbitParameters};
use super::point::Point;
use super::structures::{Matrix, Vector};
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use serde_json;
use std::collections::HashMap;
use std::fs::File;
use std::io::BufReader;
use std::path::Path;
use vtkio::model::DataSet;
use vtkio::model::*;

extern crate bincode;
extern crate byteorder;
use byteorder::{BigEndian, ReadBytesExt};

pub struct FEMProblem {
    pub elements: Vec<Element>,
    pub parameters: FEMParameters,
    pub orbit_manager: OrbitManager,
}

#[derive(Debug)]
pub struct ParserElement {
    nodeidx1: u32,
    nodeidx2: u32,
    nodeidx3: u32,
    material: MaterialProperties,
    initial_temperature: f64,
    flux: f64,
    two_sides_radiation: bool,
}

#[derive(Deserialize)]
pub struct ParserConfig {
    pub vtk_path: String,
    pub materials_path: String,
    pub view_factors_path: String,
    pub results_path: String,
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesMaterialsDetails {
    thermal_conductivity: f64,
    density: f64,
    specific_heat: f64,
    thickness: f64,
    alpha_sun: f64,
    alpha_ir: f64,
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesMaterials {
    properties: HashMap<String, ParserPropertiesMaterialsDetails>,
    elements: HashMap<String, Vec<u32>>,
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesConditionsDetails {
    initial_temperature: f64,
    initial_temperature_on: bool,
    flux: f64,
    flux_on: bool,
    two_sides_radiation: bool,
}

#[derive(Debug, Deserialize)]
pub struct ParserPropertiesConditions {
    properties: HashMap<String, ParserPropertiesConditionsDetails>,
    elements: HashMap<String, Vec<u32>>,
}

struct ParserViewFactors {
    earth_ir: Vec<(Vector, f32)>,
    earth_albedo: Vec<(Vector, f32)>,
    sun: Vec<(Vector, f32)>,
    elements: Matrix,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub struct ParserGlobalProperties {
    beta_angle: f64,
    orbital_period: f64,
    albedo: f64,
    earth_ir: f64,
    solar_constant: f64,
    space_temperature: f64,
    initial_temperature: f64,
    time_step: f64,
    snap_period: f64,
    simulation_time: f64,
    eclipse_start: f64,
    eclipse_end: f64,
}

#[derive(Debug, Deserialize)]
pub struct ParserProperties {
    global_properties: ParserGlobalProperties,
    materials: ParserPropertiesMaterials,
    conditions: ParserPropertiesConditions,
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

/// The function `result_to_vtk` converts simulation results into VTK format for visualization.
///
/// Arguments:
///
/// * `results_path`: A string representing the path where the VTK file will be saved.
/// * `points`: A vector of Point structs, where each Point struct represents a point in 3D space and
/// contains the position of the point as an array of three coordinates (x, y, z).
/// * `elements`: The `elements` parameter is a vector of `Element` structs. Each `Element` struct
/// represents a geometric element in the mesh. It contains information about the vertices that make up
/// the element, such as their global IDs.
/// * `result`: The `result` parameter is a reference to a `Vector` which contains the result values for
/// each point in the `points` vector.
///
/// Returns:
///
/// a `Result` type.
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

/// The function writes a partial VTK result file based on the given configuration, points, elements,
/// result, and id.
///
/// Arguments:
///
/// * `config`: A reference to a ParserConfig struct, which contains configuration settings for the
/// parser.
/// * `points`: A vector of Point objects, representing the coordinates of the points in the mesh.
/// * `elements`: A vector containing the elements of the mesh.
/// * `result`: The `result` parameter is of type `Vector`.
/// * `id`: The `id` parameter is an identifier used to differentiate between different result files. It
/// is of type `usize`, which means it represents a non-negative integer value.
///
/// Returns:
///
/// a `Result` type.
pub fn write_partial_vtk_result(
    config: &ParserConfig,
    points: &Vec<Point>,
    elements: &Vec<Element>,
    result: Vector,
    id: usize,
) -> Result<()> {
    let results_path = &config.results_path;
    let file_path = format!("{results_path}/result_{id}");
    let vtk_series_path = format!("{results_path}/result.vtk.series");

    let dir_path = Path::new(&vtk_series_path);
    if dir_path.exists() {
        std::fs::remove_dir_all(&results_path)?;
    }

    std::fs::create_dir_all(&results_path)?;
    result_to_vtk(file_path, points, elements, &result)?;

    Ok(())
}

/// The function `write_vtk_series` creates a VTK series file with a specified number of files and time
/// intervals.
///
/// Arguments:
///
/// * `config`: A configuration object that contains information about the results path and other
/// settings.
/// * `size`: The `size` parameter represents the number of snapshots in the VTK series.
/// It determines how many VTK files will be generated in the series.
/// * `snapshot_period`: The `snapshot_period` parameter represents the time interval between each
/// snapshot in the VTK series.
///
/// Returns:
///
/// a `Result` type.
pub fn write_vtk_series(config: &ParserConfig, size: usize, snapshot_period: f64) -> Result<()> {
    let results_path = &config.results_path;

    let mut files_data: Vec<VTKSeriesContent> = Vec::new();
    for i in 0..size {
        let file_name = format!("result_{i}.vtk");
        files_data.push(VTKSeriesContent {
            name: file_name,
            time: snapshot_period * i as f64,
        });
    }
    let data = VTKSeries {
        file_series_version: String::from("1.0"),
        files: files_data,
    };

    let vtk_series_path = format!("{results_path}/result.vtk.series");
    let file = File::create(vtk_series_path)?;
    serde_json::to_writer(file, &data)?;

    Ok(())
}

/// The function `fem_problem_from_vtk` parses VTK files and creates a FEMProblem struct for further
/// analysis.
///
/// Returns:
///
/// a Result<FEMProblem>
pub fn fem_problem_from_vtk(config: &ParserConfig) -> Result<FEMProblem> {
    let vtk_file_path = &config.vtk_path;
    let properties_file_path = &config.materials_path;
    let view_factors_path = &config.view_factors_path;

    //Elements
    let properties_reader = BufReader::new(
        File::open(&properties_file_path)
            .with_context(|| format!("Couldn't read properties file {properties_file_path}"))?,
    );
    let properties_json: ParserProperties = serde_json::from_reader(properties_reader)
        .with_context(|| format!("Couldn't parser properties file {properties_file_path}"))?;

    let mut global_properties = properties_json.global_properties;
    global_properties.beta_angle = global_properties.beta_angle.to_radians();

    let view_factors_parsed = deserialize_view_factors(&view_factors_path)
        .with_context(|| "Couldn't deserialize view factors")?;

    let vtk_file = Vtk::import(&vtk_file_path)
        .with_context(|| format!("Couldn't import vtk file: {vtk_file_path}"))?;

    let mut points: Vec<Point> = Vec::new();
    let mut parser_elements: Vec<ParserElement> = Vec::new();

    if let DataSet::UnstructuredGrid { meta: _, pieces } = vtk_file.data {
        if let Piece::Inline(vtk_piece) = &pieces[0] {
            //Points
            if let IOBuffer::F32(vtk_points) = &vtk_piece.points {
                for (id, vtk_point) in vtk_points.chunks(3).enumerate() {
                    assert!(vtk_point.len() == 3);
                    let temp = &273f64;
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
                for vtk_element in vertices.chunks(4) {
                    assert!(vtk_element.len() == 4);
                    parser_elements.push(ParserElement {
                        nodeidx1: vtk_element[1],
                        nodeidx2: vtk_element[2],
                        nodeidx3: vtk_element[3],
                        material: MaterialProperties::default(),
                        initial_temperature: global_properties.initial_temperature,
                        flux: 0.0,
                        two_sides_radiation: false,
                    });
                }
            }
        }
    }

    let mut orbit_divisions = vec![];
    for i in 0..view_factors_parsed.earth_albedo.len() {
        orbit_divisions.push(view_factors_parsed.earth_albedo[i].1 as f64);
    }

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
        }
    }

    for (condition_name, condition_elements) in properties_json.conditions.elements {
        let file_condition_properties = &properties_json.conditions.properties[&condition_name];
        for element_id in condition_elements {
            let id = element_id as usize;
            if file_condition_properties.initial_temperature_on {
                parser_elements[id].initial_temperature = file_condition_properties.initial_temperature;
            }
            if file_condition_properties.flux_on {
                parser_elements[id].flux = file_condition_properties.flux;
            }
            parser_elements[id].two_sides_radiation = file_condition_properties.two_sides_radiation;
        }
    }

    let mut elements: Vec<Element> = Vec::new();

    let initial_temperatures: HashMap<u32, (f64, u32)> =
        calculate_node_initial_temperatures(&parser_elements);

    let orbit_parameters = OrbitParameters {
        orbit_period: global_properties.orbital_period,
        orbit_divisions,
        eclipse_start: global_properties.eclipse_start,
        eclipse_end: global_properties.eclipse_end,
    };

    let orbit_manager = OrbitManager::new(&orbit_parameters);
    let orbit_divisions = orbit_manager.eclipse_divisions();
    for (parser_element_id, parser_element) in parser_elements.iter().enumerate() {
        let mut p1 = points[parser_element.nodeidx1 as usize].clone();
        let mut p2 = points[parser_element.nodeidx2 as usize].clone();
        let mut p3 = points[parser_element.nodeidx3 as usize].clone();

        p1.temperature = initial_temperatures[&parser_element.nodeidx1].0
            / initial_temperatures[&parser_element.nodeidx1].1 as f64;
        p2.temperature = initial_temperatures[&parser_element.nodeidx2].0
            / initial_temperatures[&parser_element.nodeidx2].1 as f64;
        p3.temperature = initial_temperatures[&parser_element.nodeidx3].0
            / initial_temperatures[&parser_element.nodeidx3].1 as f64;

        let mut elements_view_factors = vec![
            0.0;
            view_factors_parsed
                .elements
                .row(parser_element_id as usize)
                .len()
        ];
        for i in 0..view_factors_parsed
            .elements
            .row(parser_element_id as usize)
            .len()
        {
            elements_view_factors[i] =
                view_factors_parsed.elements.row(parser_element_id as usize)[i];
        }

        let factors = ViewFactors {
            earth_ir: view_factors_parsed
                .earth_ir
                .iter()
                .map(|(vec, _)| vec[parser_element_id as usize])
                .collect(),
            earth_albedo: view_factors_parsed
                .earth_albedo
                .iter()
                .map(|(vec, _)| vec[parser_element_id as usize])
                .collect(),
            sun: view_factors_parsed.sun[0].0[parser_element_id as usize],
            elements: elements_view_factors,
        };

        elements.push(
            Element::new(
                p1,
                p2,
                p3,
                parser_element.material.clone(),
                factors,
                global_properties.solar_constant,
                global_properties.earth_ir,
                global_properties.albedo,
                parser_element.flux,
                parser_element.two_sides_radiation,
                orbit_divisions,
            )
            .with_context(|| format!("Couldn't create element of id {}", elements.len()))?,
        );
    }

    Ok(FEMProblem {
        parameters: FEMParameters {
            simulation_time: global_properties.simulation_time,
            time_step: global_properties.time_step,
            snapshot_period: global_properties.snap_period,
        },
        elements,
        orbit_manager,
    })
}

/// The function calculates the initial temperatures of nodes based on a list of parser elements.
///
/// Arguments:
///
/// * `parser_elements`: The `parser_elements` parameter is a reference to a vector of `ParserElement`
/// structs. Each `ParserElement` struct contains information about an element
///
/// Returns:
///
/// The function `calculate_node_initial_temperatures` returns a `HashMap<u32, (f64, u32)>`.
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

/// The function updates the initial temperatures of nodes in a HashMap by adding a new temperature
/// value and incrementing the count.
///
/// Arguments:
///
/// * `initial_temperatures`: A mutable reference to a HashMap where the key is of type u32 and the
/// value is a tuple of type (f64, u32). This HashMap stores the initial temperatures for different
/// nodes.
/// * `node`: The `node` parameter is an unsigned 32-bit integer that represents a unique identifier for
/// a node in a system or network.
/// * `temperature`: The `temperature` parameter is a `f64` type, which represents a floating-point
/// number used to store the temperature value.
fn update_initial_temperatures(
    initial_temperatures: &mut HashMap<u32, (f64, u32)>,
    node: u32,
    temperature: f64,
) {
    let entry = initial_temperatures.entry(node).or_insert((0.0, 0));
    *entry = (entry.0 + temperature, entry.1 + 1);
}

/// The function `parse_config` takes a directory path as input and returns a `ParserConfig` struct with
/// file paths based on the input directory path.
///
/// Arguments:
///
/// * `directory_path`: The `directory_path` parameter is a string that represents the path to a
/// directory.
///
/// Returns:
///
/// a Result object containing a ParserConfig struct.
pub fn parse_config(directory_path: &str) -> Result<ParserConfig> {
    return Ok(ParserConfig {
        vtk_path: format!("{}/{}", directory_path, VTK_FILE_NAME),
        materials_path: format!("{}/{}", directory_path, MATERIALS_FILE_NAME),
        view_factors_path: format!("{}/{}", directory_path, VIEW_FACTORS_FILE_NAME),
        results_path: format!("{}/results", directory_path),
    });
}

const FACTOR: f64 = 1.0 / ((1 << 16) - 1) as f64;

/// The function `deserialize_matrix` reads matrix data from a file and returns a `Matrix` object.
///
/// Arguments:
///
/// * `file`: `file` is a mutable reference to a `File` object. It is used to read data from the file.
///
/// Returns:
///
/// The function `deserialize_matrix` returns a `Result<Matrix>`.
fn deserialize_matrix(file: &mut File) -> Result<Matrix> {
    let rows = file
        .read_u16::<BigEndian>()
        .with_context(|| "Couldn't deserialize matrix rows")?;
    let columns = file
        .read_u16::<BigEndian>()
        .with_context(|| "Couldn't deserialize matrix columns")?;

    let num_elements = (rows as usize) * (columns as usize);

    let mut matrix_data: Vec<u16> = vec![0; num_elements];

    file.read_u16_into::<BigEndian>(&mut matrix_data)
        .with_context(|| "Couldn't deserialize matrix data")?;

    Ok(Matrix::from_row_iterator(
        rows.into(),
        columns.into(),
        matrix_data.into_iter().map(|x| x as f64 * FACTOR),
    ))
}

/// The function `deserialize_vector` reads data from a file and returns a tuple containing a vector and
/// a start time.
///
/// Arguments:
///
/// * `file`: A mutable reference to a `File` object, which represents a file that will be read from.
///
/// Returns:
///
/// The function `deserialize_vector` returns a `Result` containing a tuple `(Vector, f32)`.
fn deserialize_vector(file: &mut File) -> Result<(Vector, f32)> {
    let size = file
        .read_u16::<BigEndian>()
        .with_context(|| "Couldn't deserialize vector size")?;

    let start_time = file
        .read_f32::<BigEndian>()
        .with_context(|| "Couldn't deserialize vector start time")?;

    let mut data: Vec<u16> = vec![0; size.into()];

    file.read_u16_into::<BigEndian>(&mut data)
        .with_context(|| "Couldn't deserialize vector data")?;

    let vec = Vector::from_row_iterator(size.into(), data.into_iter().map(|x| x as f64 * FACTOR));

    Ok((vec, start_time))
}

/// The function `deserialize_multiple_vectors` reads a file and deserializes multiple vectors along
/// with their associated float values.
///
/// Arguments:
///
/// * `file`: A mutable reference to a `File` object, which represents a file that will be read from.
///
/// Returns:
///
/// The function `deserialize_multiple_vectors` returns a `Result` containing a `Vec` of tuples
/// `(Vector, f32)`.
fn deserialize_multiple_vectors(file: &mut File) -> Result<Vec<(Vector, f32)>> {
    let len = file
        .read_u16::<BigEndian>()
        .with_context(|| "Couldn't deserialize vector length")?;
    let mut vectors: Vec<_> = vec![];

    for _ in 0..len {
        let v = deserialize_vector(file)
            .with_context(|| format!("Couldn't deserialize {len} vector"))?;
        vectors.push(v);
    }

    Ok(vectors)
}

/// The function `deserialize_view_factors` reads data from a file and deserializes it into a struct
/// called `ParserViewFactors`.
///
/// Arguments:
///
/// * `filename`: The `filename` parameter is a string that represents the name of the file that
/// contains the view factors data.
///
/// Returns:
///
/// The function `deserialize_view_factors` returns a `Result` containing a `ParserViewFactors` struct
/// if the deserialization is successful.
fn deserialize_view_factors(filename: &str) -> Result<ParserViewFactors> {
    let mut file = File::open(filename)
        .with_context(|| format!("Couldn't open view factors file {filename}"))?;

    let earth_ir = deserialize_multiple_vectors(&mut file)
        .with_context(|| "Couldn't deserialize Earth IR view factors vector")?;
    let earth_albedo = deserialize_multiple_vectors(&mut file)
        .with_context(|| "Couldn't deserialize Earth Albedo view factors vector")?;
    let sun = deserialize_multiple_vectors(&mut file)
        .with_context(|| "Couldn't deserialize Sun view factors vector")?;
    let elements = deserialize_matrix(&mut file)
        .with_context(|| "Couldn't deserialize Elements view factors matrix")?;

    Ok(ParserViewFactors {
        earth_ir,
        earth_albedo,
        sun,
        elements,
    })
}
