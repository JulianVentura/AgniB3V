use super::structures::Vector;
use super::{
    explicit_solver::ExplicitSolver, gpu_solver::GPUSolver, implicit_solver::ImplicitSolver,
};
use anyhow::Result;

//TODO: Check how much slower the solver gets if we use a dyn (dynamic dispatch) over the Solver
//object
pub enum Solver {
    Explicit(ExplicitSolver),
    Implicit(ImplicitSolver),
    GPU(GPUSolver),
}

pub struct FEMEngine {
    simulation_time: f64,
    time_step: f64,
    snapshot_period: f64,
    orbit_parameters: FEMOrbitParameters,
    solver: Solver,
    results: Vec<Vector>,
    f_index: usize,
}

#[derive(Debug)]
pub struct FEMOrbitParameters {
    pub betha: f64,
    pub orbit_period: f64,
    pub orbit_divisions: Vec<f64>,
    pub eclipse_start: f64,
    pub eclipse_end: f64,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct FEMParameters {
    pub simulation_time: f64,
    pub time_step: f64,
    pub snapshot_period: f64,
    pub orbit: FEMOrbitParameters,
}

impl FEMEngine {
    pub fn new(params: FEMParameters, solver: Solver) -> Self {
        //TODO add error handling
        if params.time_step > params.snapshot_period {
            panic!("Snapshot period cannot be smaller than time step");
        }

        if !Self::is_multiple(params.simulation_time, params.snapshot_period) {
            panic!("Snapshot period must be multiple of simulation time");
        }

        let steps = (params.simulation_time / params.time_step) as usize;
        let snapshot_step_period = (params.snapshot_period / params.time_step) as usize;

        let result_size = (steps / snapshot_step_period) as usize;

        let mut results = Vec::default();
        results.reserve(result_size);

        FEMEngine {
            simulation_time: params.simulation_time,
            time_step: params.time_step,
            snapshot_period: params.snapshot_period,
            orbit_parameters: params.orbit,
            solver,
            results,
            f_index: 0,
        }
    }

    pub fn run(&mut self) -> Result<Vec<Vector>> {
        let steps = (self.simulation_time / self.time_step) as usize;
        let snapshot_period = (self.snapshot_period / self.time_step) as usize;

        println!("Running for {steps} steps");

        let mut step: usize = 0;

        while step < steps {
            self.save_results(step, snapshot_period)?;
            self.update_f(step)?;
            self.execute_solver()?;
            step += 1;
        }

        self.save_results(step, snapshot_period)?;

        //TODO: Optimize this clone
        Ok(self.results.clone())
    }

    fn update_f(&mut self, step: usize) -> Result<()> {
        let time = step as f64 * self.time_step;
        let orbit_time = time % (self.orbit_parameters.orbit_period);
        let in_eclipse = self.is_in_eclipse(orbit_time);

        self.update_f_index(orbit_time);

        match &mut self.solver {
            Solver::Explicit(s) => s.update_f(self.f_index, in_eclipse)?,
            Solver::Implicit(s) => s.update_f(self.f_index, in_eclipse)?,
            Solver::GPU(s) => s.update_f(self.f_index, in_eclipse)?,
        };

        Ok(())
    }

    fn execute_solver(&mut self) -> Result<()> {
        match &mut self.solver {
            Solver::Explicit(s) => s.step()?,
            Solver::Implicit(s) => s.step()?,
            Solver::GPU(s) => s.step()?,
        };

        Ok(())
    }

    fn save_results(&mut self, current_step: usize, snapshot_period: usize) -> Result<()> {
        //TODO: Instead of storing results to memory, we should go to disk directly
        if current_step % snapshot_period == 0 {
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

    fn is_in_eclipse(&self, time: f64) -> bool {
        let start = self.orbit_parameters.eclipse_start;
        let end = self.orbit_parameters.eclipse_end;
        if start <= end {
            return time >= start && time <= end;
        } else {
            return time <= end || time >= start;
        }
    }

    fn update_f_index(&mut self, orbit_time: f64) {
        let orbit_divisions = &self.orbit_parameters.orbit_divisions;
        let f_index = self.f_index;
        let next = (f_index + 1) % orbit_divisions.len();
        let next_start = orbit_divisions[next];
        if next == 0 {
            if orbit_time >= orbit_divisions[f_index] {
                return;
            } else {
                self.f_index = 0;
                self.update_f_index(orbit_time);
                return;
            }
        }
        if orbit_time >= next_start || orbit_time < orbit_divisions[f_index] {
            self.f_index = next;
            self.update_f_index(orbit_time);
            return;
        } else {
            return;
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::fem::engine::Solver;

    use crate::fem::engine::FEMEngine;
    use crate::fem::engine::FEMOrbitParameters;
    use crate::fem::explicit_solver::ExplicitSolver;

    fn create_fem_engine(start: f64, end: f64, orbit_divisions: Vec<f64>) -> FEMEngine {
        let orbit = FEMOrbitParameters {
            betha: 0.0,
            orbit_period: 6000.0,
            eclipse_start: start,
            eclipse_end: end,
            orbit_divisions: orbit_divisions,
        };
        let solver = Solver::Explicit(ExplicitSolver::new(&vec![], 0.0));
        FEMEngine {
            simulation_time: 1.0,
            time_step: 1.0,
            snapshot_period: 1.0,
            orbit_parameters: orbit,
            solver: solver,
            results: vec![],
            f_index: 0,
        }
    }

    #[test]
    fn test_is_in_eclipse_1() {
        let start = 1000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 1500.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_2() {
        let start = 1000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 500.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_3() {
        let start = 1000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 2500.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_4() {
        let start = 1000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 2000.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_5() {
        let start = 1000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 1000.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_6() {
        let start = 3000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 2500.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_7() {
        let start = 3000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 1500.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_8() {
        let start = 3000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 3500.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_9() {
        let start = 3000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 3000.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_10() {
        let start = 3000.0;
        let end = 2000.0;
        let engine = create_fem_engine(start, end, vec![0.0]);
        let time = 2000.0;
        let is_in_eclipse = engine.is_in_eclipse(time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_update_f_index_1() {
        let orbit_time = 5.0;
        let f_index = 0;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 0;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_2() {
        let orbit_time = 11.0;
        let f_index = 0;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 1;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_3() {
        let orbit_time = 12.0;
        let f_index = 1;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 1;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_4() {
        let orbit_time = 21.0;
        let f_index = 1;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 2;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_5() {
        let orbit_time = 25.0;
        let f_index = 2;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 2;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_6() {
        let orbit_time = 3.0;
        let f_index = 2;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 0;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_7() {
        let orbit_time = 25.0;
        let f_index = 0;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 2;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_8() {
        let orbit_time = 15.0;
        let f_index = 2;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 1;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_9() {
        let orbit_time = 45.0;
        let f_index = 1;
        let orbit_divisions = vec![0.0, 10.0, 20.0, 30.0, 40.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 4;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_10() {
        let orbit_time = 25.0;
        let f_index = 3;
        let orbit_divisions = vec![0.0, 10.0, 20.0, 30.0, 40.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);

        let actual_f_index = 2;

        assert_eq!(engine.f_index, actual_f_index);
    }

    #[test]
    fn test_update_f_index_11() {
        let orbit_time = 5.0;
        let f_index = 2;
        let orbit_divisions = vec![0.0, 10.0, 20.0, 30.0, 40.0];

        let mut engine = create_fem_engine(1000.0, 2000.0, orbit_divisions);
        engine.f_index = f_index;
        engine.update_f_index(orbit_time);
        let actual_f_index = 0;

        assert_eq!(engine.f_index, actual_f_index);
    }
}
