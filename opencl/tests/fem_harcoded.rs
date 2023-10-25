use anyhow::Result;
use opencl::fem::{
    element::Element,
    engine::Solver,
    engine::{FEMEngine, FEMOrbitParameters, FEMParameters},
    explicit_solver::ExplicitSolver,
    point::Point,
    structures::Vector,
};

#[ignore]
#[test]
pub fn test_square_only_temperature() -> Result<()> {
    let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::from_row_slice(&[1.0, 0.0, 0.0]), 283.0, 1, 0);
    let p3 = Point::new(Vector::from_row_slice(&[1.0, 1.0, 0.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::from_row_slice(&[0.0, 1.0, 0.0]), 273.0, 3, 0);

    let e1 = Element::basic(p1.clone(), p2.clone(), p3.clone(), 0.0, 2);
    let e2 = Element::basic(p1.clone(), p3.clone(), p4.clone(), 0.0, 2);

    let time_step = 1.0;
    let snapshot_period = 1.0;
    let simulation_time = 5.0;

    let solver = Solver::Explicit(ExplicitSolver::new(&vec![e1, e2]));
    let mut engine = FEMEngine::new(
        FEMParameters {
            simulation_time,
            time_step,
            snapshot_period,
            orbit: FEMOrbitParameters {
                betha: 0.1,
                altitude: 2000.0,
                orbit_period: 100.0,
            },
        },
        solver,
    );

    let temp_results = engine.run()?;

    //Theorical check needed
    let results = [
        [273.00, 283.00, 273.00, 273.00],
        [273.59, 281.24, 273.59, 272.41],
        [273.96, 279.97, 273.96, 272.17],
        [274.21, 279.02, 274.21, 272.14],
        [274.37, 278.30, 274.37, 272.22],
        [274.47, 277.73, 274.47, 272.37],
        [274.54, 277.28, 274.54, 272.55],
        [274.59, 276.92, 274.59, 272.74],
        [274.61, 276.62, 274.61, 272.92],
        [274.63, 276.37, 274.63, 273.10],
        [274.64, 276.15, 274.64, 273.27],
        [274.65, 275.97, 274.65, 273.42],
        [274.66, 275.81, 274.66, 273.56],
        [274.66, 275.67, 274.66, 273.69],
        [274.66, 275.55, 274.66, 273.80],
        [274.66, 275.44, 274.66, 273.90],
        [274.67, 275.35, 274.67, 273.99],
        [274.67, 275.27, 274.67, 274.07],
        [274.67, 275.20, 274.67, 274.14],
        [274.67, 275.14, 274.67, 274.20],
        [274.67, 275.08, 274.67, 274.25],
    ];

    let accepted_error = 0.02;
    let mut step = 0;
    for temp in temp_results.iter() {
        for (i, val) in temp.iter().enumerate() {
            assert!(
                (val - results[step][i]).abs() < accepted_error,
                "data {:?} is not equal to result {:?}",
                val,
                &results[step][i]
            );
        }
        step += 1;
    }

    Ok(())
}

#[ignore]
#[test]
pub fn test_square_only_heat() -> Result<()> {
    let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::from_row_slice(&[1.0, 0.0, 0.0]), 273.0, 1, 0);
    let p3 = Point::new(Vector::from_row_slice(&[0.0, 1.0, 0.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::from_row_slice(&[1.0, 1.0, 0.0]), 273.0, 3, 0);

    let e1 = Element::basic(p1.clone(), p2.clone(), p3.clone(), 1000.0, 2);
    let e2 = Element::basic(p2.clone(), p4.clone(), p3.clone(), 1000.0, 2);

    let time_step = 10.0;
    let snapshot_period = 10.0;
    let simulation_time = 600.0;

    let solver = Solver::Explicit(ExplicitSolver::new(&vec![e1, e2]));
    let mut engine = FEMEngine::new(
        FEMParameters {
            simulation_time,
            time_step,
            snapshot_period,
            orbit: FEMOrbitParameters {
                betha: 0.1,
                altitude: 2000.0,
                orbit_period: 100.0,
            },
        },
        solver,
    );

    let temp_results = engine.run()?;

    //This is theorically checked
    let accepted_error = 0.02;
    let mut prev_temp = &temp_results[0];
    for temp in temp_results[1..].iter() {
        for (i, val) in temp.iter().enumerate() {
            assert!(
                (val - prev_temp[i] - 0.04).abs() < accepted_error,
                "data {:?} is not 0.04 greater than previous {:?}",
                val,
                prev_temp
            );
        }
        prev_temp = &temp;
    }

    Ok(())
}

#[test]
pub fn test_rotations_and_deformations() -> Result<()> {
    let initial_temperatures = create_initial_example()?;
    let translated_temperatures = create_translated_example()?;
    let rotated_xy_temperatures = create_rotated_xy_example()?;
    let rotated_xz_temperatures = create_rotated_xz_example()?;
    let deformated_temperatures = create_deformated_example()?;

    let accepted_error = 1.5; //There can be difference in rounding, rigth know this is the maximum difference
    let mut step = 0;
    for temp in initial_temperatures.iter() {
        for (i, val) in temp.iter().enumerate() {
            assert!(
                (val - translated_temperatures[step][i]).abs() < accepted_error,
                "data {:?} is not equal to translated {:?}",
                val,
                translated_temperatures[step]
            );
            assert!(
                (val - rotated_xy_temperatures[step][i]).abs() < accepted_error,
                "data {:?} is not equal to rotated_xy {:?}",
                val,
                rotated_xy_temperatures[step]
            );
            assert!(
                (val - rotated_xz_temperatures[step][i]).abs() < accepted_error,
                "data {:?} is not equal to rotated_xz {:?}",
                val,
                rotated_xz_temperatures[step]
            );
            assert!(
                (val - deformated_temperatures[step][i]).abs() < accepted_error,
                "data {:?} is not equal to deformated {:?}",
                val,
                deformated_temperatures[step]
            );
        }
        step += 1;
    }

    Ok(())
}

fn create_example(p1: Point, p2: Point, p3: Point, p4: Point) -> Result<Vec<Vector>> {
    let e1 = Element::basic(p1.clone(), p2.clone(), p3.clone(), 0.0, 2);
    let e2 = Element::basic(p1.clone(), p3.clone(), p4.clone(), 0.0, 2);

    let time_step = 1.0;
    let snapshot_period = 1.0;
    let simulation_time = 20.0;

    let solver = Solver::Explicit(ExplicitSolver::new(&vec![e1, e2]));
    let mut engine = FEMEngine::new(
        FEMParameters {
            simulation_time,
            time_step,
            snapshot_period,
            orbit: FEMOrbitParameters {
                betha: 0.1,
                altitude: 2000.0,
                orbit_period: 100.0,
            },
        },
        solver,
    );

    Ok(engine.run()?)
}

fn create_initial_example() -> Result<Vec<Vector>> {
    let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::from_row_slice(&[1.0, 0.0, 0.0]), 283.0, 1, 0);
    let p3 = Point::new(Vector::from_row_slice(&[1.0, 1.0, 0.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::from_row_slice(&[0.0, 1.0, 0.0]), 273.0, 3, 0);

    Ok(create_example(p1, p2, p3, p4)?)
}

fn create_translated_example() -> Result<Vec<Vector>> {
    let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 1.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::from_row_slice(&[1.0, 0.0, 1.0]), 283.0, 1, 0);
    let p3 = Point::new(Vector::from_row_slice(&[1.0, 1.0, 1.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::from_row_slice(&[0.0, 1.0, 1.0]), 273.0, 3, 0);

    Ok(create_example(p1, p2, p3, p4)?)
}

fn create_rotated_xy_example() -> Result<Vec<Vector>> {
    let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::from_row_slice(&[0.525, 0.85, 0.0]), 283.0, 1, 0);
    let p3 = Point::new(Vector::from_row_slice(&[-0.325, 1.325, 0.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::from_row_slice(&[-0.85, 0.525, 0.0]), 273.0, 3, 0);

    Ok(create_example(p1, p2, p3, p4)?)
}

fn create_rotated_xz_example() -> Result<Vec<Vector>> {
    let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::from_row_slice(&[0.525, 0.0, -0.85]), 283.0, 1, 0);
    let p3 = Point::new(Vector::from_row_slice(&[0.525, 1.0, -0.85]), 273.0, 2, 0);
    let p4 = Point::new(Vector::from_row_slice(&[0.0, 1.0, 0.0]), 273.0, 3, 0);

    Ok(create_example(p1, p2, p3, p4)?)
}

fn create_deformated_example() -> Result<Vec<Vector>> {
    let p1 = Point::new(Vector::from_row_slice(&[0.0, 0.0, 0.0]), 273.0, 0, 0);
    let p2 = Point::new(Vector::from_row_slice(&[1.0, 0.0, 0.0]), 283.0, 1, 0);
    let p3 = Point::new(Vector::from_row_slice(&[1.0, 1.0, 0.0]), 273.0, 2, 0);
    let p4 = Point::new(Vector::from_row_slice(&[0.5, 0.5, 0.7071]), 273.0, 3, 0);

    Ok(create_example(p1, p2, p3, p4)?)
}
