use std::collections::HashMap;

use super::element::Element;
use super::engine::FEMProblem;
use super::point::Point;
use super::structures::Vector;
use anyhow::Result;
use serde::{Deserialize, Serialize};

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
        .from_path(results_path)?;

    // Serialize and write each Result struct
    for result in r.iter() {
        writer.serialize(result)?;
    }

    // Finish writing and flush the file
    writer.flush()?;

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
    let thickness = 2e-3;

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

    for result in reader.deserialize() {
        let pelement: ParserElement = result.unwrap();
        let p1 = points[pelement.nodeidx1 as usize].clone();
        let p2 = points[pelement.nodeidx2 as usize].clone();
        let p3 = points[pelement.nodeidx3 as usize].clone();
        elements.push(Element::new(
            p1,
            p2,
            p3,
            conductivity,
            density,
            specific_heat,
            thickness,
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