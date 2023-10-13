use super::element::Element;
use super::point::Point;
use super::solver;
use super::structures::{Matrix, Vector, LU};

pub struct ImplicitSolver {
    f_const: Vector,
    pub a_lu: LU,
    pub d: Matrix,
    pub h: Matrix,
    temp: Vector,
    points: Vec<Point>,
}

impl ImplicitSolver {
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
        let f_const = solver::construct_global_vector_f_const(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);
        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f64>>());

        let h = l - e;

        //Implicit matrixes
        let theta = 0.5;
        let d = &m / time_step - (1.0 - theta) * &k;
        let a = &m / time_step + theta * &k;
        let a_lu = a.lu();
        println!("FEM Engine built successfully");

        ImplicitSolver {
            f_const,
            a_lu,
            d,
            h,
            temp,
            points,
        }
    }

    pub fn step(&mut self) {
        //System:
        // A * Tn+1 = D * Tn + (1 - theta) * Fn + theta * Fn+1
        // Since Fn+1 == Fn, then the system is simplified
        // TODO: Change f vector if radiation is included
        let mut t_4 = self.temp.clone();
        solver::fourth_power(&mut t_4);

        let f = &self.f_const + &self.h * t_4;
        let b = &self.d * &self.temp + f;

        self.temp = self.a_lu.solve(&b).expect("Oh no...");
    }

    pub fn points(&self) -> &Vec<Point> {
        &self.points
    }

    pub fn temperature(&self) -> Vector {
        self.temp.clone()
    }
}
