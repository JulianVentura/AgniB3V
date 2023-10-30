use std::collections::HashSet;

use super::constants::BOLTZMANN;
use super::structures::{Matrix, Vector};
use super::{element::Element, point::Point};

pub fn calculate_number_of_points(elements: &Vec<Element>) -> usize {
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

pub fn construct_points_array(elements: &Vec<Element>, n_points: usize) -> Vec<Point> {
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

pub fn construct_global_matrix(
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

pub fn construct_l_matrix(elements: &Vec<Element>, n_points: usize) -> Matrix {
    //P[i][j] = F[i][j] * alpha_ir_i * alpha_ir_j * area_i
    //
    //L[i][j] = 0
    //for k in elems(i)
    //  for w in elems(j)
    //    L[i][j] += P[w][k]

    let n_elements = elements.len();
    let mut elems: Vec<HashSet<u32>> = vec![HashSet::default(); n_points];
    let mut view_factors: Vec<Vec<f64>> = vec![Vec::default(); n_elements];

    for (i, element) in elements.iter().enumerate() {
        elems[element.p1.global_id as usize].insert(i as u32);
        elems[element.p2.global_id as usize].insert(i as u32);
        elems[element.p3.global_id as usize].insert(i as u32);

        view_factors[i] = element.view_factors.clone();
    }

    let mut p =
        Matrix::from_row_iterator(n_elements, n_elements, view_factors.into_iter().flatten());

    for i in 0..elements.len() {
        for j in 0..elements.len() {
            let alpha_i = &elements[i].alpha_ir;
            let alpha_j = &elements[j].alpha_ir;
            let area = &elements[i].area;
            p[(i, j)] *= alpha_i * alpha_j * area;
        }
    }

    let l = Matrix::from_fn(n_points, n_points, |i, j| {
        let mut v = 0.0;
        for k in &elems[i] {
            for w in &elems[j] {
                v += p[(*w as usize, *k as usize)];
            }
        }
        v
    });

    l * BOLTZMANN / 3.0
}

pub fn construct_global_vector_f_const(elements: &Vec<Element>, n_points: usize) -> Vector {
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

pub fn construct_global_vector_f_const_eclipse(elements: &Vec<Element>, n_points: usize) -> Vector {
    let mut f = Vector::zeros(n_points);

    for e in elements {
        let map = [e.p1.global_id, e.p2.global_id, e.p3.global_id];
        let local_vector = &e.f_eclipse;

        for i in 0..3 {
            let v = local_vector[i];
            let new_i = map[i] as usize;
            f[new_i] += v;
        }
    }

    f
}

pub fn fourth_power(array: &mut Vector) {
    for val in array.iter_mut() {
        *val *= *val;
        *val *= *val;
    }
}

#[cfg(test)]
mod tests {
    use crate::fem::constants::BOLTZMANN;
    use crate::fem::element::{Element, MaterialProperties, ViewFactors};
    use crate::fem::point::Point;
    use crate::fem::solver;
    use crate::fem::structures::{Matrix, Vector};

    fn assert_float_eq(value_1: f64, value_2: f64, precision: f64) {
        assert!(
            (value_1 - value_2).abs() < precision,
            "value1 {} != {}",
            value_1,
            value_2
        );
    }

    #[test]
    fn test_fourth_power() {
        let mut v = Vector::from_row_slice(&[1.0, 2.0, 3.0]);
        let expected = Vector::from_row_slice(&[1.0, 16.0, 81.0]);

        solver::fourth_power(&mut v);

        for (x, e) in v.iter().zip(expected.iter()) {
            assert_float_eq(*x, *e, f64::EPSILON);
        }
    }

    #[test]
    fn test_l_matrix_construction_base_2d_plane() {
        let conductivity = 237.0;
        let density = 2700.0;
        let specific_heat = 900.0;
        let thickness = 0.1;
        let alpha_sun = 1.0;
        let solar_intensity = 300.0;
        let earth_ir = 1.0;
        let betha = 0.1;
        let albedo_factor = 0.1;

        let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 0.0]), 0.0, 0, 0);
        let p2 = Point::new(Vector::from_row_slice(&[1.0, 0.0, 0.0]), 0.0, 1, 0);
        let p3 = Point::new(Vector::from_row_slice(&[1.0, 1.0, 0.0]), 0.0, 2, 0);
        let p4 = Point::new(Vector::from_row_slice(&[0.0, 1.0, 0.0]), 0.0, 3, 0);

        let props1 = MaterialProperties {
            conductivity,
            density,
            specific_heat,
            thickness,
            alpha_sun,
            alpha_ir: 0.7,
        };

        let props2 = MaterialProperties {
            conductivity,
            density,
            specific_heat,
            thickness,
            alpha_sun,
            alpha_ir: 0.5,
        };

        let f1 = ViewFactors {
            earth: 1.0,
            sun: 1.0,
            elements: vec![0.1, 0.3],
        };

        let f2 = ViewFactors {
            earth: 1.0,
            sun: 1.0,
            elements: vec![0.2, 0.4],
        };

        let e1 = Element::new(
            p1.clone(),
            p2.clone(),
            p3.clone(),
            props1,
            f1,
            solar_intensity,
            earth_ir,
            betha,
            albedo_factor,
            0.0,
        );

        let e2 = Element::new(
            p2,
            p4,
            p3,
            props2,
            f2,
            solar_intensity,
            earth_ir,
            betha,
            albedo_factor,
            0.0,
        );

        let mut l = solver::construct_l_matrix(&vec![e1, e2], 4);

        l /= BOLTZMANN / 3.0;

        let expected = Matrix::from_row_slice(
            4,
            4,
            &[
                0.0245, 0.0595, 0.0595, 0.035, //
                0.077, 0.162, 0.162, 0.085, //
                0.077, 0.162, 0.162, 0.085, //
                0.0525, 0.1025, 0.1025, 0.05, //
            ],
        );

        for (x, e) in l.iter().zip(expected.iter()) {
            assert_float_eq(*x, *e, f64::EPSILON);
        }
    }
}
