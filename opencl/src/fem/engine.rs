use super::constants::EARTH_RADIOUS;
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
    eclipse_fraction: f64,
    orbit_period: f64,
    solver: Solver,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct FEMProblem {
    pub elements: Vec<Element>,
    pub simulation_time: f64,
    pub time_step: f64,
    pub snapshot_period: f64,
    pub betha: f64,
}

impl FEMEngine {
    pub fn new(
        simulation_time: f64,
        time_step: f64,
        snapshot_period: f64,
        altitude: f64,
        orbit_period: f64,
        betha: f64,
        solver: Solver,
    ) -> Self {
        //TODO add error handling
        if time_step > snapshot_period {
            panic!("Snapshot period cannot be smaller than time step");
        }

        if !Self::is_multiple(simulation_time, snapshot_period) {
            panic!("Snapshot period must be multiple of simulation time");
        }

        let eclipse_fraction = Self::calculate_eclipse_fraction(altitude, betha);

        println!("Eclipse fraction: {}", eclipse_fraction);

        FEMEngine {
            simulation_time,
            time_step,
            snapshot_period,
            eclipse_fraction,
            orbit_period,
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
            let is_in_eclipse = time as u32 % (self.orbit_period as u32)
                < (self.orbit_period * self.eclipse_fraction) as u32;
            match &mut self.solver {
                Solver::Explicit(s) => s.step(self.time_step, is_in_eclipse),
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

    fn calculate_eclipse_fraction(altitude: f64, betha: f64) -> f64 {
        let mut eclipse_fraction = 0.0;

        let betha_eclipse_begin = f64::asin(EARTH_RADIOUS / (EARTH_RADIOUS + altitude));

        if betha.to_radians() < betha_eclipse_begin {
            let upper = f64::sqrt(altitude * altitude + 2.0 * EARTH_RADIOUS * altitude);
            let lower = (EARTH_RADIOUS + altitude) * f64::cos(betha.to_radians());
            eclipse_fraction = 1.0 / 180.0_f64.to_radians() * f64::acos(upper / lower);
        }

        eclipse_fraction
    }
}
