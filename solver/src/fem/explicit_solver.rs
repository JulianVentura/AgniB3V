use super::solver;
use super::structures::{Matrix, Vector, LU};
use super::{element::Element, point::Point};
use anyhow::{Context, Result};

pub struct ExplicitSolver {
    pub m_lu: LU,
    pub k: Matrix,
    pub h: Matrix,
    f_const: Vec<Vector>,
    f_index: usize,
    temp: Vector,
    t_4: Vector,
    points: Vec<Point>,
    time_step: f64,
}

#[allow(dead_code)]
#[derive(Debug)]
pub struct FEMProblem {
    pub elements: Vec<Element>,
    pub simulation_time: f64,
    pub time_step: f64,
    pub snapshot_period: f64,
}

impl ExplicitSolver {
    pub fn new(elements: &Vec<Element>, time_step: f64) -> Result<Self> {
        let n_points = solver::calculate_number_of_points(elements);
        println!("Constructing global M matrix");
        let m = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.m);
        println!("Constructing global K matrix");
        let k = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.k);
        println!("Constructing global E matrix");
        let e = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.e);
        println!("Constructing global L matrix");
        let l = solver::construct_l_matrix(elements, n_points);
        println!("Constructing global flux vector");
        let f_const = solver::construct_global_vector_f_const_array(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);
        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f64>>());

        let h = l - e;

        let m_lu = m.lu();
        println!("Explicit Solver built successfully");

        Ok(ExplicitSolver {
            m_lu,
            k,
            h,
            f_const,
            time_step,
            f_index: 0,
            t_4: temp.clone(),
            temp,
            points,
        })
    }

    pub fn temperature(&mut self) -> Result<&Vector> {
        Ok(&self.temp)
    }

    pub fn points(&self) -> &Vec<Point> {
        &self.points
    }

    pub fn update_f(&mut self, f_index: usize) -> Result<()> {
        self.f_index = f_index;

        Ok(())
    }

    /// The `step` function calculates the temperature at the next time step based on a linear system of
    /// equations.
    ///
    /// Returns:
    ///
    /// a `Result<()>`.
    pub fn step(&mut self) -> Result<()> {
        solver::fourth_power(&self.temp, &mut self.t_4);

        let f = &self.h * &self.t_4 + &self.f_const[self.f_index];
        let b = f - &self.k * &self.temp;
        let x = &self
            .m_lu
            .solve(&b)
            .with_context(|| "Couldn't solve linear system")?;

        self.temp = self.time_step * x + &self.temp;

        Ok(())
    }

    /// The `run_for` function runs a given number of steps.
    ///
    /// Arguments:
    ///
    /// * `steps`: The `steps` parameter is of type `usize` and represents the number of steps to run
    /// the code for.
    ///
    /// Returns:
    ///
    /// The `run_for` function returns a `Result<()>`.
    pub fn run_for(&mut self, steps: usize) -> Result<()> {
        for _ in 0..steps {
            self.step()?;
        }

        Ok(())
    }
}
