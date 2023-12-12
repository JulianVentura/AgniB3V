use crate::err;
use anyhow::Result;

use super::orbit_manager::OrbitManager;
use super::structures::Vector;
use super::{
    explicit_solver::ExplicitSolver, gpu_solver::GPUSolver, implicit_solver::ImplicitSolver,
};

//TODO: Check how much slower the solver gets if we use a dyn (dynamic dispatch) over the Solver
//object
pub enum Solver {
    Explicit(ExplicitSolver),
    Implicit(ImplicitSolver),
    GPU(GPUSolver),
}

pub struct FEMEngine {
    simulation_steps: usize,
    time_step: f64,
    snapshot_steps: usize,
    solver: Solver,
    orbit_manager: OrbitManager,
    results: Vec<Vector>,
    f_index: usize,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct FEMParameters {
    pub simulation_time: f64,
    pub time_step: f64,
    pub snapshot_period: f64,
}

impl FEMEngine {
    pub fn new(params: FEMParameters, orbit_manager: OrbitManager, solver: Solver) -> Result<Self> {
        if params.time_step > params.snapshot_period {
            err!("Snapshot period cannot be smaller than time step");
        }

        if !Self::is_multiple(params.simulation_time, params.snapshot_period) {
            err!("Snapshot period must be multiple of simulation time");
        }

        let simulation_steps = (params.simulation_time / params.time_step) as usize;
        let snapshot_steps = (params.snapshot_period / params.time_step) as usize;

        let result_size = (simulation_steps / snapshot_steps) as usize;

        let mut results = Vec::default();
        results.reserve(result_size);

        Ok(FEMEngine {
            simulation_steps,
            time_step: params.time_step,
            snapshot_steps,
            orbit_manager,
            solver,
            results,
            f_index: 0,
        })
    }

    pub fn run(&mut self) -> Result<Vec<Vector>> {
        println!("Running for {} steps", self.simulation_steps);

        let mut step: usize = 0;

        while step < self.simulation_steps {
            self.save_results(step)?;
            self.update_f(step)?;
            let simulated_steps = self.execute_solver(step)?;
            step += simulated_steps;
        }

        self.save_results(step)?;

        //TODO: Optimize this clone
        Ok(self.results.clone())
    }

    fn update_f(&mut self, step: usize) -> Result<()> {
        let time = step as f64 * self.time_step;
        let idx = self.orbit_manager.current_index(time);
        if idx == self.f_index {
            return Ok(());
        }

        self.f_index = idx;
        match &mut self.solver {
            Solver::Explicit(s) => s.update_f(self.f_index)?,
            Solver::Implicit(s) => s.update_f(self.f_index)?,
            Solver::GPU(s) => s.update_f(self.f_index)?,
        };

        Ok(())
    }

    fn calculate_iteration_steps(
        next_division_time: f64,
        snapshot_steps: usize,
        current_step: usize,
        time_step: f64,
    ) -> usize {
        let next_snap_steps = snapshot_steps - current_step % snapshot_steps;
        let next_division_steps = (next_division_time / time_step).ceil() as usize;

        usize::min(next_snap_steps, next_division_steps)
    }

    fn execute_solver(&mut self, current_step: usize) -> Result<usize> {
        let next_division_time = self
            .orbit_manager
            .time_to_next(current_step as f64 * self.time_step);

        let sim_steps = Self::calculate_iteration_steps(
            next_division_time,
            self.snapshot_steps,
            current_step,
            self.time_step,
        );

        match &mut self.solver {
            Solver::Explicit(s) => s.run_for(sim_steps)?,
            Solver::Implicit(s) => s.run_for(sim_steps)?,
            Solver::GPU(s) => s.run_for(sim_steps)?,
        };

        Ok(sim_steps)
    }

    fn save_results(&mut self, current_step: usize) -> Result<()> {
        //TODO: Instead of storing results to memory, we should go to disk directly
        if current_step % self.snapshot_steps == 0 {
            let temp = match &mut self.solver {
                Solver::Explicit(s) => s.temperature()?,
                Solver::Implicit(s) => s.temperature()?,
                Solver::GPU(s) => s.temperature()?,
            };
            self.results.push(temp.clone());
        }

        Ok(())
    }

    fn is_multiple(dividend: f64, divisor: f64) -> bool {
        (dividend / divisor).fract().abs() < 1e-12
    }
}

#[cfg(test)]
mod tests {
    use crate::fem::engine::FEMEngine;
    #[test]
    pub fn test_calculate_iteration_steps_1() {
        let next_division_time = 600.0;
        let snapshot_steps = 8;
        let current_step = 53;
        let time_step = 10.0;

        let expected_sim_step = 3;

        let sim_steps = FEMEngine::calculate_iteration_steps(
            next_division_time,
            snapshot_steps,
            current_step,
            time_step,
        );

        assert_eq!(sim_steps, expected_sim_step);
    }

    #[test]
    pub fn test_calculate_iteration_steps_2() {
        let next_division_time = 20.0;
        let snapshot_steps = 8;
        let current_step = 53;
        let time_step = 10.0;

        let expected_sim_step = 2;

        let sim_steps = FEMEngine::calculate_iteration_steps(
            next_division_time,
            snapshot_steps,
            current_step,
            time_step,
        );

        assert_eq!(sim_steps, expected_sim_step);
    }

    #[test]
    pub fn test_calculate_iteration_steps_3() {
        let next_division_time = 30.0;
        let snapshot_steps = 8;
        let current_step = 53;
        let time_step = 10.0;

        let expected_sim_step = 3;

        let sim_steps = FEMEngine::calculate_iteration_steps(
            next_division_time,
            snapshot_steps,
            current_step,
            time_step,
        );

        assert_eq!(sim_steps, expected_sim_step);
    }

    #[test]
    pub fn test_calculate_iteration_steps_4() {
        let next_division_time = 11.0;
        let snapshot_steps = 8;
        let current_step = 53;
        let time_step = 10.0;

        let expected_sim_step = 2;

        let sim_steps = FEMEngine::calculate_iteration_steps(
            next_division_time,
            snapshot_steps,
            current_step,
            time_step,
        );

        assert_eq!(sim_steps, expected_sim_step);
    }
}
