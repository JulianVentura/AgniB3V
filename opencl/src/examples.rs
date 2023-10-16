use crate::fem;

use super::fem::{
    engine::{FEMEngine, FEMProblem, Solver},
    explicit_solver::ExplicitSolver,
    parser,
};
use anyhow::{anyhow, Result};
use std::collections::HashMap;

#[allow(dead_code)]
fn test_2_d_plane() -> (FEMProblem, String) {
    let elements_path = "./models/2D_plane_triangles.csv".to_string();
    let nodes_path = "./models/2D_plane_verts.csv".to_string();
    let results_path = "./models/2D_plane_results".to_string();

    let initial_temp_map: HashMap<u32, f64> = [(104, 473.0)].into_iter().collect();

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

    let initial_temp_map: HashMap<u32, f64> = [(575, 573.0), (633, 573.0)].into_iter().collect();

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
    let initial_temp_map: HashMap<u32, f64> = [
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

    let initial_temp_map: HashMap<u32, f64> = [(25, 600.0)].into_iter().collect();

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

    let initial_temp_map: HashMap<u32, f64> = [(56, 473.0)].into_iter().collect();

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

    let initial_temp_map: HashMap<u32, f64> = [(265, 473.0), (252, 473.0)].into_iter().collect();

    (
        parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map),
        results_path,
    )
}

pub fn test_plane_0_2() -> Result<()> {
    let name = "cilindro_mesh_prepo";
    let elements_path = format!("./models/{}_triangles.csv", name);
    let nodes_path = format!("./models/{}_verts.csv", name);
    let results_folder = format!("./models/{}_results", name);
    let results_file = format!("{}_results", name);
    let results_format = "csv".to_string();

    let initial_temp_map: HashMap<u32, f64> = [
        (85, 573.0),
        (126, 573.0),
        (125, 573.0),
        (83, 573.0),
        (61, 573.0),
        (77, 573.0),
        (115, 573.0),
        (86, 573.0),
        (131, 573.0),
    ]
    .into_iter()
    .collect();

    let problem = parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map);
    println!("{}", problem.elements.len());
    let simulation_time = 5000.0;
    let time_step = 1.0;
    let snap_time = simulation_time / 10.0;

    let solver = ExplicitSolver::new(&problem.elements);

    let points = solver.points().clone();

    let mut engine = FEMEngine::new(
        simulation_time,
        time_step,
        snap_time,
        Solver::Explicit(solver),
    );

    let temp_results = engine.run()?;

    println!("{:#?}", &temp_results.last());

    //Calculate the average temperature

    let mut sum = 0.0;
    let mut len = 0;
    let last = &temp_results.last();
    for temp in last {
        sum += temp.iter().sum::<f64>();
        len += temp.len();
    }
    let avg = sum / len as f64;

    println!("Average temperature: {}", avg);

    parser::fem_multiple_results_to_csv(
        results_folder.clone(),
        results_file.clone(),
        results_format,
        &temp_results,
    )?;

    parser::fem_multiple_results_to_vtk(
        results_folder,
        results_file,
        &points,
        &problem.elements,
        &temp_results,
        snap_time,
    )?;

    Ok(())
}

pub fn run_example() -> Result<()> {
    let (problem, results_path) = test_plane_medium();

    println!("{}", problem.elements.len());

    let simulation_time = 0.01;
    let time_step = 1e-2;

    let solver = ExplicitSolver::new(&problem.elements);

    let points = solver.points().clone();

    let mut engine = FEMEngine::new(
        simulation_time,
        time_step,
        time_step,
        Solver::Explicit(solver),
    );

    let temp_results = engine.run()?;

    println!("{}", temp_results.last().unwrap());

    parser::fem_results_to_vtk(
        results_path.clone(),
        &points,
        &problem.elements,
        &temp_results.last().ok_or(anyhow!("No result"))?.clone(),
    )?;

    parser::fem_results_to_csv(
        results_path,
        &temp_results.last().ok_or(anyhow!("No result"))?.clone(),
    )?;

    Ok(())
}

pub fn vtk_test() -> Result<()> {
    let fem_problem = parser::fem_problem_from_vtk(
        "mesh4.vtk".to_string(),
        "mesh.json".to_string(),
        [].into_iter().collect(),
    );
    for element in fem_problem.elements.iter() {
        println!("{:#?}", element.f);
    }
    Ok(())
}

pub fn cilinder_vtk() -> Result<()> {
    let name = "cilinder_vtk";
    let results_folder = format!("./models/{}_results", name);
    let results_file = format!("{}_results", name);

    let problem = parser::fem_problem_from_vtk(
        "models/mesh.vtk".to_string(),
        "models/mesh_res.json".to_string(),
        [].into_iter().collect(),
    );

    let simulation_time = 1000000.0;
    let time_step = 1.0;
    let snap_time = simulation_time / 5000.0;

    let solver = ExplicitSolver::new(&problem.elements);

    let points = solver.points().clone();

    let mut engine = FEMEngine::new(
        simulation_time,
        time_step,
        snap_time,
        Solver::Explicit(solver),
    );

    let temp_results = engine.run()?;

    println!("{:#?}", &temp_results.last());

    parser::fem_multiple_results_to_vtk(
        results_folder,
        results_file,
        &points,
        &problem.elements,
        &temp_results,
        snap_time,
    )?;

    Ok(())
}
