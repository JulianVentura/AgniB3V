pub mod examples;
pub mod fem;
use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    examples::test_square_only_temperature(false)?;
    examples::test_square_only_heat(false)?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
