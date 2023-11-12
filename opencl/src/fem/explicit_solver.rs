use super::solver;
use super::structures::{Matrix, Vector, LU};
use super::{element::Element, point::Point};
use anyhow::Result;

pub struct ExplicitSolver {
    pub m_lu: LU,
    pub k: Matrix,
    pub h: Matrix,
    f_const: Vec<Vector>,
    f_const_eclipse: Vec<Vector>,
    f_index: usize,
    in_eclipse: bool,
    temp: Vector,
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
    pub fn new(elements: &Vec<Element>, time_step: f64) -> Self {
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
        let f_const = solver::construct_global_vector_f_const_multiple_earth(elements, n_points);
        println!("Constructing global flux vector eclipse");
        let f_const_eclipse =
            solver::construct_global_vector_f_const_eclipse_multiple_earth(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);
        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f64>>());

        let h = l - e;

        let m_lu = m.lu();
        println!("Explicit Solver built successfully");

        ExplicitSolver {
            m_lu,
            k,
            h,
            f_const,
            f_const_eclipse,
            time_step,
            f_index: 0,
            in_eclipse: false,
            temp,
            points,
        }
    }

    pub fn temperature(&mut self) -> Result<&Vector> {
        Ok(&self.temp)
    }

    pub fn points(&self) -> &Vec<Point> {
        &self.points
    }

    pub fn update_f(&mut self, f_index: usize, in_eclipse: bool) -> Result<()> {
        self.f_index = f_index;
        self.in_eclipse = in_eclipse;

        Ok(())
    }

    pub fn step(&mut self) -> Result<()> {
        let mut t_4 = self.temp.clone();
        solver::fourth_power(&mut t_4);

        let mut f = &self.h * &t_4;
        if self.in_eclipse {
            f += &self.f_const_eclipse[self.f_index];
        } else {
            f += &self.f_const[self.f_index];
        }
        let b = f - &self.k * &self.temp;
        let x = &self.m_lu.solve(&b).expect("Oh no...");

        self.temp = self.time_step * x + &self.temp;

        Ok(())
    }
}
