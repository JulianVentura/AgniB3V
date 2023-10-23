use super::constants::BOLTZMANN;
use super::point::Point;
use super::structures::{Matrix, Vector};

#[derive(Debug)]
pub struct Element {
    pub p1: Point,
    pub p2: Point,
    pub p3: Point,
    pub k: Matrix,
    pub m: Matrix,
    pub e: Matrix,
    pub f: Vector,
    pub f_eclipse: Vector,
    pub alpha_sun: f64,
    pub alpha_ir: f64,
    pub view_factors: Vec<f64>,
    pub area: f64,
}

#[derive(Clone, Debug)]
pub struct MaterialProperties {
    pub conductivity: f64,
    pub density: f64,
    pub specific_heat: f64,
    pub thickness: f64,
    pub alpha_sun: f64,
    pub alpha_ir: f64,
}

impl Default for MaterialProperties {
    fn default() -> Self {
        MaterialProperties {
            conductivity: 0.0,
            density: 0.0,
            specific_heat: 0.0,
            thickness: 0.0,
            alpha_sun: 0.0,
            alpha_ir: 0.0,
        }
    }
}

#[derive(Clone, Debug)]
pub struct ViewFactors {
    pub earth: f64,
    pub sun: f64,
    pub elements: Vec<f64>,
}

impl Element {
    pub fn new(
        mut p1: Point,
        mut p2: Point,
        mut p3: Point,
        properties: MaterialProperties,
        factors: ViewFactors,
        solar_intensity: f64,
        betha: f64,
        albedo_factor: f64,
        generated_heat: f64,
    ) -> Self {
        Self::check_point_length(&p1);
        Self::check_point_length(&p2);
        Self::check_point_length(&p3);

        let area: f64 = Self::calculate_area(&p1, &p2, &p3);

        p1.set_local_id(1);
        p2.set_local_id(2);
        p3.set_local_id(3);

        let k = Self::calculate_k(
            &p1,
            &p2,
            &p3,
            properties.conductivity,
            area,
            properties.thickness,
        );

        let m = Self::calculate_m(
            area,
            properties.specific_heat,
            properties.density,
            properties.thickness,
        );

        let e = Self::calculate_e(area, properties.alpha_ir);

        let f = Self::calculate_f(
            area,
            &properties,
            &factors,
            solar_intensity,
            betha,
            albedo_factor,
            generated_heat,
        );

        let f_eclipse = Self::calculate_f_eclipse(area, &properties, &factors, generated_heat);

        Element {
            p1,
            p2,
            p3,
            k,
            m,
            e,
            f,
            f_eclipse,
            alpha_sun: properties.alpha_sun,
            alpha_ir: properties.alpha_ir,
            view_factors: factors.elements,
            area,
        }
    }

    pub fn basic(p1: Point, p2: Point, p3: Point, generated_heat: f64, n_elements: usize) -> Self {
        let conductivity = 237.0;
        let density = 2700.0;
        let specific_heat = 900.0;
        let thickness = 0.01;
        let alpha_sun = 1.0;
        let alpha_ir = 1.0;
        let solar_intensity = 300.0;
        let betha = 0.1;
        let albedo_factor = 0.1;

        let props = MaterialProperties {
            conductivity,
            density,
            specific_heat,
            thickness,
            alpha_sun,
            alpha_ir,
        };

        let factors = ViewFactors {
            earth: 1.0,
            sun: 1.0,
            elements: vec![0.1f64; n_elements],
        };

        Self::new(
            p1,
            p2,
            p3,
            props,
            factors,
            solar_intensity,
            betha,
            albedo_factor,
            generated_heat,
        )
    }

    fn calculate_area(p1: &Point, p2: &Point, p3: &Point) -> f64 {
        let ab = &p2.position - &p1.position;
        let ac = &p3.position - &p1.position;

        //Cross product
        let a: f64 = ab[1] * ac[2] - ab[2] * ac[1];
        let b: f64 = ab[2] * ac[0] - ab[0] * ac[2];
        let c: f64 = ab[0] * ac[1] - ab[1] * ac[0];

        (a * a + b * b + c * c).sqrt() / 2.0
    }

    fn calculate_sqr_distance(p1: &Point, p2: &Point) -> f64 {
        let mut distance = (p1.position[0] - p2.position[0]).powi(2);
        distance += (p1.position[1] - p2.position[1]).powi(2);
        distance += (p1.position[2] - p2.position[2]).powi(2);

        distance
    }

    fn edges_dot_product(a: (&Point, &Point), b: (&Point, &Point)) -> f64 {
        //Calculate the dot product between two edges
        let edge1 = &a.1.position - &a.0.position;
        let edge2 = &b.1.position - &b.0.position;

        edge1.dot(&edge2)
    }

    fn check_point_length(point: &Point) {
        //TODO: Add error handling
        if point.position.len() != 3 {
            panic!("Point length is not 3");
        }
    }

    fn calculate_k(
        p1: &Point,
        p2: &Point,
        p3: &Point,
        conductivity: f64,
        area: f64,
        thickness: f64,
    ) -> Matrix {
        let k11 = Self::calculate_sqr_distance(&p2, &p3);
        let k22 = Self::calculate_sqr_distance(&p1, &p3);
        let k33 = Self::calculate_sqr_distance(&p1, &p2);

        //(2 -> 3) ^ (3 -> 1)
        let k12 = Self::edges_dot_product((&p2, &p3), (&p3, &p1));
        //(2 -> 3) ^ (1 -> 2)
        let k13 = Self::edges_dot_product((&p2, &p3), (&p1, &p2));
        //(3 -> 1) ^ (1 -> 2)
        let k23 = Self::edges_dot_product((&p3, &p1), (&p1, &p2));

        let k21 = k12;
        let k31 = k13;
        let k32 = k23;

        let mut k = Matrix::from_row_slice(
            3,
            3,
            &[
                k11, k12, k13, //Row 1
                k21, k22, k23, //Row 2
                k31, k32, k33, //Row 3
            ],
        );

        //TODO: Check if thickness is correct
        k = k * thickness * conductivity / (4.0 * area);
        k
    }

    fn calculate_m(area: f64, specific_heat: f64, density: f64, thickness: f64) -> Matrix {
        let mut m = Matrix::from_row_slice(
            3,
            3,
            &[
                2.0, 1.0, 1.0, //Row 1
                1.0, 2.0, 1.0, //Row 2
                1.0, 1.0, 2.0, //Row 3
            ],
        );

        //TODO: Check if thickness is correct
        m = m * (area * specific_heat * density * thickness / 12.0);

        m
    }

    fn calculate_e(area: f64, alpha: f64) -> Matrix {
        let e = Matrix::from_row_slice(
            3,
            3,
            &[
                1.0, 0.0, 0.0, //Row 1
                0.0, 1.0, 0.0, //Row 2
                0.0, 0.0, 1.0, //Row 3
            ],
        );

        (BOLTZMANN * alpha * area / 3.0) * e
    }

    fn calculate_f(
        area: f64,
        properties: &MaterialProperties,
        factors: &ViewFactors,
        solar_intensity: f64,
        betha: f64,
        albedo_factor: f64,
        generated_heat: f64,
    ) -> Vector {
        //TODO: Add single node heat source
        // f += [nodo1.heat_source, nodo2.heat_source, nodo3.heat_source]
        //Note: probably that would make each element where that node is part add its heat source, so it would be duplicated
        let f = Vector::from_row_slice(&[1.0, 1.0, 1.0]);

        //TODO: Define constant value
        let constant = 1.0;

        let solar = properties.alpha_sun * solar_intensity * f64::sin(betha.into()) * factors.sun;
        let ir = properties.alpha_ir * constant * factors.earth;
        let albedo = properties.alpha_sun * solar_intensity * albedo_factor * factors.earth;

        let magnitude = (generated_heat + solar + ir + albedo) * area / 3.0;

        magnitude * f
    }

    fn calculate_f_eclipse(
        area: f64,
        properties: &MaterialProperties,
        factors: &ViewFactors,
        generated_heat: f64,
    ) -> Vector {
        //TODO: Add single node heat source
        // f += [nodo1.heat_source, nodo2.heat_source, nodo3.heat_source]
        //Note: probably that would make each element where that node is part add its heat source, so it would be duplicated
        let f = Vector::from_row_slice(&[1.0, 1.0, 1.0]);

        //TODO: Define constant value
        let constant = 1.0;

        let ir = properties.alpha_ir * constant * factors.earth;

        let magnitude = (generated_heat + ir) * area / 3.0;

        magnitude * f
    }
}

#[cfg(test)]
mod tests {
    use crate::fem::element::Element;
    use crate::fem::point::Point;
    use crate::fem::structures::Vector;

    fn calculate_area_default(
        position1: [f64; 3],
        position2: [f64; 3],
        position3: [f64; 3],
    ) -> f64 {
        let p1 = Point::new(Vector::from_row_slice(&position1), 0.0, 0, 0);
        let p2 = Point::new(Vector::from_row_slice(&position2), 0.0, 1, 0);
        let p3 = Point::new(Vector::from_row_slice(&position3), 0.0, 2, 0);

        let area = Element::calculate_area(&p1, &p2, &p3);

        area
    }

    fn assert_float_eq(value_1: f64, value_2: f64, precision: f64) {
        assert!(
            (value_1 - value_2).abs() < precision,
            "value1 {} != {}",
            value_1,
            value_2
        );
    }

    fn calculate_distance_default(position1: [f64; 3], position2: [f64; 3]) -> f64 {
        let p1 = Point::new(Vector::from_row_slice(&position1), 0.0, 0, 0);
        let p2 = Point::new(Vector::from_row_slice(&position2), 0.0, 1, 0);

        let distance = Element::calculate_sqr_distance(&p1, &p2);

        distance
    }

    fn calculate_edges_dot_product_default(
        position1: [f64; 3],
        position2: [f64; 3],
        position3: [f64; 3],
        position4: [f64; 3],
    ) -> f64 {
        let p1 = Point::new(Vector::from_row_slice(&position1), 0.0, 0, 0);
        let p2 = Point::new(Vector::from_row_slice(&position2), 0.0, 1, 0);
        let p3 = Point::new(Vector::from_row_slice(&position3), 0.0, 2, 0);
        let p4 = Point::new(Vector::from_row_slice(&position4), 0.0, 3, 0);

        let dot_product = Element::edges_dot_product((&p1, &p2), (&p3, &p4));

        dot_product
    }
    #[test]
    fn test_calculate_area_1() {
        let position1 = [0.0, 0.0, 0.0];
        let position2 = [1.0, 0.0, 0.0];
        let position3 = [0.0, 1.0, 0.0];
        let area = calculate_area_default(position1, position2, position3);

        assert_eq!(area, 0.5);
    }
    #[test]
    fn test_calculate_area_2() {
        let position1 = [4.3, 7.9, 1.3];
        let position2 = [9.0, -1.7, 13.2];
        let position3 = [13.0, 5.1, -3.7];
        let area = calculate_area_default(position1, position2, position3);

        assert_float_eq(area, 83.217, 0.01);
    }

    #[test]
    fn test_calculate_area_3() {
        let position1 = [-8.1, 2.3, 4.2];
        let position2 = [6.3, 1.1, 2.2];
        let position3 = [3.3, -5.2, -4.2];
        let area = calculate_area_default(position1, position2, position3);

        assert_float_eq(area, 68.11, 0.01);
    }

    #[test]
    fn test_calculate_sqr_distance_1() {
        let position1 = [0.0, 0.0, 0.0];
        let position2 = [1.0, 0.0, 0.0];
        let distance = calculate_distance_default(position1, position2);

        assert_eq!(distance, 1.0);
    }
    #[test]
    fn test_calculate_sqr_distance_2() {
        let position1 = [-1.7, 2.6, 7.3];
        let position2 = [2.2, -1.0, 5.5];
        let distance = calculate_distance_default(position1, position2);

        assert_float_eq(distance, 31.4, 0.02);
    }
    #[test]
    fn test_calculate_sqr_distance_3() {
        let position1 = [2.32, 7.2, 2.4];
        let position2 = [9.31, -3.46, 5.2];
        let distance = calculate_distance_default(position1, position2);

        assert_float_eq(distance, 170.3, 0.04);
    }

    #[test]
    fn test_calculate_edges_dot_product_1() {
        let position1 = [0.0, 0.0, 0.0];
        let position2 = [1.0, 0.0, 0.0];
        let position3 = [0.0, 1.0, 0.0];
        let position4 = [0.0, 0.0, 1.0];
        let dot_product =
            calculate_edges_dot_product_default(position1, position2, position3, position4);

        assert_eq!(dot_product, 0.0);
    }

    #[test]
    fn test_calculate_edges_dot_product_2() {
        let position1 = [2.3, -2.5, 3.6];
        let position2 = [1.8, 2.1, -4.1];
        let position3 = [3.5, 6.2, -4.2];
        let position4 = [4.3, 1.3, -2.3];
        let dot_product =
            calculate_edges_dot_product_default(position1, position2, position3, position4);

        assert_float_eq(dot_product, -37.57, 0.01);
    }

    #[test]
    fn test_calculate_edges_dot_product_3() {
        let position1 = [6.335, 1.262, 4.326];
        let position2 = [1.3, 0.0, 1.2];
        let position3 = [3.66, -1.0, -2.0];
        let position4 = [1.2, 2.445, 0.05];
        let dot_product =
            calculate_edges_dot_product_default(position1, position2, position3, position4);

        assert_float_eq(dot_product, 1.63, 0.01);
    }
}
