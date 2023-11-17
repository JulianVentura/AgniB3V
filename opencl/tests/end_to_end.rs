use anyhow::Result;
use opencl::fem::executor::run_solver;
use serde::Deserialize;
use std::{fs::remove_dir_all, fs::File, io::BufReader, path::PathBuf};
use vtkio::{
    model::{Attribute, DataSet, Piece},
    IOBuffer, Vtk,
};

#[derive(Deserialize)]
pub struct VTK {
    name: String,
    time: f64,
}

#[derive(Deserialize)]
pub struct VTKSeries {
    files: Vec<VTK>,
}

fn assert_float_eq(value_1: f64, value_2: f64, precision: f64) {
    assert!(
        (value_1 - value_2).abs() < precision,
        "value1 {} != {}",
        value_1,
        value_2
    );
}

fn get_vtk_results(vtk_file: Vtk) -> Vec<f64> {
    if let DataSet::UnstructuredGrid { meta: _, pieces } = vtk_file.data {
        if let Piece::Inline(vtk_piece) = &pieces[0] {
            if let Attribute::DataArray(data_array) = &vtk_piece.data.point[0] {
                if let IOBuffer::F64(vtk_data) = &data_array.data {
                    return vtk_data.to_vec();
                }
            }
        }
    }
    return vec![];
}

fn compare_vtk(file_path1: String, file_path2: String) -> Result<()> {
    let file_path_buf = PathBuf::from(file_path1);
    let vtk_file1 =
        Vtk::import(&file_path_buf).expect(&format!("Failed to load file: {:?}", file_path_buf));

    let file_path_buf2 = PathBuf::from(file_path2);
    let vtk_file2 =
        Vtk::import(&file_path_buf2).expect(&format!("Failed to load file: {:?}", file_path_buf2));

    let vtk_1_results = get_vtk_results(vtk_file1);
    let vtk_2_results = get_vtk_results(vtk_file2);

    assert!(
        vtk_1_results.len() == vtk_2_results.len(),
        "Vtks do not have the same lenght"
    );

    let precision = 0.001;

    for i in 0..vtk_1_results.len() {
        assert_float_eq(vtk_1_results[i], vtk_2_results[i], precision)
    }

    Ok(())
}

fn compare_results(
    actual_results: String,
    new_results: String,
    actual_results_name: String,
    new_results_name: String,
) -> Result<()> {
    let actual_file = format!("{}/{}.vtk.series", actual_results, actual_results_name);
    let new_file = format!("{}/{}.vtk.series", new_results, new_results_name);

    let actual_file_reader =
        BufReader::new(File::open(&actual_file).expect("Couldn't read actual_file"));
    let actual_file_json: VTKSeries =
        serde_json::from_reader(actual_file_reader).expect("Couldn't parse actual_file");

    let new_file_reader = BufReader::new(File::open(&new_file).expect("Couldn't read new_file"));
    let new_file_json: VTKSeries =
        serde_json::from_reader(new_file_reader).expect("Couldn't parse new_file");

    assert!(
        actual_file_json.files.len() == new_file_json.files.len(),
        "Length of results files not equal"
    );

    for i in 0..actual_file_json.files.len() {
        assert_float_eq(
            actual_file_json.files[i].time,
            new_file_json.files[i].time,
            0.01,
        );
        compare_vtk(
            format!("{}/{}", actual_results, actual_file_json.files[i].name),
            format!("{}/{}", new_results, new_file_json.files[i].name),
        )?;
    }

    Ok(())
}

fn run_test_solver(test_number: u32, solver: &str) -> Result<()> {
    let config_path = format!(
        "Unit_tests/Test_{}/test_{}_config_{}.json",
        test_number, test_number, solver
    );
    let actual_results_path = format!(
        "Unit_tests/Test_{}/test_{}_results",
        test_number, test_number
    );
    let results_path = format!("Unit_tests/Test_{}", test_number);
    let new_results_name = format!("test_{}_new", test_number);
    let actual_results_name = format!("test_{}_results", test_number);

    run_solver(&config_path)?;

    compare_results(
        actual_results_path,
        format!("{}/{}_results", results_path, new_results_name),
        actual_results_name,
        format!("{}_results", new_results_name),
    )?;

    remove_dir_all(format!("{}/{}_results", results_path, new_results_name))?;

    Ok(())
}

fn run_test(test_number: u32) -> Result<()> {
    run_test_solver(test_number, "implicit")?;
    //run_test_solver(test_number, "explicit")?;
    run_test_solver(test_number, "gpu")?;
    Ok(())
}

#[test]
pub fn test_conduction_1() -> Result<()> {
    /*
    Only Condcution
    Cube of 1 m x 1 m x 1 m
    Material: Aluminuim, density: 2700 kg/m3, specific heat: 900 J/(K kg), thermal conductivity: 237 W/(K m)
    One of the faces has an initial temperature of 573 K (300 C), the rest 273 K (0 C)
    There are no fluxes
    */

    run_test(1)?;

    Ok(())
}

#[test]
pub fn test_conduction_2() -> Result<()> {
    /*
    Only Condcution
    Cube of 1 m x 1 m x 1 m
    Material: Aluminuim, density: 2700 kg/m3, specific heat: 900 J/(K kg), thermal conductivity: 237 W/(K m)
    Initial temperature of  273 K (0 C)
    Fixed Flux of 200 W/m2
    */

    run_test(2)?;

    Ok(())
}

#[test]
pub fn test_conduction_3() -> Result<()> {
    /*
    Only Condcution
    Cube of 1 m x 1 m x 1 m
    One of the faces has material Copper: density: 8960 kg/m3, specific heat: 385 J/(K kg), thermal conductivity: 400 W/(K m)
    The rest of the cube has material Oak (Wood): density: 700 kg/m3, specific heat: 2300 J/(K kg), thermal conductivity: 0.23 W/(K m)
    The initial temperature of the Copper face is 573 K (300 C)
    The initial temperatures of the Oak faces are 273 K (0 C)
    There are no fluxes
    */

    run_test(3)?;

    Ok(())
}

#[test]
pub fn test_conduction_4() -> Result<()> {
    /*
    Only Condcution
    Cube of 1 m x 1 m x 1 m
    One of the faces has material Copper: density: 8960 kg/m3, specific heat: 385 J/(K kg), thermal conductivity: 400 W/(K m)
    The rest of the cube has material Aluminuim, density: 2700 kg/m3, specific heat: 900 J/(K kg), thermal conductivity: 237 W/(K m)
    The initial temperature of the Copper face is 573 K (300 C)
    The initial temperatures of the Aluminium faces are 273 K (0 C)
    There are no fluxes
    */

    run_test(4)?;

    Ok(())
}

#[test]
pub fn test_conduction_5() -> Result<()> {
    /*
    Only Condcution
    Cube of 1 m x 1 m x 1 m
    One of the faces has material Copper: density: 8960 kg/m3, specific heat: 385 J/(K kg), thermal conductivity: 400 W/(K m)
    The rest of the cube has material Oak (Wood): density: 700 kg/m3, specific heat: 2300 J/(K kg), thermal conductivity: 0.23 W/(K m)
    Initial temperature of  273 K (0 C)
    Fixed Flux of 100 W/m2
    */

    run_test(5)?;

    Ok(())
}

#[test]
pub fn test_radiation_1() -> Result<()> {
    /*
    Only Radiation between elements
    Two planes of 1000 m x 1000 m x 0.001 m, separated by 0.1 m
    Both planes have density: 2700 kg/m3, specific heat: 897 J/(K kg), thermal conductivity: 0 W/(K m), alphaIR = 1.0
    Initial temperature of plane 1: 500 K
    Initial temperature of plane 2: 300 K
    */

    run_test(6)?;

    Ok(())
}

#[test]
pub fn test_radiation_2() -> Result<()> {
    /*
    Only Radiation between elements
    Two planes of 1000 m x 1000 m x 0.001 m, separated by 0.1 m
    Both planes have density: 2700 kg/m3, specific heat: 897 J/(K kg), thermal conductivity: 0 W/(K m)
    Plane 1 has alphaIR = 0.7
    Plane 2 has alphaIR = 1.0
    Initial temperature of plane 1: 500 K
    Initial temperature of plane 2: 300 K
    */

    run_test(7)?;

    Ok(())
}

#[test]
pub fn test_radiation_3() -> Result<()> {
    /*
    Only Radiation between elements
    Two planes of 1000 m x 1000 m x 0.001 m, separated by 0.1 m
    Both planes have density: 2700 kg/m3, specific heat: 897 J/(K kg), thermal conductivity: 0 W/(K m)
    Plane 1 has alphaIR = 0.7
    Plane 2 has alphaIR = 0.2
    Initial temperature of plane 1: 500 K
    Initial temperature of plane 2: 300 K
    */

    run_test(8)?;

    Ok(())
}

#[test]
pub fn test_radiation_4() -> Result<()> {
    /*
    Only Radiation from elements to space
     - Solar constant set to zero
     - Albedo factor set to zero
     - Earth IR set to zero
    One cube of 1m
     - Density: 2700 kg/m3
     - Specific heat: 897 J/(K kg),
     - Thermal conductivity: 237 W/(K m)
     - Initial temperature: 473.15 K
    */

    run_test(9)?;

    Ok(())
}
