pub mod examples;
pub mod fem;
use anyhow::Result;
use log::error;

fn run() -> Result<()> {
    //examples::test_2d_plane()?;
    //examples::test_non_tilted_3d_plane()?;
    examples::test_plane_0_2()?;

    Ok(())
}

fn main() {
    env_logger::init();
    match run() {
        Ok(_) => println!("Ok"),
        Err(e) => error!("{e:?}"),
    };
}
