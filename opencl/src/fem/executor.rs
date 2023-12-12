use super::element::Element;
use super::engine::{FEMEngine, Solver};
use super::parser;
use super::{
    explicit_solver::ExplicitSolver, gpu_solver::GPUSolver, implicit_solver::ImplicitSolver,
};
use crate::err;
use anyhow::{Context, Result};

pub fn run_solver(config_path: &String) -> Result<()> {
    let config = parser::parse_config(config_path).with_context(|| "Couldn't parse config")?;

    let problem =
        parser::fem_problem_from_vtk(&config).with_context(|| "Couldn't load FEM problem")?;

    let solver = build_solver(
        &config.solver,
        &problem.elements,
        problem.parameters.time_step,
    )
    .with_context(|| "Couldn't initialize FEM solver")?;

    let points = match &solver {
        Solver::Explicit(s) => s.points().clone(),
        Solver::Implicit(s) => s.points().clone(),
        Solver::GPU(s) => s.points().clone(),
    };

    let snapshot_period = problem.parameters.snapshot_period;

    let mut engine = FEMEngine::new(problem.parameters, problem.orbit_manager, solver)
        .with_context(|| "Couldn't start a FEM Engine")?;

    let temp_results = engine
        .run()
        .with_context(|| "Couldn't run the FEM Engine")?;

    parser::fem_result_to_vtk(
        &config,
        &points,
        &problem.elements,
        &temp_results,
        snapshot_period,
    )?;

    Ok(())
}

fn build_solver(solver_id: &str, elements: &Vec<Element>, time_step: f64) -> Result<Solver> {
    match solver_id {
        "Explicit" => Ok(Solver::Explicit(ExplicitSolver::new(elements, time_step)?)),
        "Implicit" => Ok(Solver::Implicit(ImplicitSolver::new(elements, time_step)?)),
        "GPU" => Ok(Solver::GPU(GPUSolver::new(elements, time_step)?)),
        _ => err!("Solver not recognized"),
    }
}
