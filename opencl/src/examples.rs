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
    let elements_path = "./models/shell_mesh_triangles.csv".to_string();
    let nodes_path = "./models/shell_mesh_verts.csv".to_string();
    let results_folder = "./models/shell_mesh_results".to_string();
    let results_file = "shell_mesh_results".to_string();
    let results_format = "csv".to_string();

    let initial_temp_map: HashMap<u32, f32> = [
        (79, 573.0),
        (145, 573.0),
        (144, 573.0),
        (143, 573.0),
        (141, 573.0),
        (140, 573.0),
        (139, 573.0),
        (136, 573.0),
        (135, 573.0),
    ]
    .into_iter()
    .collect();

    let problem = parser::fem_problem_from_csv(elements_path, nodes_path, initial_temp_map);

    let simulation_time = 3000.0;
    let time_step = 1.0;
    let snap_time = simulation_time / 10.0;

    let mut engine = FEMEngine::new(simulation_time, time_step, problem.elements, snap_time);

    // engine.m_inverse_k.data().iter().for_each(|value| {
    //     if value.is_nan() || value.abs() == f32::INFINITY {
    //         println!("{:#?}", value);
    //     }
    // });
    // return Ok(());

    // println!("{:#?}", engine.m_inverse);
    // println!("{:#?}", engine.m_inverse_k);
    //
    //
    let temp_results = engine.run()?;

    for temp in &temp_results {
        println!("{:#?}", temp.data());
    }

    // println!("{:#?}", temp_results);

    println!("{:#?}", &temp_results.last());

    parser::fem_multiple_results_to_csv(
        results_folder,
        results_file,
        results_format,
        &temp_results,
    )?;

    Ok(())
}
