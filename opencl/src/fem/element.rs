use super::point::Point;
use rulinalg::{matrix, vector};

type Matrix = matrix::Matrix<f32>;
type Vector = vector::Vector<f32>;

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
        //TODO: Add 3D

        let mut area = p1.position[0] * (p2.position[1] - p3.position[1]);
        area += p2.position[0] * (p3.position[1] - p1.position[1]);
        area += p3.position[0] * (p1.position[1] - p2.position[1]);

        area = area.abs() / 2.0;

        area
    }

    fn calculate_sqr_distance(p1: &Point, p2: &Point) -> f32 {
        //Calculate the distance between two points squared
        //TODO: Add 3D

        let mut distance = (p1.position[0] - p2.position[0]).powi(2);
        distance += (p1.position[1] - p2.position[1]).powi(2);

        distance
    }

    fn calculate_dot_product(fixed: &Point, start: &Point, end: &Point) -> f32 {
        //Calculate the dot product between two edges
        //TODO: Add 3D

        let edge1: Vector = Vector::new([
            fixed.position[0] - start.position[0],
            fixed.position[1] - start.position[1],
        ]);
        let edge2: Vector = Vector::new([
            end.position[0] - fixed.position[0],
            end.position[1] - fixed.position[1],
        ]);
        let mut dot_product = edge1[0] * edge2[0];
        dot_product += edge1[1] * edge2[1];

        dot_product
    }

    fn check_point_length(point: &Point) {
        //TODO: Add 3D
        //TODO: Add error handling
        if point.position.size() != 2 {
            panic!("Point length is not 2");
        }
    }

    fn calculate_k(p1: &Point, p2: &Point, p3: &Point, conductivity: f32, area: f32) -> Matrix {
        let k11 = Self::calculate_sqr_distance(&p2, &p3);
        let k22 = Self::calculate_sqr_distance(&p1, &p3);
        let k33 = Self::calculate_sqr_distance(&p1, &p2);

        let k12 = Self::calculate_dot_product(&p3, &p2, &p1);
        let k13 = Self::calculate_dot_product(&p2, &p1, &p3);
        let k23 = Self::calculate_dot_product(&p1, &p3, &p2);

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
