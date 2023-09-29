use super::{element::Element, engine::FEMEngine, point::Point};
use rulinalg::vector;

pub fn test_square() {
    let p1 = Point::new(vector![0.0, 0.0], 0.0, 1, 0);
    let p2 = Point::new(vector![1.0, 0.0], 10.0, 2, 0);
    let p3 = Point::new(vector![1.0, 1.0], 0.0, 3, 0);
    let p4 = Point::new(vector![0.0, 1.0], 0.0, 4, 0);

    let e1 = Element::new(p1.clone(), p2.clone(), p3.clone(), 1.0, 1.0, 1.0, 1.0, 0.0);
    let e2 = Element::new(p1.clone(), p3.clone(), p4.clone(), 1.0, 1.0, 1.0, 1.0, 0.0);

    let time_step = 0.01;
    let simulation_time = 1.0;
    let mut engine = FEMEngine::new(simulation_time, time_step, vec![e1, e2]);

    let temp_results = engine.run().unwrap();

    let mut step = 0.0;
    for temp in temp_results.iter() {
        println!("Time: {:.2} , Temp: {:?}", (time_step * step), temp.data());
        step += 1.0;
    }
}
