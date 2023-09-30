pub mod examples;
pub mod fem;
use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    examples::test_square_only_temperature(true)?;
    examples::test_square_only_heat(false)?;
    // let problem = fem::parser::fem_problem_from_csv();
    //
    // println!("{:#?}", problem);

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
