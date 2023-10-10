use super::structures::{Matrix, Vector, LU};
use super::{element::Element, point::Point};
use super::solver;

pub struct ExplicitSolver {
    pub m_lu: LU,
    pub k: Matrix,
    f: Vector,
    temp: Vector,
    points: Vec<Point>,
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
    pub fn new(elements: &Vec<Element>) -> Self {
        let n_points = solver::calculate_number_of_points(elements);
        println!("Constructing global M matrix");
        let m = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.m);
        println!("Constructing global K matrix");
        let k = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.k);
        println!("Constructing global flux vector");
        let f = solver::construct_global_vector_f(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);

        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f32>>());

        let m_lu = m.lu();
        println!("FEM Engine built successfully");

        ExplicitSolver {
            m_lu,
            k,
            f,
            temp,
            points,
        }
    }

    pub fn temperature(&self) -> Vector {
        self.temp.clone()
    }

    pub fn points(&self) -> &Vec<Point> {
        &self.points
    }

    pub fn step(&mut self, time_step: f32) {
        let b = &self.f - &self.k * &self.temp;
        let x = &self.m_lu.solve(&b).expect("Oh no...");

        self.temp = time_step * x + &self.temp;
    }
}
