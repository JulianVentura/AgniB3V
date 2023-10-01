use super::point::Point;
use super::structures::{Matrix, Vector};
use rulinalg::{matrix, vector};

#[derive(Debug)]
pub struct Element {
    pub p1: Point,
    pub p2: Point,
    pub p3: Point,
    pub k: Matrix,
    pub m: Matrix,
    pub f: Vector,
    pub conductivity: f32,
    pub density: f32,
    pub specific_heat: f32,
    pub thickness: f32,
    pub area: f32,
    pub generated_heat: f32,
}

impl Element {
    pub fn new(
        mut p1: Point,
        mut p2: Point,
        mut p3: Point,
        conductivity: f32,
        density: f32,
        specific_heat: f32,
        thickness: f32,
        generated_heat: f32,
    ) -> Self {
        Self::check_point_length(&p1);
        Self::check_point_length(&p2);
        Self::check_point_length(&p3);

        let area: f32 = Self::calculate_area(&p1, &p2, &p3);

        p1.set_local_id(1);
        p2.set_local_id(2);
        p3.set_local_id(3);

        let k = Self::calculate_k(&p1, &p2, &p3, conductivity, area);

        let m = Self::calculate_m(area, specific_heat, density, thickness);

        let f = Self::calculate_f(area, generated_heat);

        Element {
            p1,
            p2,
            p3,
            k,
            m,
            f,
            conductivity,
            density,
            specific_heat,
            thickness,
            area,
            generated_heat,
        }
    }

    fn calculate_area(p1: &Point, p2: &Point, p3: &Point) -> f32 {
        let ab = &p2.position - &p1.position;
        let ac = &p3.position - &p1.position;

        //Cross product
        let a: f32 = ab[1] * ac[2] - ab[2] * ac[1];
        let b: f32 = ab[2] * ac[0] - ab[0] * ac[2];
        let c: f32 = ab[0] * ac[1] - ab[1] * ac[0];

        (a * a + b * b + c * c).sqrt() / 2.0
    }

    fn calculate_sqr_distance(p1: &Point, p2: &Point) -> f32 {
        let mut distance = (p1.position[0] - p2.position[0]).powi(2);
        distance += (p1.position[1] - p2.position[1]).powi(2);
        distance += (p1.position[2] - p2.position[2]).powi(2);

        distance
    }

    fn edges_dot_product(a: (&Point, &Point), b: (&Point, &Point)) -> f32 {
        //Calculate the dot product between two edges
        let edge1 = &a.1.position - &a.0.position;
        let edge2 = &b.1.position - &b.0.position;

        edge1.dot(&edge2)
    }

    fn check_point_length(point: &Point) {
        //TODO: Add error handling
        if point.position.size() != 3 {
            panic!("Point length is not 3");
        }
    }

    fn calculate_k(p1: &Point, p2: &Point, p3: &Point, conductivity: f32, area: f32) -> Matrix {
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

        let mut k = matrix![
            //Row 1
            k11,
            k12,
            k13;
            //Row 2
            k21,
            k22,
            k23;
            //Row 3
            k31,
            k32,
            k33
        ];
        k = k * (conductivity / (4.0 * area));
        k
    }

    fn calculate_m(area: f32, specific_heat: f32, density: f32, thickness: f32) -> Matrix {
        let mut m = matrix![
            2.0, 1.0, 1.0; //Row 1
            1.0, 2.0, 1.0; //Row 2
            1.0, 1.0, 2.0 //Row 3
        ];

        //Thickness is necessary in order to get a volume
        m = m * (area * specific_heat * density * thickness / 12.0);

        m
    }

    fn calculate_f(area: f32, generated_heat: f32) -> Vector {
        let mut f = vector![1.0, 1.0, 1.0];

        f = f * (generated_heat * area / 3.0);

        //TODO: Add single node heat source
        // f += [nodo1.heat_source, nodo2.heat_source, nodo3.heat_source]
        //Note: probably that would make each element where that node is part add its heat source, so it would be duplicated

        f
    }
}
