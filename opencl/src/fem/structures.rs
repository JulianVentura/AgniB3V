use nalgebra::{DMatrix, DVector, Dyn};

pub type Matrix = DMatrix<f32>;
pub type LU = nalgebra::LU<f32, Dyn, Dyn>;
pub type Vector = DVector<f32>;
