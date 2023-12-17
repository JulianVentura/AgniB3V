use std::collections::HashSet;

use super::constants::BOLTZMANN;
use super::structures::{Matrix, Vector};
use super::{element::Element, point::Point};
use std::cmp::max;

/// The function calculates the number of points based on the maximum global ID of the elements.
///
/// Arguments:
///
/// * `elements`: The `elements` parameter is a vector of `Element` objects.
///
/// Returns:
///
/// the number of points in the `elements` vector.
pub fn calculate_number_of_points(elements: &Vec<Element>) -> usize {
    let mut size: u32 = 0;
    for e in elements {
        size = max(
            max(max(e.p1.global_id, e.p2.global_id), e.p3.global_id),
            size,
        );
    }

    (size + 1) as usize
}

/// The function constructs an array of points by populating it with elements from a given vector.
///
/// Arguments:
///
/// * `elements`: `elements` is a vector of `Element` structs. Each `Element` struct contains three
/// `Point` structs (`p1`, `p2`, and `p3`).
/// * `n_points`: The `n_points` parameter represents the number of points that should be present in the
/// resulting `points` array.
///
/// Returns:
///
/// The function `construct_points_array` returns a `Vec<Point>`.
pub fn construct_points_array(elements: &Vec<Element>, n_points: usize) -> Vec<Point> {
    let mut points: Vec<Point> = Vec::new();
    points.reserve_exact(n_points);

    points.resize(n_points, Default::default());

    for e in elements {
        points[e.p1.global_id as usize] = e.p1.clone();
        points[e.p2.global_id as usize] = e.p2.clone();
        points[e.p3.global_id as usize] = e.p3.clone();
    }

    points
}

/// The function constructs a global matrix by iterating over a vector of elements and mapping their
/// local matrices to the corresponding positions in the global matrix.
///
/// Arguments:
///
/// * `elements`: A vector of elements. Each element contains information about three points (p1, p2,
/// p3) and a global_id.
/// * `n_points`: The parameter `n_points` represents the number of points in the global matrix. It
/// specifies the size of the square matrix that will be constructed.
/// * `key`: The `key` parameter is a function that takes an `Element` as input and returns a reference
/// to a `Matrix`. This function is used to retrieve the local matrix associated with each element in
/// the `elements` vector.
///
/// Returns:
///
/// The function `construct_global_matrix` returns a `Matrix` object.
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

/// The function constructs an L matrix using view factors and other parameters for a given set of
/// elements and number of points.
///
/// Arguments:
///
/// * `elements`: A vector of `Element` structs, which represent the elements in the system. Each
/// `Element` struct contains information about the element's points (`p1`, `p2`, `p3`), view factors
/// (`view_factors`), alpha values (`alpha_ir`), and area (`area`)
/// * `n_points`: The `n_points` parameter represents the number of points in the system. It is used to
/// determine the size of the resulting matrix `L`, which will have dimensions `n_points` x `n_points`.
///
/// Returns:
///
/// a matrix, specifically the L matrix.
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

    l * BOLTZMANN / 9.0
}

/// The function constructs a global vector by iterating over the divisions of elements and applying a
/// function to each element.
///
/// Arguments:
///
/// * `elements`: A vector of elements. Each element has a field `f` which is an array of values.
/// * `n_points`: The `n_points` parameter represents the number of points in the vector.
///
/// Returns:
///
/// The function `construct_global_vector_f_const_array` returns a `Vec<Vector>`.
pub fn construct_global_vector_f_const_array(
    elements: &Vec<Element>,
    n_points: usize,
) -> Vec<Vector> {
    let n_divisions = match elements.get(0) {
        Some(e) => e.f.len(),
        None => 0,
    };

    (0..n_divisions)
        .map(|i| construct_global_vector_f_const(elements, n_points, |e: &Element| &e.f[i]))
        .collect()
}
/// The function constructs a global vector by summing up the local vectors of each element based on a
/// given key function.
///
/// Arguments:
///
/// * `elements`: A reference to a vector of elements. Each element has three points (p1, p2, p3) and a
/// global_id.
/// * `n_points`: The `n_points` parameter represents the number of points in the global vector `f`. It
/// specifies the size of the vector that will be constructed.
/// * `key`: The `key` parameter is a closure that takes an `Element` as input and returns a reference
/// to a `Vector`. It is used to extract the local vector associated with each element.
///
/// Returns:
///
/// The function `construct_global_vector_f_const` returns a `Vector` object.
fn construct_global_vector_f_const(
    elements: &Vec<Element>,
    n_points: usize,
    key: impl Fn(&Element) -> &Vector,
) -> Vector {
    let mut f = Vector::zeros(n_points);

    for e in elements {
        let map = [e.p1.global_id, e.p2.global_id, e.p3.global_id];
        let local_vector = key(&e);

        for i in 0..3 {
            let v = local_vector[i];
            let new_i = map[i] as usize;
            f[new_i] += v;
        }
    }

    f
}

/// The function `fourth_power` takes an input array, and raises each elementto the fourth power
///
/// Arguments:
///
/// * `source_array`: source_array is a reference to a Vector, which is a collection of elements. It is
/// the input array from which we will calculate the fourth power of each element.
/// * `result_array`: The `result_array` parameter is a mutable reference to a `Vector`. It is used to
/// store the fourth power of each element in the `source_array`.
pub fn fourth_power(source_array: &Vector, result_array: &mut Vector) {
    for (idx, val) in source_array.iter().enumerate() {
        let aux = val * val;
        result_array[idx] = aux * aux;
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
        let source = Vector::from_row_slice(&[1.0, 2.0, 3.0]);
        let mut result = Vector::from_row_slice(&[0.0, 0.0, 0.0]);
        let expected = Vector::from_row_slice(&[1.0, 16.0, 81.0]);

        solver::fourth_power(&source, &mut result);

        for (x, e) in result.iter().zip(expected.iter()) {
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
            earth_ir: vec![1.0],
            earth_albedo: vec![1.0],
            sun: 1.0,
            elements: vec![0.1, 0.3],
        };

        let f2 = ViewFactors {
            earth_ir: vec![1.0],
            earth_albedo: vec![1.0],
            sun: 1.0,
            elements: vec![0.2, 0.4],
        };

        let divisions = vec![(0, false)];

        let e1 = Element::new(
            p1.clone(),
            p2.clone(),
            p3.clone(),
            props1,
            f1,
            solar_intensity,
            earth_ir,
            albedo_factor,
            0.0,
            false,
            &divisions,
        )
        .unwrap();

        let e2 = Element::new(
            p2,
            p4,
            p3,
            props2,
            f2,
            solar_intensity,
            earth_ir,
            albedo_factor,
            0.0,
            false,
            &divisions,
        )
        .unwrap();

        let mut l = solver::construct_l_matrix(&vec![e1, e2], 4);

        l /= BOLTZMANN / 3.0;

        let expected = Matrix::from_row_slice(
            4,
            4,
            &[
                //Row 1
                49.0 / 6000.0,
                119.0 / 6000.0,
                119.0 / 6000.0,
                7.0 / 600.0,
                //Row 2
                77.0 / 3000.0,
                27.0 / 500.0,
                27.0 / 500.0,
                17.0 / 600.0,
                //Row 3
                77.0 / 3000.0,
                27.0 / 500.0,
                27.0 / 500.0,
                17.0 / 600.0,
                //Row 4
                7.0 / 400.0,
                41.0 / 1200.0,
                41.0 / 1200.0,
                1.0 / 60.0,
            ],
        );

        for (x, e) in l.iter().zip(expected.iter()) {
            assert_float_eq(*x, *e, f64::EPSILON);
        }
    }
}
