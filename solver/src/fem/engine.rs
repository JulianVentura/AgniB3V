use crate::err;
use anyhow::Result;

use super::orbit_manager::OrbitManager;
use super::results_writer::ResultsWriterWorker;
use super::{gpu_solver::GPUSolver, implicit_solver::ImplicitSolver};

pub enum Solver {
    Implicit(ImplicitSolver),
    GPU(GPUSolver),
}

pub struct FEMEngine<'a> {
    simulation_steps: usize,
    time_step: f64,
    snapshot_steps: usize,
    solver: Solver,
    orbit_manager: OrbitManager,
    writer: &'a mut ResultsWriterWorker,
    f_index: usize,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct FEMParameters {
    pub simulation_time: f64,
    pub time_step: f64,
    pub snapshot_period: f64,
}

impl<'a> FEMEngine<'a> {
    pub fn new(
        params: FEMParameters,
        orbit_manager: OrbitManager,
        writer: &'a mut ResultsWriterWorker,
        solver: Solver,
    ) -> Result<Self> {
        if params.time_step > params.snapshot_period {
            err!("Snapshot period cannot be smaller than time step");
        }

        if !Self::is_multiple(params.simulation_time, params.snapshot_period) {
            err!("Simulation time must be a multiple of snapshot period");
        }

        if !Self::is_multiple(params.snapshot_period, params.time_step) {
            err!("Snapshot period must be a multiple of time step");
        }

        let simulation_steps = (params.simulation_time / params.time_step) as usize;
        let snapshot_steps = (params.snapshot_period / params.time_step) as usize;

        Ok(FEMEngine {
            simulation_steps,
            time_step: params.time_step,
            snapshot_steps,
            orbit_manager,
            writer,
            solver,
            f_index: 0,
        })
    }

    /// The `run` function runs a simulation for a specified number of steps, saving results at each
    /// step and updating the simulation state.
    ///
    /// Returns:
    ///
    /// The `run` function returns a `Result<()>`.
    pub fn run(&mut self) -> Result<()> {
        println!("Running for {} steps", self.simulation_steps);

        let mut step: usize = 0;

        while step < self.simulation_steps {
            self.save_results(step)?;
            self.update_f(step)?;
            let simulated_steps = self.execute_solver(step)?;
            step += simulated_steps;
        }

        self.save_results(step)?;

        Ok(())
    }

    /// The function `update_f` updates the value of `f_index` and calls the `update_f` method of the
    /// appropriate solver based on the current value of `f_index`.
    ///
    /// Arguments:
    ///
    /// * `step`: The `step` parameter represents the current step number in the simulation.
    ///
    /// Returns:
    ///
    /// The function `update_f` returns a `Result<()>`.
    fn update_f(&mut self, step: usize) -> Result<()> {
        let time = step as f64 * self.time_step;
        let idx = self.orbit_manager.current_index(time);
        if idx == self.f_index {
            return Ok(());
        }

        self.f_index = idx;
        match &mut self.solver {
            Solver::Implicit(s) => s.update_f(self.f_index)?,
            Solver::GPU(s) => s.update_f(self.f_index)?,
        };

        Ok(())
    }

    /// The function calculates the number of iteration steps needed based on the next division time,
    /// snapshot steps, current step, and time step.
    ///
    /// Arguments:
    ///
    /// * `next_division_time`: The `next_division_time` parameter represents the time at which the next
    /// division will occur.
    /// * `snapshot_steps`: The `snapshot_steps` parameter represents the number of steps between each
    /// snapshot. It determines how often a snapshot of the calculation is taken.
    /// * `current_step`: The `current_step` parameter represents the current iteration step in a loop
    /// or simulation. It is of type `usize`, which means it is an unsigned integer.
    /// * `time_step`: The `time_step` parameter represents the duration of each time step in the
    /// simulation. It is a floating-point number (f64) that indicates the length of time that each
    /// iteration of the simulation represents.
    ///
    /// Returns:
    ///
    /// The function `calculate_iteration_steps` returns a `usize` value.
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

    /// The function `execute_solver` runs a simulation for a specified number of steps using a specific
    /// solver algorithm.
    ///
    /// Arguments:
    ///
    /// * `current_step`: The `current_step` parameter represents the current iteration step in the
    /// simulation. It is of type `usize`, which means it is an unsigned integer.
    ///
    /// Returns:
    ///
    /// The function `execute_solver` returns a `Result<usize>`.
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
            Solver::Implicit(s) => s.run_for(sim_steps)?,
            Solver::GPU(s) => s.run_for(sim_steps)?,
        };

        Ok(sim_steps)
    }

    /// The function saves the temperature results at regular intervals during a simulation.
    ///
    /// Arguments:
    ///
    /// * `current_step`: The `current_step` parameter represents the current step or iteration in the
    /// process.
    ///
    /// Returns:
    ///
    /// The function `save_results` returns a `Result<()>`.
    fn save_results(&mut self, current_step: usize) -> Result<()> {
        if current_step % self.snapshot_steps == 0 {
            let temp = match &mut self.solver {
                Solver::Implicit(s) => s.temperature()?,
                Solver::GPU(s) => s.temperature()?,
            };
            self.writer.write_result(temp.clone())?;
        }

        Ok(())
    }

    /// The function checks if a given dividend is a multiple of a given divisor.
    ///
    /// Arguments:
    ///
    /// * `dividend`: The dividend is the number that is being divided. It is the number that is being
    /// divided by the divisor.
    /// * `divisor`: The divisor is the number that divides the dividend. It is the number that we want
    /// to check if it is a multiple of the dividend.
    ///
    /// Returns:
    ///
    /// a boolean value, indicating whether the dividend is a multiple of the divisor.
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
