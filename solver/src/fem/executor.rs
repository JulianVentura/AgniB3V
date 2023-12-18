use super::element::Element;
use super::engine::{FEMEngine, Solver};
use super::parser;
use super::results_writer::ResultsWriterWorker;
use super::{gpu_solver::GPUSolver, implicit_solver::ImplicitSolver};
use crate::err;
use anyhow::{Context, Result};

/// The `run_solver` function takes a directory path and solver ID as input, parses a configuration
/// file, builds a solver, initializes a FEM engine, runs the engine, and writes the results to a file.
///
/// Arguments:
///
/// * `directory_path`: The `directory_path` parameter is a string that represents the path to the
/// directory where the configuration files and input data are located.
/// * `solver_id`: The `solver_id` parameter is a string that represents the identifier of the solver to
/// be used. It is used to determine which type of solver to build and initialize.
///
/// Returns:
///
/// The function `run_solver` returns a `Result` with the unit type `()` as the success value.
pub fn run_solver(directory_path: &str, solver_id: &str) -> Result<()> {
    let config = parser::parse_config(directory_path).with_context(|| "Couldn't parse config")?;

    let problem =
        parser::fem_problem_from_vtk(&config).with_context(|| "Couldn't load FEM problem")?;

    let solver = build_solver(&solver_id, &problem.elements, problem.parameters.time_step)
        .with_context(|| "Couldn't initialize FEM solver")?;

    let points = match &solver {
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

/// The function `build_solver` takes a solver ID, a vector of elements, and a time step as input, and
/// returns a solver based on the solver ID.
///
/// Arguments:
///
/// * `solver_id`: A string representing the type of solver to be built. It can be one of the following
/// values: "Implicit", or "GPU".
/// * `elements`: The `elements` parameter is a vector of `Element` objects. It represents the elements
/// that will be used in the solver.
/// * `time_step`: The `time_step` parameter represents the time interval between each iteration or time
/// step in the solver. It is a floating-point number that determines the granularity of the simulation.
/// Smaller time steps generally result in more accurate simulations but require more computational
/// resources.
///
/// Returns:
///
/// a `Result<Solver>`.
fn build_solver(solver_id: &str, elements: &Vec<Element>, time_step: f64) -> Result<Solver> {
    match solver_id {
        "Implicit" => Ok(Solver::Implicit(ImplicitSolver::new(elements, time_step)?)),
        "GPU" => Ok(Solver::GPU(GPUSolver::new(elements, time_step)?)),
        _ => err!("Solver not recognized"),
    }
}
