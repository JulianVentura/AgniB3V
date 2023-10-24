use super::engine::{FEMEngine, Solver};
use super::implicit_solver::ImplicitSolver;
use super::parser;

use anyhow::Result;

pub fn run_solver(vtk_path: &String, json_path: &String, results_name: &String) -> Result<()> {
    let results_folder = format!("./models/{}_results", results_name); //TODO: See if this is ok, or if we want to let the user choose this
    let results_file = format!("{}_results", results_name);

    let problem = parser::fem_problem_from_vtk(
        vtk_path.to_string(),
        json_path.to_string(),
        [].into_iter().collect(),
    );

    let simulation_time = 30000.0; //TODO: Add to json or where applicable
    let time_step = 1.0;
    let snap_time = simulation_time / 5000.0;

    let solver = ImplicitSolver::new(&problem.elements, time_step); //TODO: add option to choose solver

    let points = solver.points().clone();

    let mut engine = FEMEngine::new(
        simulation_time,
        time_step,
        snap_time,
        problem.orbit_parameters,
        Solver::Implicit(solver),
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
