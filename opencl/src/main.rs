pub mod examples;
pub mod fem;

use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    //examples::run_example()?;
    examples::cilinder_vtk()?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
