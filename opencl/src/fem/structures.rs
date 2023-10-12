use nalgebra::{DMatrix, DVector, Dyn};

pub type Matrix = DMatrix<f64>;
pub type LU = nalgebra::LU<f64, Dyn, Dyn>;
pub type Vector = DVector<f64>;
