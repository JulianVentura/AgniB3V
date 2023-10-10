use super::element::Element;
use super::structures::Vector;
use super::{explicit_solver::ExplicitSolver, implicit_solver::ImplicitSolver};
use anyhow::Result;

//TODO: Check how much slower the solver gets if we use a dyn (dynamic dispatch) over the Solver
//object
pub enum Solver {
    Explicit(ExplicitSolver),
    Implicit(ImplicitSolver),
}

pub struct FEMEngine {
    simulation_time: f64,
    time_step: f64,
    snapshot_period: f64,
    solver: Solver,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct FEMProblem {
    pub elements: Vec<Element>,
    pub simulation_time: f64,
    pub time_step: f64,
    pub snapshot_period: f64,
}

impl FEMEngine {
    pub fn new(simulation_time: f64, time_step: f64, snapshot_period: f64, solver: Solver) -> Self {
        //TODO add error handling
        if time_step > snapshot_period {
            panic!("Snapshot period cannot be smaller than time step");
        }

        if !Self::is_multiple(simulation_time, snapshot_period) {
            panic!("Snapshot period must be multiple of simulation time");
        }

        FEMEngine {
            simulation_time,
            time_step,
            snapshot_period,
            solver,
        }
    }

    pub fn run(&mut self) -> Result<Vec<Vector>> {
        let mut temp_results = Vec::new();

        let steps = (self.simulation_time / self.time_step) as u32;
        let snapshot_period = (self.snapshot_period / self.time_step) as u32;

        println!("Running for {steps} steps");

        for step in 0..steps {
            if step % snapshot_period == 0 {
                let temp = match &self.solver {
                    Solver::Explicit(s) => s.temperature(),
                    Solver::Implicit(s) => s.temperature(),
                };
                temp_results.push(temp);
            }
            match &mut self.solver {
                Solver::Explicit(s) => s.step(self.time_step as f32),
                Solver::Implicit(s) => s.step(),
            };
        }

        let temp = match &self.solver {
            Solver::Explicit(s) => s.temperature(),
            Solver::Implicit(s) => s.temperature(),
        };

        temp_results.push(temp);

        Ok(temp_results)
    }

    fn is_multiple(dividend: f64, divisor: f64) -> bool {
        (dividend / divisor).fract().abs() < 1e-12
    }
}
