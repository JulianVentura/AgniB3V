use super::constants::EARTH_RADIOUS;
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
    eclipse_fraction: f64,
    orbit_period: f64,
    orbit_divisions: u32,
    solver: Solver,
}

#[derive(Debug)]
pub struct FEMOrbitParameters {
    pub betha: f64,
    pub altitude: f64,
    pub orbit_period: f64,
    pub orbit_divisions: u32,
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

        let eclipse_fraction =
            Self::calculate_eclipse_fraction(params.orbit.altitude, params.orbit.betha);

        println!("Eclipse fraction: {}", eclipse_fraction);

        FEMEngine {
            simulation_time: params.simulation_time,
            time_step: params.time_step,
            snapshot_period: params.snapshot_period,
            eclipse_fraction,
            orbit_period: params.orbit.orbit_period,
            orbit_divisions: params.orbit.orbit_divisions,
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

            let time = step as f64 * self.time_step;
            let orbit_time = time % (self.orbit_period);
            let is_in_eclipse = orbit_time > (self.orbit_period * (1.0 - self.eclipse_fraction));

            let f_index =
                Self::calculate_f_index(orbit_time, self.orbit_period, self.orbit_divisions);

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

    fn calculate_eclipse_fraction(altitude: f64, betha: f64) -> f64 {
        let mut eclipse_fraction = 0.0;

        let betha_eclipse_begin = f64::asin(EARTH_RADIOUS / (EARTH_RADIOUS + altitude));

        if betha < betha_eclipse_begin {
            let upper = f64::sqrt(altitude * altitude + 2.0 * EARTH_RADIOUS * altitude);
            let lower = (EARTH_RADIOUS + altitude) * f64::cos(betha);
            eclipse_fraction = 1.0 / 180.0_f64.to_radians() * f64::acos(upper / lower);
        }

        eclipse_fraction
    }

    fn calculate_f_index(orbit_time: f64, orbit_period: f64, orbit_divisions: u32) -> usize {
        let orbit_division_time = orbit_period / orbit_divisions as f64;

        (orbit_time / orbit_division_time) as usize
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
    fn test_calculate_eclipse_fraction_1() {
        let altitude = 2000.0;
        let betha = 0.1;

        let eclipse_fraction = FEMEngine::calculate_eclipse_fraction(altitude, betha);

        let actual_eclipse_fraction = 0.27;
        let precision = 0.01;

        assert_float_eq(eclipse_fraction, actual_eclipse_fraction, precision);
    }

    #[test]
    fn test_calculate_eclipse_fraction_2() {
        let altitude = 2000.0;
        let betha = 0.9;

        let eclipse_fraction = FEMEngine::calculate_eclipse_fraction(altitude, betha);

        let actual_eclipse_fraction = 0.0;
        let precision = 0.01;

        assert_float_eq(eclipse_fraction, actual_eclipse_fraction, precision);
    }

    #[test]
    fn test_calculate_eclipse_fraction_3() {
        let altitude = 1000.0;
        let betha = 0.9;

        let eclipse_fraction = FEMEngine::calculate_eclipse_fraction(altitude, betha);

        let actual_eclipse_fraction = 0.2;
        let precision = 0.01;

        assert_float_eq(eclipse_fraction, actual_eclipse_fraction, precision);
    }

    #[test]
    fn test_calculate_eclipse_fraction_4() {
        let altitude = 10000.0;
        let betha = 0.3;

        let eclipse_fraction = FEMEngine::calculate_eclipse_fraction(altitude, betha);

        let actual_eclipse_fraction = 0.09;
        let precision = 0.01;

        assert_float_eq(eclipse_fraction, actual_eclipse_fraction, precision);
    }

    #[test]
    fn test_calculate_eclipse_fraction_5() {
        let altitude = 1.0;
        let betha = 0.1;

        let eclipse_fraction = FEMEngine::calculate_eclipse_fraction(altitude, betha);

        let actual_eclipse_fraction = 0.49;
        let precision = 0.01;

        assert_float_eq(eclipse_fraction, actual_eclipse_fraction, precision);
    }

    #[test]
    fn test_calculate_f_index_1() {
        let orbit_time = 0.0;
        let orbit_period = 100.0;
        let orbit_divisions = 10;

        let f_index = FEMEngine::calculate_f_index(orbit_time, orbit_period, orbit_divisions);

        let actual_f_index = 0;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_2() {
        let orbit_time = 11.0;
        let orbit_period = 100.0;
        let orbit_divisions = 10;

        let f_index = FEMEngine::calculate_f_index(orbit_time, orbit_period, orbit_divisions);

        let actual_f_index = 1;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_3() {
        let orbit_time = 25.0;
        let orbit_period = 100.0;
        let orbit_divisions = 10;

        let f_index = FEMEngine::calculate_f_index(orbit_time, orbit_period, orbit_divisions);

        let actual_f_index = 2;

        assert_eq!(f_index, actual_f_index);
    }

    #[test]
    fn test_calculate_f_index_4() {
        let orbit_time = 20.0;
        let orbit_period = 30.0;
        let orbit_divisions = 5;

        let f_index = FEMEngine::calculate_f_index(orbit_time, orbit_period, orbit_divisions);

        let actual_f_index = 4;

        assert_eq!(f_index, actual_f_index);
    }
}
