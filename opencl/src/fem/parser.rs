use super::element::Element;
use super::engine::FEMProblem;
use super::point::Point;
use super::structures::Vector;
use serde::Deserialize;

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
    _z: f32,
}

pub fn fem_problem_from_csv() -> FEMProblem {
    let elements_path = "./models/2D-plane_triangles.csv";
    let nodes_path = "./models/2D-plane_verts.csv";

    //Alumium
    let conductivity = 237.0;
    let density = 2700.0;
    let specific_heat = 900.0;
    let thickness = 0.01;

    let mut reader = csv::ReaderBuilder::new()
        .has_headers(false)
        .from_path(nodes_path)
        .unwrap();

    let mut points: Vec<Point> = Vec::new();

    for result in reader.deserialize() {
        let pnode: ParserNode = result.unwrap();
        //TODO: Add 3D
        points.push(Point::new(
            Vector::new([pnode.x, pnode.y]),
            0.0,
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
    }
}
