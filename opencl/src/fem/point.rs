use rulinalg::vector;

type Vector = vector::Vector<f32>;

#[derive(Clone)]
pub struct Point {
    pub global_id: u32,
    pub local_id: u32,
    pub position: Vector,
    pub temperature: f32,
}

impl Point {
    pub fn new(position: Vector, temperature: f32, global_id: u32, local_id: u32) -> Self {
        Point {
            position,
            temperature,
            global_id,
            local_id,
        }
    }

    pub fn set_local_id(&mut self, id: u32) {
        self.local_id = id;
    }
}
