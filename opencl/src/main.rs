pub mod fem;
use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    fem::examples::test_square();
    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
