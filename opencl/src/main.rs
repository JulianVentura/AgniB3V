pub mod fem;
pub mod gpu;
use std::env;

use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        eprintln!("Usage: {} <directory_path> <method>", args[0]);
        std::process::exit(1); //TODO: Change this to return an error
    }

    let directory_path = &args[1];
    let method = &args[2];

    fem::executor::run_solver(directory_path, method)?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
