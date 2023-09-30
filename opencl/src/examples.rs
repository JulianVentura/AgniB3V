use std::collections::HashMap;

use anyhow::{anyhow, Result};

use super::fem::{element::Element, engine::FEMEngine, parser, point::Point, structures::Vector};

fn log_results(temp_results: Vec<Vector>, time_step: f32, verbose: bool) {
    if !verbose {
        return;
    }

    let mut step = 0.0;
    for temp in temp_results.iter() {
        let d = temp.data();
        println!(
            "Time: {:.3} , Temp: [{:.2}, {:.2}, {:.2}, {:.2}]",
            (time_step * step),
            d[0],
            d[1],
            d[2],
            d[3]
        );
        step += time_step;
    }
}

pub fn test_square_only_temperature(verbose: bool) -> Result<()> {
    let p1 = Point::new(Vector::new([0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::new([1.0, 0.0, 0.0]), 283.0, 1, 0);
    let p3 = Point::new(Vector::new([1.0, 1.0, 0.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::new([0.0, 1.0, 0.0]), 273.0, 3, 0);

    //Alumium
    let conductivity = 237.0;
    let density = 2700.0;
    let specific_heat = 900.0;
    let thickness = 0.01;

    let e1 = Element::new(
        p1.clone(),
        p2.clone(),
        p3.clone(),
        conductivity,
        density,
        specific_heat,
        thickness,
        0.0,
    );
    let e2 = Element::new(
        p1.clone(),
        p3.clone(),
        p4.clone(),
        conductivity,
        density,
        specific_heat,
        thickness,
        0.0,
    );

    let time_step = 1.0;
    let time_res = 1.0;
    let simulation_time = 20.0;
    let mut engine = FEMEngine::new(simulation_time, time_step, vec![e1, e2], time_res);

    let temp_results = engine.run()?;

    log_results(temp_results, time_step, verbose);

    Ok(())
}

pub fn test_square_only_heat(verbose: bool) -> Result<()> {
    let p1 = Point::new(Vector::new([0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::new([1.0, 0.0, 0.0]), 273.0, 1, 0);
    let p3 = Point::new(Vector::new([0.0, 1.0, 0.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::new([1.0, 1.0, 0.0]), 273.0, 3, 0);

    //Alumium
    let conductivity = 237.0;
    let density = 2700.0;
    let specific_heat = 900.0;
    let thickness = 0.1;

    let e1 = Element::new(
        p1.clone(),
        p2.clone(),
        p3.clone(),
        conductivity,
        density,
        specific_heat,
        thickness,
        1000.0,
    );
    let e2 = Element::new(
        p2.clone(),
        p4.clone(),
        p3.clone(),
        conductivity,
        density,
        specific_heat,
        thickness,
        1000.0,
    );

    let time_step = 10.0;
    let time_res = 10.0;
    let simulation_time = 600.0;
    let mut engine = FEMEngine::new(simulation_time, time_step, vec![e1, e2], time_res);

    let temp_results = engine.run()?;

    log_results(temp_results, time_step, verbose);

    Ok(())
}

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
