use super::element::Element;
use super::engine::{FEMEngine, Solver};
use super::parser;
use super::results_writer::ResultsWriterWorker;
use super::{
    explicit_solver::ExplicitSolver, gpu_solver::GPUSolver, implicit_solver::ImplicitSolver,
};
use crate::err;
use anyhow::{Context, Result};

pub fn run_solver(directory_path: &str, solver_id: &str) -> Result<()> {
    let config = parser::parse_config(directory_path).with_context(|| "Couldn't parse config")?;

    let problem =
        parser::fem_problem_from_vtk(&config).with_context(|| "Couldn't load FEM problem")?;

    let solver = build_solver(&solver_id, &problem.elements, problem.parameters.time_step)
        .with_context(|| "Couldn't initialize FEM solver")?;

    let points = match &solver {
        Solver::Explicit(s) => s.points().clone(),
        Solver::Implicit(s) => s.points().clone(),
        Solver::GPU(s) => s.points().clone(),
    };

    let snapshot_period = problem.parameters.snapshot_period;

    let mut writer = ResultsWriterWorker::new(config, points, problem.elements, snapshot_period);

    FEMEngine::new(
        problem.parameters,
        problem.orbit_manager,
        &mut writer,
        solver,
    )
    .with_context(|| "Couldn't start a FEM Engine")?
    .run()
    .with_context(|| "Couldn't run the FEM Engine")?;

    writer.finish()?;

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
