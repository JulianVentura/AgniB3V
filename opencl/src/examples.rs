use std::collections::HashMap;

use anyhow::{anyhow, Result};

use super::fem::{engine::FEMEngine, parser};

pub fn test_2d_plane() -> Result<()> {
    let elements_path = "./models/2D-plane_triangles.csv".to_string();
    let nodes_path = "./models/2D-plane_verts.csv".to_string();
    let results_path = "./models/2D-plane_results.csv".to_string();

    let initial_temp_map: HashMap<u32, f32> = [(0, 373.0), (3, 373.0)].into_iter().collect();

    let problem = parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map);

    let simulation_time = 10.0;
    let time_step = 1.0;

    let mut engine = FEMEngine::new(simulation_time, time_step, problem.elements, 10.0);

    let temp_results = engine.run()?;

    parser::fem_results_to_csv(
        results_path,
        &temp_results.last().ok_or(anyhow!("No result"))?.clone(),
    )?;

    Ok(())
}

pub fn test_non_tilted_3d_plane() -> Result<()> {
    // let elements_path = "./models/monkey_mesh_triangles.csv".to_string();
    // let nodes_path = "./models/monkey_mesh_verts.csv".to_string();
    // let results_path = "./models/monkey_mesh_results.csv".to_string();

    let elements_path = "./models/3D_plane_non_tilted_triangles.csv".to_string();
    let nodes_path = "./models/3D_plane_non_tilted_verts.csv".to_string();
    let results_path = "./models/3D_plane_non_tilted_results.csv".to_string();

    // let elements_path = "./models/3d-plane_triangles.csv".to_string();
    // let nodes_path = "./models/3d-plane_triangles.csv".to_string();
    // let results_path = "./models/3d-plane_results.csv".to_string();

    // let initial_temp_map: HashMap<u32, f32> = [
    //     (2, 373.0),
    //     (22, 373.0),
    //     (5, 373.0),
    //     (0, 373.0),
    //     (20, 373.0),
    //     (7, 373.0),
    //     // (112, 373.0),
    //     // (5, 373.0),
    // ]
    // .into_iter()
    // .collect();

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

    // let initial_temp_map: HashMap<u32, f32> = [(575, 573.0), (633, 573.0)].into_iter().collect();

    let problem = parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map);
    println!("{}", problem.elements.len());

    let simulation_time = 1.0;
    let time_step = 1e-4;

    let mut engine = FEMEngine::new(simulation_time, time_step, problem.elements, time_step);

    let temp_results = engine.run()?;

    println!("{}", temp_results.last().unwrap());

    parser::fem_results_to_csv(
        results_path,
        &temp_results.last().ok_or(anyhow!("No result"))?.clone(),
    )?;

    Ok(())
}
