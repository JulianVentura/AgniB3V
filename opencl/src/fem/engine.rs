use super::{element::Element, point::Point};
use anyhow::Result;
use rulinalg::{matrix, vector};

type Vector = vector::Vector<f32>;
type Matrix = matrix::Matrix<f32>;

pub struct FEMEngine {
    simulation_time: f32, //TODO
    time_step: f32,       //TODO
    points: Vec<Point>,
    m_inverse: Matrix,
    m_inverse_k: Matrix,
    f: Vector,
}

#[allow(dead_code)]
pub struct FEMProblem {
    elements: Vec<Element>,
    simulation_time: f32,
    time_step: f32,
}

impl FEMEngine {
    pub fn new(simulation_time: f32, time_step: f32, elements: Vec<Element>) -> Self {
        let n_points = Self::calculate_number_of_points(&elements);
        let m = Self::construct_global_matrix(&elements, n_points, |e: &Element| &e.m);
        let k = Self::construct_global_matrix(&elements, n_points, |e: &Element| &e.k);
        let f = Self::construct_global_vector_f(&elements, n_points);
        let points = Self::construct_points_array(elements, n_points);

        let m_inverse = m
            .inverse()
            .expect("Couldn't invert M matrix, this is wrong...");
        let m_inverse_k = &m_inverse * &k;

        FEMEngine {
            simulation_time,
            time_step,
            points,
            m_inverse,
            m_inverse_k,
            f,
        }
    }

    pub fn run(&mut self) -> Result<Vec<Vector>> {
        let mut time = 0.0;
        let mut temp = Vector::new(
            self.points
                .iter()
                .map(|p| p.temperature)
                .collect::<Vec<f32>>(),
        );
        let mut temp_results = Vec::new();
        temp_results.push(temp.clone());

        while time < self.simulation_time {
            temp = self.step(&temp);
            temp_results.push(temp.clone());
            time += self.time_step;
        }

        Ok(temp_results)
    }

    pub fn step(&mut self, temp: &Vector) -> Vector {
        temp + (&self.m_inverse * &self.f - &self.m_inverse_k * temp) * self.time_step
    }

    fn calculate_number_of_points(elements: &Vec<Element>) -> usize {
        use std::cmp::max;

        //Right now its ok, but we have to make sure the global ids are sequential (and start from 1)
        let mut size: u32 = 0;
        for e in elements {
            size = max(
                max(max(e.p1.global_id, e.p2.global_id), e.p3.global_id),
                size,
            );
        }

        size as usize
    }

    fn construct_points_array(elements: Vec<Element>, n_points: usize) -> Vec<Point> {
        let mut points: Vec<Point> = Vec::new();
        points.reserve_exact(n_points);

        points.resize(n_points, Default::default());
        // If we dont fill the vector with default values, we will get an error when trying to access an element

        // TODO: This is not very efficient, we can check if the point already exists
        for e in elements {
            points[(e.p1.global_id - 1) as usize] = e.p1.clone();
            points[(e.p2.global_id - 1) as usize] = e.p2.clone();
            points[(e.p3.global_id - 1) as usize] = e.p3.clone();
        }

        points
    }

    fn construct_global_matrix(
        elements: &Vec<Element>,
        n_points: usize,
        key: fn(e: &Element) -> &Matrix,
    ) -> Matrix {
        let mut m = Matrix::zeros(n_points, n_points);

        for e in elements {
            let map = [e.p1.global_id, e.p2.global_id, e.p3.global_id];
            let local_matrix = key(e);

            for y in 0..3 {
                for x in 0..3 {
                    let v = local_matrix[[y, x]];
                    let new_x = (map[x] - 1) as usize;
                    let new_y = (map[y] - 1) as usize;
                    m[[new_y, new_x]] += v;
                }
            }
        }

        m
    }

    fn construct_global_vector_f(elements: &Vec<Element>, n_points: usize) -> Vector {
        let mut f = Vector::zeros(n_points);

        for e in elements {
            let map = [e.p1.global_id, e.p2.global_id, e.p3.global_id];
            let local_vector = &e.f;

            for i in 0..3 {
                let v = local_vector[i];
                let new_i = (map[i] - 1) as usize;
                f[new_i] += v;
            }
        }

        f
    }
}
