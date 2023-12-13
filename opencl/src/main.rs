use anyhow::Result;
use opencl::fem;
use std::env;

use log::error;

fn run() -> Result<()> {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        fem::error::err!("Usage: <executable> <config_path>");
    }

    let config_path = &args[1];

    fem::executor::run_solver(config_path)?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
