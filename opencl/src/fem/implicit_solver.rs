use super::element::Element;
use super::point::Point;
use super::solver;
use super::structures::{Matrix, Vector, LU};
use anyhow::{Context, Result};

pub struct ImplicitSolver {
    pub f_const: Vec<Vector>,
    pub f_const_eclipse: Vec<Vector>,
    pub a_lu: LU,
    pub d: Matrix,
    pub h: Matrix,
    temp: Vector,
    points: Vec<Point>,
    f_index: usize,
    in_eclipse: bool,
}

impl ImplicitSolver {
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
        let f_const = solver::construct_global_vector_f_const_multiple_earth(elements, n_points);
        println!("Constructing global flux vector eclipse");
        let f_const_eclipse =
            solver::construct_global_vector_f_const_eclipse_multiple_earth(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);
        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f64>>());

        let h = l - e;

        //Implicit matrixes
        let theta = 0.5;
        let d = &m / time_step - (1.0 - theta) * &k;
        let a = &m / time_step + theta * &k;
        println!("Building LU decomposition");

        let a_lu = a.clone().lu();

        println!("Implicit Solver built successfully");

        Ok(ImplicitSolver {
            f_const,
            f_const_eclipse,
            a_lu,
            d,
            h,
            temp,
            points,
            in_eclipse: false,
            f_index: 0,
        })
    }

    pub fn step(&mut self) -> Result<()> {
        //TODO: Optimize this clone
        let mut t_4 = self.temp.clone();
        solver::fourth_power(&mut t_4);

        let mut f = &self.h * t_4;
        //TODO: Merge both f_const vectors into one
        if self.in_eclipse {
            f += &self.f_const_eclipse[self.f_index];
        } else {
            f += &self.f_const[self.f_index];
        }

        let b = &self.d * &self.temp + f;

        self.temp = self
            .a_lu
            .solve(&b)
            .with_context(|| "Couldn't solve linear system")?;
        Ok(())
    }

    pub fn update_f(&mut self, f_index: usize, in_eclipse: bool) -> Result<()> {
        self.f_index = f_index;
        self.in_eclipse = in_eclipse;

        Ok(())
    }

    pub fn points(&self) -> &Vec<Point> {
        &self.points
    }

    pub fn temperature(&mut self) -> Result<&Vector> {
        Ok(&self.temp)
    }
}
