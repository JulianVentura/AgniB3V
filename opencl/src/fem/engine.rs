use super::constants::EARTH_RADIOUS;
use super::structures::Vector;
use super::{explicit_solver::ExplicitSolver, implicit_solver::ImplicitSolver};
use anyhow::Result;
use nalgebra::SimdBool;

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
    orbit_parameters: FEMOrbitParameters,
    solver: Solver,
}

#[derive(Debug)]
pub struct FEMOrbitParameters {
    pub betha: f64,
    pub altitude: f64,
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

        FEMEngine {
            simulation_time: params.simulation_time,
            time_step: params.time_step,
            snapshot_period: params.snapshot_period,
            orbit_parameters: params.orbit,
            solver,
        }
    }

    pub fn run(&mut self) -> Result<Vec<Vector>> {
        let mut temp_results = Vec::new();

        let steps = (self.simulation_time / self.time_step) as u32;
        let snapshot_period = (self.snapshot_period / self.time_step) as u32;

        println!("Running for {steps} steps");

        let mut f_index = 0;
        for step in 0..steps {
            if step % snapshot_period == 0 {
                let temp = match &self.solver {
                    Solver::Explicit(s) => s.temperature(),
                    Solver::Implicit(s) => s.temperature(),
                };
                temp_results.push(temp);
            }

            let time = step as f64 * self.time_step;
            let orbit_time = time % (self.orbit_parameters.orbit_period);
            let is_in_eclipse = Self::is_in_eclipse(
                self.orbit_parameters.eclipse_start,
                self.orbit_parameters.eclipse_end,
                orbit_time,
            );

            f_index = Self::calculate_f_index(
                orbit_time,
                f_index,
                &self.orbit_parameters.orbit_divisions,
            );

            match &mut self.solver {
                Solver::Explicit(s) => s.step(self.time_step, is_in_eclipse, f_index),
                Solver::Implicit(s) => s.step(is_in_eclipse, f_index),
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

    fn is_in_eclipse(start: f64, end: f64, time: f64) -> bool {
        if start <= end {
            return time >= start && time <= end;
        } else {
            return time <= end || time >= start;
        }
    }

    fn calculate_f_index(orbit_time: f64, f_index: usize, orbit_divisions: &Vec<f64>) -> usize {
        let next = (f_index + 1) % orbit_divisions.len();
        let next_start = orbit_divisions[next];
        if next == 0 {
            if orbit_time >= orbit_divisions[f_index] {
                return f_index;
            } else {
                return Self::calculate_f_index(orbit_time, next, orbit_divisions);
            }
        }
        if orbit_time >= next_start {
            return Self::calculate_f_index(orbit_time, next, orbit_divisions);
        } else {
            return f_index;
        }
    }
}

#[cfg(test)]
mod tests {
    use crate::fem::engine::FEMEngine;

    fn assert_float_eq(value_1: f64, value_2: f64, precision: f64) {
        assert!(
            (value_1 - value_2).abs() < precision,
            "value1 {} != {}",
            value_1,
            value_2
        );
    }

    #[test]
    fn test_is_in_eclipse_1() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 1500.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_2() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 500.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_3() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 2500.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_4() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 2000.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_5() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 1000.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_6() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 2500.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_7() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 1500.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_8() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 3500.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_9() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 3000.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_10() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 2000.0;
        let is_in_eclipse = FEMEngine::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_calculate_f_index_1() {
        let orbit_time = 5.0;
        let f_index = 0;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 0;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_2() {
        let orbit_time = 11.0;
        let f_index = 0;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 1;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_3() {
        let orbit_time = 12.0;
        let f_index = 1;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 1;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_4() {
        let orbit_time = 21.0;
        let f_index = 1;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 2;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_5() {
        let orbit_time = 25.0;
        let f_index = 2;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 2;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_6() {
        let orbit_time = 3.0;
        let f_index = 2;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 0;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_7() {
        let orbit_time = 25.0;
        let f_index = 0;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 2;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_8() {
        let orbit_time = 15.0;
        let f_index = 2;
        let orbit_divisions = vec![0.0, 10.0, 20.0];

        let f_index = FEMEngine::calculate_f_index(orbit_time, f_index, &orbit_divisions);

        let actual_f_index = 1;

        assert_eq!(f_index, actual_f_index);
    }
}
