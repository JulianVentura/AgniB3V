pub mod examples;
pub mod fem;
use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    examples::test_square_only_temperature(true)?;
    println!("-------------------");
    //examples::test_square_only_temperature_rotated_90(true)?;
    println!("-------------------");
    examples::test_square_only_temperature_translated(true)?;
    println!("-------------------");
    examples::test_square_only_temperature_rotated_45_xy(true)?;
    println!("-------------------");
    examples::test_square_only_temperature_rotated_45_xz(true)?;
    println!("-------------------");
    examples::test_square_only_temperature_deformated(true)?;

    // examples::test_square_only_heat(false)?;
    //examples::test_2d_plane()?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
