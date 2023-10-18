use super::solver;
use super::structures::{Matrix, Vector, LU};
use super::{element::Element, point::Point};

pub struct ExplicitSolver {
    pub m_lu: LU,
    pub k: Matrix,
    pub h: Matrix,
    f_const: Vector,
    f_const_eclipse: Vector,
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
        println!("Constructing global E matrix");
        let e = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.e);
        println!("Constructing global L matrix");
        let l = solver::construct_l_matrix(elements, n_points);
        println!("Constructing global flux vector");
        let f_const = solver::construct_global_vector_f_const(elements, n_points);
        println!("Constructing global flux vector eclipse");
        let f_const_eclipse = solver::construct_global_vector_f_const_eclipse(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);
        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f64>>());

        let h = l - e;

        let m_lu = m.lu();
        println!("FEM Engine built successfully");

        ExplicitSolver {
            m_lu,
            k,
            h,
            f_const,
            f_const_eclipse,
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

    pub fn step(&mut self, time_step: f64, is_in_eclipse: bool) {
        let mut t_4 = self.temp.clone();
        solver::fourth_power(&mut t_4);

        let mut f = &self.h * &t_4;
        if is_in_eclipse {
            f += &self.f_const_eclipse;
        } else {
            f += &self.f_const;
        }
        let b = f - &self.k * &self.temp;
        let x = &self.m_lu.solve(&b).expect("Oh no...");

        self.temp = time_step * x + &self.temp;
    }
}
