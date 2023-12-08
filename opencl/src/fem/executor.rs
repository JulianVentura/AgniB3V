use super::engine::{FEMEngine, Solver};
use super::parser;
use super::{
    explicit_solver::ExplicitSolver, gpu_solver::GPUSolver, implicit_solver::ImplicitSolver,
};
use anyhow::Result;

pub fn run_solver(directory_path: &String, method: &String) -> Result<()> {
    let config = parser::parse_config(directory_path);

    let problem = parser::fem_problem_from_vtk(
        config.vtk_path.to_string(),
        config.materials_path.to_string(),
        config.view_factors_path.to_string(),
    );

    let solver = match method.as_str() {
        "Explicit" => Solver::Explicit(ExplicitSolver::new(
            &problem.elements,
            problem.parameters.time_step,
        )),
        "Implicit" => Solver::Implicit(ImplicitSolver::new(
            &problem.elements,
            problem.parameters.time_step,
        )),
        "GPU" => Solver::GPU(GPUSolver::new(
            &problem.elements,
            problem.parameters.time_step,
        )),
        _ => panic!("Solver not recognized"),
    };

    let points = match &solver {
        Solver::Explicit(s) => s.points().clone(),
        Solver::Implicit(s) => s.points().clone(),
        Solver::GPU(s) => s.points().clone(),
    };

    let snapshot_period = problem.parameters.snapshot_period;

    let mut engine = FEMEngine::new(problem.parameters, solver);

    let temp_results = engine.run()?;

    println!("{:#?}", &temp_results.last());

    parser::fem_result_to_vtk(
        config.results_path,
        config.results_name,
        &points,
        &problem.elements,
        &temp_results,
        snapshot_period,
    )?;

    Ok(())
}
