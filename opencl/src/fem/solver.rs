use super::structures::Vector;

pub trait Solver {
    fn step(&mut self, temp: &Vector) -> Vector;
}
