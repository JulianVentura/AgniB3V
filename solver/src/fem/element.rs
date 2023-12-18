use crate::err;

use super::constants::BOLTZMANN;
use super::point::Point;
use super::structures::{Matrix, Vector};
use anyhow::Result;

#[derive(Debug)]
pub struct Element {
    pub p1: Point,
    pub p2: Point,
    pub p3: Point,
    pub k: Matrix,
    pub m: Matrix,
    pub e: Matrix,
    pub f: Vec<Vector>,
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
    pub earth_ir: Vec<f64>,
    pub earth_albedo: Vec<f64>,
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
        earth_ir: f64,
        albedo_factor: f64,
        generated_heat: f64,
        two_side_radiation: bool,
        orbit_divisions: &Vec<(usize, bool)>,
    ) -> Result<Self> {
        Self::check_point_length(&p1)?;
        Self::check_point_length(&p2)?;
        Self::check_point_length(&p3)?;

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

        let e = Self::calculate_e(area, properties.alpha_ir, two_side_radiation);

        let f = Self::calculate_f_array(
            area,
            &properties,
            &factors,
            solar_intensity,
            earth_ir,
            albedo_factor,
            generated_heat,
            orbit_divisions,
        );

        Ok(Element {
            p1,
            p2,
            p3,
            k,
            m,
            e,
            f,
            alpha_sun: properties.alpha_sun,
            alpha_ir: properties.alpha_ir,
            view_factors: factors.elements,
            area,
        })
    }

    pub fn basic(
        p1: Point,
        p2: Point,
        p3: Point,
        generated_heat: f64,
        n_elements: usize,
    ) -> Result<Self> {
        let conductivity = 237.0;
        let density = 2700.0;
        let specific_heat = 900.0;
        let thickness = 0.01;
        let alpha_sun = 1.0;
        let alpha_ir = 1.0;
        let solar_intensity = 300.0;
        let earth_ir = 225.0;
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
            earth_ir: vec![1.0],
            earth_albedo: vec![1.0],
            sun: 1.0,
            elements: vec![0.1f64; n_elements],
        };

        let divisions = vec![(0, false)];

        Self::new(
            p1,
            p2,
            p3,
            props,
            factors,
            solar_intensity,
            earth_ir,
            albedo_factor,
            generated_heat,
            false,
            &divisions,
        )
    }

    /// The function calculates the area of a triangle using the cross product of two vectors.
    ///
    /// Arguments:
    ///
    /// * `p1`: The parameter `p1` is a reference to a `Point` object.
    /// * `p2`: The parameter `p2` represents the second point in a triangle.
    /// * `p3`: The `p3` parameter represents the third point of a triangle.
    ///
    /// Returns:
    ///
    /// The function `calculate_area` returns a `f64` value, which represents the calculated area.
    fn calculate_area(p1: &Point, p2: &Point, p3: &Point) -> f64 {
        let ab = &p2.position - &p1.position;
        let ac = &p3.position - &p1.position;

        //Cross product
        let a: f64 = ab[1] * ac[2] - ab[2] * ac[1];
        let b: f64 = ab[2] * ac[0] - ab[0] * ac[2];
        let c: f64 = ab[0] * ac[1] - ab[1] * ac[0];

        (a * a + b * b + c * c).sqrt() / 2.0
    }

    /// The function calculates the squared distance between two points in a three-dimensional space.
    ///
    /// Arguments:
    ///
    /// * `p1`: A reference to a Point struct representing the first point.
    /// * `p2`: The `p2` parameter is a reference to a `Point` object.
    ///
    /// Returns:
    ///
    /// The function `calculate_sqr_distance` returns a `f64` value, which represents the squared
    /// distance between two points.
    fn calculate_sqr_distance(p1: &Point, p2: &Point) -> f64 {
        let mut distance = (p1.position[0] - p2.position[0]).powi(2);
        distance += (p1.position[1] - p2.position[1]).powi(2);
        distance += (p1.position[2] - p2.position[2]).powi(2);

        distance
    }

    /// The function calculates the dot product between two edges defined by their endpoints.
    ///
    /// Arguments:
    ///
    /// * `a`: The parameter `a` is a tuple containing two references to `Point` objects. The first
    /// element of the tuple (`a.0`) represents the starting point of the first edge, and the second
    /// element (`a.1`) represents the ending point of the first edge.
    ///
    /// Returns:
    ///
    /// The function `edges_dot_product` returns a `f64` value, which is the dot product between two
    /// edges.
    fn edges_dot_product(a: (&Point, &Point), b: (&Point, &Point)) -> f64 {
        //Calculate the dot product between two edges
        let edge1 = &a.1.position - &a.0.position;
        let edge2 = &b.1.position - &b.0.position;

        edge1.dot(&edge2)
    }

    /// The function `check_point_length` checks if a point has the correct dimensionality.
    ///
    /// Arguments:
    ///
    /// * `point`: A reference to a `Point` object.
    fn check_point_length(point: &Point) -> Result<()> {
        if point.position.len() != 3 {
            err!("Point with wrong dimensionality");
        }

        Ok(())
    }

    /// The function calculates the conductivity matrix for a given set of points, conductivity, area,
    /// and thickness.
    ///
    /// Arguments:
    ///
    /// * `p1`: The parameter `p1` represents the first point in a 3D coordinate system. It is of
    /// type `Point`, which is a custom data structure that holds the coordinates of a point.
    /// * `p2`: The parameter `p2` represents the coordinates of the second point in a three-point
    /// system.
    /// * `p3`: p3 is a reference to a Point object.
    /// * `conductivity`: The conductivity parameter represents the thermal conductivity of the
    /// material. It is a measure of how well the material conducts heat.
    /// * `area`: The parameter "area" represents the cross-sectional area of the material through which
    /// heat is being conducted. It is a measure of the size of the surface through which heat is
    /// flowing.
    /// * `thickness`: The "thickness" parameter represents the thickness of the material through which
    /// heat is being conducted. It is a scalar value that indicates the distance between the two
    /// surfaces of the material.
    ///
    /// Returns:
    ///
    /// The function `calculate_k` returns a `Matrix` object.
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

        k = k * thickness * conductivity / (4.0 * area);
        k
    }

    /// The function calculates the m matrix for a given area, specific heat, density, and thickness.
    ///
    /// Arguments:
    ///
    /// * `area`: The parameter "area" represents the surface area of the object in square units.
    /// * `specific_heat`: Specific heat is the amount of heat energy required to raise the temperature
    /// of a substance by a certain amount.
    /// * `density`: Density refers to the mass per unit volume of a substance. In this context, it
    /// represents the density of the material being considered for the calculation.
    /// * `thickness`: The "thickness" parameter represents the thickness of the material.
    ///
    /// Returns:
    ///
    /// The function `calculate_m` returns a matrix of type `Matrix`.
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

        m = m * (area * specific_heat * density * thickness / 12.0);

        m
    }

    /// The function calculates the e matrix based on the area, alpha, and whether two-side
    /// radiation is considered.
    ///
    /// Arguments:
    ///
    /// * `area`: The `area` parameter represents the surface area of the element for which you want to
    /// calculate the radiation loss.
    /// * `alpha`: Alpha is the absorptivity of the material. It represents the fraction of incident
    /// radiation that is absorbed by the material.
    /// * `two_side_radiation`: The parameter `two_side_radiation` is a boolean value that indicates
    /// whether the radiation loss occurs on both sides of the element or only in the element's normal
    /// direction. If `two_side_radiation` is `true`, it means that the radiation loss is doubled
    ///
    /// Returns:
    ///
    /// The function `calculate_e` returns a `Matrix` object.
    fn calculate_e(area: f64, alpha: f64, two_side_radiation: bool) -> Matrix {
        let factor = match two_side_radiation {
            true => 2.0,  //Doubles the radiation loss
            false => 1.0, //Radiation loss only in the element normal direction
        };

        let e = Matrix::from_row_slice(
            3,
            3,
            &[
                1.0, 0.0, 0.0, //
                0.0, 1.0, 0.0, //
                0.0, 0.0, 1.0, //
            ],
        );

        (factor * BOLTZMANN * alpha * area / 3.0) * e
    }

    /// The function `calculate_f_array` calculates the F values for each orbit division based on
    /// various input parameters.
    ///
    /// Returns:
    ///
    /// The function `calculate_f_array` returns a `Vec<Vector>`.
    fn calculate_f_array(
        area: f64,
        properties: &MaterialProperties,
        factors: &ViewFactors,
        solar_intensity: f64,
        earth_ir: f64,
        albedo_factor: f64,
        generated_heat: f64,
        orbit_divisions: &Vec<(usize, bool)>,
    ) -> Vec<Vector> {
        orbit_divisions
            .iter()
            .map(|(idx, in_eclipse)| {
                Self::calculate_f(
                    area,
                    &properties,
                    &factors,
                    solar_intensity,
                    earth_ir,
                    albedo_factor,
                    generated_heat,
                    factors.earth_albedo[*idx],
                    factors.earth_ir[*idx],
                    *in_eclipse,
                )
            })
            .collect()
    }

    /// The function calculates the magnitude of the heat generated by a system based on various
    /// factors.
    ///
    /// Arguments:
    ///
    /// * `area`: The `area` parameter represents the surface area of the object for which the heat flux
    /// is being calculated.
    /// * `properties`: The `properties` parameter is of type `MaterialProperties` and contains the
    /// properties of the material being considered.
    /// * `factors`: The `factors` parameter is of type `ViewFactors` and represents the view factors
    /// between the surface and other objects in the environment.
    /// * `solar_intensity`: The solar_intensity parameter represents the intensity of solar radiation
    /// incident on the surface. It is a measure of the amount of solar energy per unit area.
    /// * `earth_ir`: The parameter `earth_ir` represents the intensity of infrared radiation emitted by
    /// the Earth.
    /// * `albedo_factor`: The `albedo_factor` parameter represents the factor by which the earth reflect Sun radiation.
    /// It is multiplied with the solar intensity and the earth view factor for albedo to calculate the albedo contribution.
    /// * `generated_heat`: The `generated_heat` parameter represents the amount of heat generated by
    /// the element. It is a `f64` (floating-point number) value.
    /// * `earth_view_factor_albedo`: The parameter `earth_view_factor_albedo` represents the view
    /// factor between the surface and the Earth for the albedo component. It is used to calculate the
    /// contribution of reflected solar radiation from the Earth's surface.
    /// * `earth_view_factor_ir`: The parameter `earth_view_factor_ir` represents the view factor
    /// between the surface and the Earth for infrared radiation. It is used to calculate the
    /// contribution of Earth's infrared radiation.
    /// * `in_eclipse`: A boolean value indicating whether the element is in eclipse or not.
    ///
    /// Returns:
    ///
    /// a Vector.
    fn calculate_f(
        area: f64,
        properties: &MaterialProperties,
        factors: &ViewFactors,
        solar_intensity: f64,
        earth_ir: f64,
        albedo_factor: f64,
        generated_heat: f64,
        earth_view_factor_albedo: f64,
        earth_view_factor_ir: f64,
        in_eclipse: bool,
    ) -> Vector {
        let f = Vector::from_row_slice(&[1.0, 1.0, 1.0]);

        let solar = match in_eclipse {
            true => 0.0,
            false => properties.alpha_sun * solar_intensity * factors.sun,
        };
        let ir = properties.alpha_ir * earth_view_factor_ir * earth_ir;
        let albedo =
            properties.alpha_sun * solar_intensity * albedo_factor * earth_view_factor_albedo;

        let magnitude = (generated_heat + solar + ir + albedo) * area / 3.0;

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

    #[test]
    fn test_calculate_f_array_1() {
        use super::{MaterialProperties, ViewFactors};
        let m_props = MaterialProperties {
            conductivity: 1.0,
            density: 1.0,
            specific_heat: 1.0,
            thickness: 1.0,
            alpha_sun: 1.0,
            alpha_ir: 1.0,
        };

        let vf = ViewFactors {
            earth_ir: vec![1.0, 0.5, 1.0],
            earth_albedo: vec![1.0, 0.4, 1.0],
            sun: 1.0,
            elements: vec![1.0, 1.0, 1.0],
        };

        let divisions = vec![(0, false), (0, true), (1, true), (2, true), (2, false)];

        let f = Element::calculate_f_array(1.0, &m_props, &vf, 1361.0, 225.0, 1.0, 0.0, &divisions);

        let f_expected = [
            Vector::from_row_slice(&[982.33, 982.33, 982.33]),
            Vector::from_row_slice(&[528.66, 528.66, 528.66]),
            Vector::from_row_slice(&[218.963, 218.963, 218.963]),
            Vector::from_row_slice(&[528.66, 528.66, 528.66]),
            Vector::from_row_slice(&[982.33, 982.33, 982.33]),
        ];

        for (f_r, f_exp) in f.iter().zip(f_expected) {
            for (x, y) in f_r.iter().zip(f_exp.iter()) {
                assert_float_eq(*x, *y, 0.01);
            }
        }
    }

    #[test]
    fn test_calculate_f_array_2() {
        use super::{MaterialProperties, ViewFactors};
        let m_props = MaterialProperties {
            conductivity: 1.0,
            density: 1.0,
            specific_heat: 1.0,
            thickness: 1.0,
            alpha_sun: 1.0,
            alpha_ir: 1.0,
        };

        let vf = ViewFactors {
            earth_ir: vec![1.0, 0.5, 1.0],
            earth_albedo: vec![1.0, 0.4, 1.0],
            sun: 1.0,
            elements: vec![1.0, 1.0, 1.0],
        };

        let divisions = vec![(0, true), (0, false), (1, false), (2, false), (2, true)];

        let f = Element::calculate_f_array(1.0, &m_props, &vf, 1361.0, 225.0, 1.0, 0.0, &divisions);

        let f_expected = [
            Vector::from_row_slice(&[528.66, 528.66, 528.66]),
            Vector::from_row_slice(&[982.33, 982.33, 982.33]),
            Vector::from_row_slice(&[672.63, 672.63, 672.63]),
            Vector::from_row_slice(&[982.33, 982.33, 982.33]),
            Vector::from_row_slice(&[528.66, 528.66, 528.66]),
        ];

        for (f_r, f_exp) in f.iter().zip(f_expected) {
            for (x, y) in f_r.iter().zip(f_exp.iter()) {
                assert_float_eq(*x, *y, 0.01);
            }
        }
    }
}
