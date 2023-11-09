use anyhow::Result;
use std::fs::File;
use std::io::prelude::*;
use std::time::Instant;

use crate::gpu::matrix_inversion;
use crate::gpu::matrix_mult::compile_kernel;
use crate::gpu::matrix_mult::MatrixMult;

use super::super::gpu::matrix_mult::matrix_mult;

use super::super::gpu::eq_systems_methods_cpu::lu_decomposition;
use super::super::gpu::eq_systems_methods_cpu::lu_solve;

use super::super::gpu::eq_systems_methods_cpu::LUDecomposition;

use super::super::gpu::eq_systems_methods_cpu::gauss_seidel_cpu;

use super::super::gpu::eq_systems_methods_cpu::jacobi_method_cpu;

use super::super::gpu::matrix_inversion::matrix_inversion;

use super::element::Element;
use super::point::Point;
use super::solver;
use super::structures::{Matrix, Vector, LU};

pub struct ImplicitSolver {
    f_const: Vec<Vector>,
    f_const_eclipse: Vec<Vector>,
    pub a_lu: LU,
    pub a: Matrix,
    pub d: Matrix,
    pub h: Matrix,
    temp: Vector,
    points: Vec<Point>,
    pub matrix_mult: MatrixMult,
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
        //let a_lu_dec = lu_decomposition(a.clone());

        let a_lu = a.clone().lu();
        let a_inverse = matrix_inversion(a.clone()).expect("Oh no2...");
        let matrix_mult = compile_kernel(&temp, &h, &f_const[0], &d, &a_inverse).expect("Oh no...");

        println!("FEM Engine built successfully");

        ImplicitSolver {
            f_const,
            f_const_eclipse,
            a_lu,
            a,
            d,
            h,
            temp,
            points,
            matrix_mult,
        }
    }

    pub fn step(&mut self, is_in_eclipse: bool, f_index: usize) {
        //System:
        // A * Tn+1 = D * Tn + (1 - theta) * Fn + theta * Fn+1
        // Since Fn+1 == Fn, then the system is simplified
        // TODO: Change f vector if radiation is included
        let mut t_4 = self.temp.clone();
        solver::fourth_power(&mut t_4);

        let mut f = &self.h * t_4;
        if is_in_eclipse {
            f += &self.f_const_eclipse[f_index];
        } else {
            f += &self.f_const[f_index];
        }

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
