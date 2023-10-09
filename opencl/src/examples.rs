use std::collections::HashMap;

use anyhow::{anyhow, Result};

use crate::fem::engine::FEMProblem;

use super::fem::{engine::FEMEngine, parser};

pub fn test_2d_plane() -> Result<()> {
    let elements_path = "./models/2D-plane_triangles.csv".to_string();
    let nodes_path = "./models/2D-plane_verts.csv".to_string();
    let results_path = "./models/2D-plane_results".to_string();

    let initial_temp_map: HashMap<u32, f32> = [(0, 373.0), (3, 373.0)].into_iter().collect();

    let problem = parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map);

    let simulation_time = 10.0;
    let time_step = 1.0;

    let mut engine = FEMEngine::new(simulation_time, time_step, &problem.elements, 10.0);

    let temp_results = engine.run()?;

    parser::fem_results_to_csv(
        results_path,
        &temp_results.last().ok_or(anyhow!("No result"))?.clone(),
    )?;

    Ok(())
}

#[allow(dead_code)]
fn test_2_d_plane() -> (FEMProblem, String) {
    let elements_path = "./models/2D_plane_triangles.csv".to_string();
    let nodes_path = "./models/2D_plane_verts.csv".to_string();
    let results_path = "./models/2D_plane_results".to_string();

    let initial_temp_map: HashMap<u32, f32> = [(104, 473.0)].into_iter().collect();

    (
        parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map),
        results_path,
    )
}

#[allow(dead_code)]
fn test_monkey() -> (FEMProblem, String) {
    let elements_path = "./models/monkey_mesh_triangles.csv".to_string();
    let nodes_path = "./models/monkey_mesh_verts.csv".to_string();
    let results_path = "./models/monkey_mesh_results".to_string();

    let initial_temp_map: HashMap<u32, f32> = [(575, 573.0), (633, 573.0)].into_iter().collect();

    (
        parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map),
        results_path,
    )
}

#[allow(dead_code)]
fn test_3_d_plane_non_tilted() -> (FEMProblem, String) {
    let elements_path = "./models/3D_plane_non_tilted_triangles.csv".to_string();
    let nodes_path = "./models/3D_plane_non_tilted_verts.csv".to_string();
    let results_path = "./models/3D_plane_non_tilted_results".to_string();

    //TODO: Check
    let initial_temp_map: HashMap<u32, f32> = [
        (130, 473.0),
        (145, 473.0),
        (146, 473.0),
        (102, 473.0),
        (273, 473.0),
        (261, 473.0),
    ]
    .into_iter()
    .collect();

    (
        parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map),
        results_path,
    )
}

#[allow(dead_code)]
fn test_3_d_cube() -> (FEMProblem, String) {
    let elements_path = "./models/Cube_triangles.csv".to_string();
    let nodes_path = "./models/Cube_verts.csv".to_string();
    let results_path = "./models/Cube_results".to_string();

    let initial_temp_map: HashMap<u32, f32> = [(25, 600.0)].into_iter().collect();

    (
        parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map),
        results_path,
    )
}

#[allow(dead_code)]
fn test_cylinder() -> (FEMProblem, String) {
    let elements_path = "./models/cylinder_triangles.csv".to_string();
    let nodes_path = "./models/cylinder_verts.csv".to_string();
    let results_path = "./models/cylinder_results.csv".to_string();

    let initial_temp_map: HashMap<u32, f32> = [(56, 473.0)].into_iter().collect();

    (
        parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map),
        results_path,
    )
}

#[allow(dead_code)]
fn test_plane_medium() -> (FEMProblem, String) {
    let elements_path = "./models/plane_medium_triangles.csv".to_string();
    let nodes_path = "./models/plane_medium_verts.csv".to_string();
    let results_path = "./models/plane_medium_results.csv".to_string();

    let initial_temp_map: HashMap<u32, f32> = [(265, 473.0), (252, 473.0)].into_iter().collect();

    (
        parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map),
        results_path,
    )
}

pub fn test_plane_0_2() -> Result<()> {
    let name = "plano_chico_mesh";
    let elements_path = format!("./models/{}_triangles.csv", name);
    let nodes_path = format!("./models/{}_verts.csv", name);
    let results_folder = format!("./models/{}_results", name);
    let results_file = format!("{}_results", name);
    let results_format = "csv".to_string();

    let initial_temp_map: HashMap<u32, f32> = [
        (482, 573.0),
        (499, 573.0),
        (501, 573.0),
        (504, 573.0),
        (506, 573.0),
        (509, 573.0),
        (511, 573.0),
        (514, 573.0),
        (516, 573.0),
        (520, 573.0),
        (522, 573.0),
        (525, 573.0),
        (528, 573.0),
        (530, 573.0),
        (532, 573.0),
        (535, 573.0),
        (537, 573.0),
    ]
    .into_iter()
    .collect();

    let problem = parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map);
    println!("{}", problem.elements.len());
    let simulation_time = 0.005;
    let time_step = 0.000001;
    let snap_time = simulation_time / 10.0;

    let mut engine = FEMEngine::new(simulation_time, time_step, &problem.elements, snap_time);

    let temp_results = engine.run()?;

    println!("{}", temp_results.last().unwrap());

    println!("{:#?}", &temp_results.last());

    //Calculate the average temperature

    let mut sum = 0.0;
    let mut len = 0;
    let last = &temp_results.last();
    for temp in last {
        sum += temp.iter().sum::<f32>();
        len += temp.len();
    }
    let avg = sum / len as f32;

    println!("Average temperature: {}", avg);

    parser::fem_multiple_results_to_csv(
        results_folder,
        results_file,
        results_format,
        &temp_results,
    )?;

    Ok(())
}

pub fn run_example() -> Result<()> {
    let (problem, results_path) = test_3_d_cube();

    println!("{}", problem.elements.len());

    let simulation_time = 7200.0;
    let time_step = 1.0;

    let mut engine = FEMEngine::new(simulation_time, time_step, &problem.elements, time_step);

    let temp_results = engine.run()?;

    println!("{}", temp_results.last().unwrap());

    parser::fem_results_to_vtk(
        results_path.clone(),
        &engine.points,
        &problem.elements,
        &temp_results.last().ok_or(anyhow!("No result"))?.clone(),
    )?;

    parser::fem_results_to_csv(
        results_path,
        &temp_results.last().ok_or(anyhow!("No result"))?.clone(),
    )?;

    Ok(())
}
