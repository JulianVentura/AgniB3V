use std::collections::HashMap;

use super::element::{Element, MaterialProperties, ViewFactors};
use super::engine::FEMProblem;
use super::point::Point;
use super::structures::Vector;
use anyhow::Result;
use serde::{Deserialize, Serialize};

use vtkio::model::*;

#[derive(Debug, Deserialize)]
pub struct ParserElement {
    _id: u32,
    nodeidx1: u32,
    nodeidx2: u32,
    nodeidx3: u32,
}

#[derive(Debug, Deserialize)]
pub struct ParserNode {
    id: u32,
    x: f32,
    y: f32,
    z: f32,
}

#[derive(Serialize)]
struct FEMResult {
    id: u32,
    temp: f32,
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
            points: IOBuffer::F32(
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
                point: vec![Attribute::scalars("Temperatura", 1)
                    .with_data(results.iter().map(|&x| x).collect::<Vec<f32>>())],
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
    format: String,
    points: &Vec<Point>,
    elements: &Vec<Element>,
    results: &Vec<Vector>,
) -> Result<()> {
    std::fs::create_dir_all(&directory_path)?;
    for (i, result) in results.iter().enumerate() {
        let file_path = format!("{}/{}_{}.{}", directory_path, file_name, i, format);
        fem_results_to_vtk(file_path, points, elements, result)?;
    }
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
    initial_temp: HashMap<u32, f32>,
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

    let mut reader = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_path(nodes_path)
        .unwrap();

    let mut points: Vec<Point> = Vec::new();

    for result in reader.deserialize() {
        let pnode: ParserNode = result.unwrap();
        let temp = initial_temp.get(&pnode.id).unwrap_or(&273f32);
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
        let pelement: ParserElement = result.unwrap();
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
            elements: vec![0.1f32; elements_count],
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
    }
}
