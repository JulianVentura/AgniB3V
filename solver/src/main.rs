use anyhow::Result;
use solver::fem;
use std::env;

use log::error;

/// This function takes command line arguments for a directory path and a method, and then runs the solver
/// using the specified method and the directory.
///
/// Returns:
///
/// The `run()` function is returning a `Result` type.
fn run() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    if args.len() != 3 {
        fem::error::err!("Usage: {} <directory_path> <method>", args[0]);
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
