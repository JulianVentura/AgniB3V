use super::engine::{FEMEngine, FEMParameters, Solver};
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

    //TODO: Change this hardcoded parameters
    let simulation_time = 30000.0;
    let time_step = 1.0;
    let snapshot_period = simulation_time / 5000.0;

    let p = FEMParameters {
        simulation_time,
        time_step,
        snapshot_period,
        orbit: problem.parameters.orbit,
    };

    let solver = ImplicitSolver::new(&problem.elements, time_step); //TODO: add option to choose solver

    let points = solver.points().clone();

    let mut engine = FEMEngine::new(p, Solver::Implicit(solver));

    let temp_results = engine.run()?;

    println!("{:#?}", &temp_results.last());

    parser::fem_result_to_vtk(
        results_folder,
        results_file,
        &points,
        &problem.elements,
        &temp_results,
        snapshot_period,
    )?;

    Ok(())
}
