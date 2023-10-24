pub mod examples;
pub mod fem;
use std::env;

use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 4 {
        eprintln!("Usage: {} vtk_path json_path results_name", args[0]);
        std::process::exit(1);
    }

    let vtk_path = &args[1];
    let json_path = &args[2];
    let results_name = &args[3];

    fem::executor::run_solver(vtk_path, json_path, results_name)?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
