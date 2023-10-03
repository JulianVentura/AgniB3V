use super::structures::Vector;

#[derive(Clone, Debug)]
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

impl Default for Point {
    fn default() -> Self {
        Point {
            global_id: 0,                                       // Default global_id value
            local_id: 0,                                        // Default local_id value
            position: Vector::from_row_slice(&[0.0, 0.0, 0.0]), // Default position
            temperature: 0.0,                                   // Default temperature value
        }
    }
}
