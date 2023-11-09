use super::engine::{FEMEngine, Solver};
use super::implicit_solver::ImplicitSolver;

use super::parser;

use super::explicit_solver::ExplicitSolver;
use anyhow::Result;

pub fn run_solver(config_path: &String) -> Result<()> {
    let config = parser::parse_config(config_path);
    let results_folder = format!("{}/{}_results", config.results_path, config.results_name);
    let results_file = format!("{}_results", config.results_name);

    let problem = parser::fem_problem_from_vtk(
        config.vtk_path.to_string(),
        config.materials_path.to_string(),
        config.view_factors_path.to_string(),
    );

    let solver = match config.solver.as_str() {
        "Explicit" => Solver::Explicit(ExplicitSolver::new(&problem.elements)),
        "Implicit" => Solver::Implicit(ImplicitSolver::new(
            &problem.elements,
            problem.parameters.time_step,
        )),
        _ => panic!("Solver not recognized"),
    };

    let points = match &solver {
        Solver::Explicit(s) => s.points().clone(),
        Solver::Implicit(s) => s.points().clone(),
    };

    let snapshot_period = problem.parameters.snapshot_period;

    let mut engine = FEMEngine::new(problem.parameters, solver);

    let temp_results = engine.run_gpu()?;

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
