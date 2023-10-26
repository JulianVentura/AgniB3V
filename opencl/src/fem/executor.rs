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

    let solver = ImplicitSolver::new(&problem.elements, problem.parameters.time_step); //TODO: add option to choose solver

    let points = solver.points().clone();

    let snapshot_period = problem.parameters.snapshot_period;

    let mut engine = FEMEngine::new(problem.parameters, Solver::Implicit(solver));

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
