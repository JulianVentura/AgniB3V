use super::point::Point;
use rulinalg::{matrix};

type Matrix = matrix::Matrix<f32>;

pub struct Element {
    pub p1: Point,
    pub p2: Point,
    pub p3: Point,
    pub k: Matrix,
    pub m: Matrix,
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
        let area: f32 = 4.0; //TODO

        p1.set_local_id(1);
        p2.set_local_id(2);
        p3.set_local_id(3);

        //TODO: Check vector length
        let b1: f32 = p2.position[1] - p3.position[1];
        let b2: f32 = p3.position[1] - p1.position[1];
        let b3: f32 = p1.position[1] - p2.position[1];
        let c1: f32 = p3.position[0] - p2.position[0];
        let c2: f32 = p1.position[0] - p3.position[0];
        let c3: f32 = p2.position[0] - p1.position[0];

        let mut k = matrix![
            //Row 1
            b1 * b1 + c1 * c1,
            b1 * b2 + c1 * c2,
            b1 * b3 + c1 * c3;
            //Row 2
            b1 * b2 + c1 * c2,
            b2 * b2 + c2 * c2,
            b2 * b3 + c2 * c3;
            //Row 3
            b1 * b3 + c1 * c3,
            b2 * b3 + c2 * c3,
            b3 * b3 + c3 * c3
        ];

        k = k * (conductivity / (4.0 * area));

        let mut m = matrix![
            2.0, 1.0, 1.0; //Row 1
            1.0, 2.0, 1.0; //Row 2
            1.0, 1.0, 2.0 //Row 3
        ];

        //Thickness is necessary in order to get a volume
        m = m * (area * specific_heat * density * thickness / 12.0);

        Element {
            p1,
            p2,
            p3,
            k,
            m,
            conductivity,
            density,
            specific_heat,
            thickness,
            area,
            generated_heat,
        }
    }
}
