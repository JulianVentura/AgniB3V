use super::structures::{Matrix, Vector, LU};
use super::{element::Element, point::Point};

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
        let n_points = Self::calculate_number_of_points(elements);
        println!("Constructing global M matrix");
        let m = Self::construct_global_matrix(elements, n_points, |e: &Element| &e.m);
        println!("Constructing global K matrix");
        let k = Self::construct_global_matrix(elements, n_points, |e: &Element| &e.k);
        println!("Constructing global flux vector");
        let f = Self::construct_global_vector_f(elements, n_points);
        println!("Constructing points array");
        let points = Self::construct_points_array(elements, n_points);

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

        (size + 1) as usize
    }

    fn construct_points_array(elements: &Vec<Element>, n_points: usize) -> Vec<Point> {
        let mut points: Vec<Point> = Vec::new();
        points.reserve_exact(n_points);

        points.resize(n_points, Default::default());
        // If we dont fill the vector with default values, we will get an error when trying to access an element

        // TODO: This is not very efficient, we can check if the point already exists
        for e in elements {
            points[e.p1.global_id as usize] = e.p1.clone();
            points[e.p2.global_id as usize] = e.p2.clone();
            points[e.p3.global_id as usize] = e.p3.clone();
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
                    let v = local_matrix[(y, x)];
                    let new_x = map[x] as usize;
                    let new_y = map[y] as usize;
                    m[(new_y, new_x)] += v;
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
                let new_i = map[i] as usize;
                f[new_i] += v;
            }
        }

        f
    }
}
