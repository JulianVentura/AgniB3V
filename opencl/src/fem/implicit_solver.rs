use super::element::Element;
use super::solver;
use super::structures::{Matrix, Vector, LU};

pub struct ImplicitSolver {
    f: Vector,
    pub a_lu: LU,
    pub d: Matrix,
    temp: Vector,
}

impl ImplicitSolver {
    pub fn new(elements: &Vec<Element>, time_step: f64) -> Self {
        let n_points = solver::calculate_number_of_points(elements);
        println!("Constructing global M matrix");
        let m = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.m);
        println!("Constructing global K matrix");
        let k = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.k);
        println!("Constructing global flux vector");
        let f = solver::construct_global_vector_f_const(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);
        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f64>>());

        //Implicit matrixes
        let theta = 0.5;
        let d = &m / time_step - (1.0 - theta) * &k;
        let a = &m / time_step + theta * &k;
        let a_lu = a.lu();
        println!("FEM Engine built successfully");

        ImplicitSolver { f, a_lu, d, temp }
    }

    pub fn step(&mut self) {
        //System:
        // A * Tn+1 = D * Tn + (1 - theta) * Fn + theta * Fn+1
        // Since Fn+1 == Fn, then the system is simplified
        // TODO: Change f vector if radiation is included

        let b = &self.d * &self.temp + &self.f;

        self.temp = self.a_lu.solve(&b).expect("Oh no...");
    }

    pub fn temperature(&self) -> Vector {
        self.temp.clone()
    }
}
