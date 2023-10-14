pub mod examples;
pub mod fem;
use std::collections::HashMap;

use anyhow::Result;
use fem::parser::fem_problem_from_vtk;
use log::error;

fn run() -> Result<()> {
    //examples::run_example()?;
    examples::vtk_test()?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
