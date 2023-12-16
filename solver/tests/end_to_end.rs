use anyhow::{Context, Result};
use serde::Deserialize;
use solver::fem::executor::run_solver;
use std::{fs::remove_dir_all, fs::File, io::BufReader};
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

fn compare_vtk(file_path1: &str, file_path2: &str) -> Result<()> {
    let vtk_file1 =
        Vtk::import(&file_path1).with_context(|| format!("Couldn't load file: {file_path1}"))?;

    let vtk_file2 =
        Vtk::import(&file_path2).with_context(|| format!("Couldn't load file: {file_path2}"))?;

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

fn parse_json(path: &str) -> Result<VTKSeries> {
    let file_reader =
        BufReader::new(File::open(&path).with_context(|| format!("Couldn't read file {path}"))?);
    let json_file: VTKSeries = serde_json::from_reader(file_reader)
        .with_context(|| format!("Couldn't parse file {path}"))?;

    Ok(json_file)
}

fn compare_results(results_path: &str, actual_results_path: &str) -> Result<()> {
    let result_file_path = format!("{}/result.vtk.series", results_path);
    let actual_result_file_path = format!("{}/result.vtk.series", actual_results_path);

    let result_file_json =
        parse_json(&result_file_path).with_context(|| "Couldn't parse results json file")?;
    let actual_result_file_json = parse_json(&actual_result_file_path)
        .with_context(|| "Couldn't parse actual results json file")?;

    assert!(
        actual_result_file_json.files.len() == result_file_json.files.len(),
        "Length of results files not equal"
    );

    for i in 0..actual_result_file_json.files.len() {
        assert_float_eq(
            actual_result_file_json.files[i].time,
            result_file_json.files[i].time,
            0.01,
        );
        compare_vtk(
            &format!(
                "{}/{}",
                actual_results_path, actual_result_file_json.files[i].name
            ),
            &format!("{}/{}", results_path, result_file_json.files[i].name),
        )?;
    }

    Ok(())
}

fn run_test_on_solver(directory_path: &str, solver: &str) -> Result<()> {
    let results_path = format!("{directory_path}/results");
    let actual_results_path = format!("{directory_path}/actual_results");

    run_solver(directory_path, solver)?;

    compare_results(&results_path, &actual_results_path)?;
    remove_dir_all(results_path)?;

    Ok(())
}

fn run_test(test_path: &str) -> Result<()> {
    run_test_on_solver(test_path, "Implicit")?;
    //run_test_solver(test_number, "Explicit")?;
    run_test_on_solver(test_path, "GPU")?;
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

    run_test("e2e_tests/conduction_1")?;

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

    run_test("e2e_tests/conduction_2")?;

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

    run_test("e2e_tests/conduction_3")?;

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

    run_test("e2e_tests/conduction_4")?;

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

    run_test("e2e_tests/conduction_5")?;

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

    run_test("e2e_tests/radiation_1")?;

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

    run_test("e2e_tests/radiation_2")?;

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

    run_test("e2e_tests/radiation_3")?;

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

    run_test("e2e_tests/radiation_4")?;

    Ok(())
}

#[test]
pub fn test_radiation_5() -> Result<()> {
    /*
    One plate of 1m
     - Density: 2700 kg/m3
     - Specific heat: 897 J/(K kg),
     - Thermal conductivity: 237 W/(K m)
     - Initial temperature: 473.15 K
     - Two side radiation: True
    Only radiation from elements to space (both sides)
     - Solar constant set to zero
     - Albedo factor set to zero
     - Earth IR set to zero
    */

    run_test("e2e_tests/radiation_5")?;

    Ok(())
}

#[test]
pub fn test_sun_1() -> Result<()> {
    /*
    One Cube of 1 m x 1 m x 1 m, thickness 5 cm.
    Density 2700 kg/m3,
    Specific Heat 900 J/(K kg) y
    Thermal Conductivity 0 W/(K m)
    Alpha sun = 1
    Alpha_ir = 1
    Initial Temperature 273.15 K
    Sun Pointing
    Albedo = 0
    Earth_ir = 0
    Solar constant = 1361 W/m2
    SMA: 7000 km
    ECC: 0
    INC: 0
    RAAN: 0
    AOP: 0
    TA: 0
    */

    run_test("e2e_tests/sun_1")?;

    Ok(())
}

#[test]
pub fn test_ir_1() -> Result<()> {
    /*
    One Cube of 1 m x 1 m x 1 m, thickness 5 cm.
    Density 2700 kg/m3,
    Specific Heat 900 J/(K kg) y
    Thermal Conductivity 0 W/(K m)
    Alpha sun = 1
    Alpha_ir = 1
    Initial Temperature 273.15 K
    Sun Pointing
    Albedo = 0
    Earth_ir = 225 W/m2
    Solar constant = 0
    SMA: 7000 km
    ECC: 0
    INC: 0
    RAAN: 0
    AOP: 0
    TA: 0
    */

    run_test("e2e_tests/ir_1")?;

    Ok(())
}

#[test]
pub fn test_albedo_1() -> Result<()> {
    /*
    One Cube of 1 m x 1 m x 1 m, thickness 5 cm.
    Density 2700 kg/m3,
    Specific Heat 900 J/(K kg) y
    Thermal Conductivity 0 W/(K m)
    Alpha sun = 1
    Alpha_ir = 1
    Initial Temperature 273.15 K
    Sun Pointing
    Albedo = 1
    Earth_ir = 0
    Solar constant = 1361W/m2
    SMA: 7000 km
    ECC: 0
    INC: 0
    RAAN: 0
    AOP: 0
    TA: 0
    */

    run_test("e2e_tests/albedo_1")?;

    Ok(())
}

#[test]
pub fn test_all_sources_1() -> Result<()> {
    /*
    One Cube of 1 m x 1 m x 1 m, thickness 5 cm.
    Density 2700 kg/m3,
    Specific Heat 900 J/(K kg) y
    Thermal Conductivity 0 W/(K m)
    Alpha sun = 1
    Alpha_ir = 1
    Initial Temperature 273.15 K
    Sun Pointing
    Albedo = 0.2
    Earth_ir = 225 W/m2
    Solar constant = 1361 W/m2
    SMA: 7000 km
    ECC: 0
    INC: 0
    RAAN: 0
    AOP: 0
    TA: 0
    */

    run_test("e2e_tests/all_sources_1")?;

    Ok(())
}

#[test]
pub fn test_all_sources_2() -> Result<()> {
    /*
    One Cube of 1 m x 1 m x 1 m, thickness 5 cm.
    Density 2700 kg/m3,
    Specific Heat 900 J/(K kg) y
    Thermal Conductivity 237 W/(K m)
    Alpha sun = 1
    Alpha_ir = 1
    Initial Temperature 273.15 K
    Sun Pointing
    Albedo = 0.2
    Earth_ir = 225 W/m2
    Solar constant = 1361 W/m2
    SMA: 7000 km
    ECC: 0
    INC: 0
    RAAN: 0
    AOP: 0
    TA: 0
    */

    run_test("e2e_tests/all_sources_2")?;

    Ok(())
}

#[test]
pub fn test_pyramid() -> Result<()> {
    /*
    One Pyramid of 1 m x 1 m base, x 1 m heigth, thickness 5 cm.
    Density 2700 kg/m3,
    Specific Heat 900 J/(K kg) y
    Thermal Conductivity 237 W/(K m)
    Alpha sun = 1
    Alpha_ir = 1
    Initial Temperature 273.15 K
    Sun Pointing (point of the pyramid)
    Albedo = 0.2
    Earth_ir = 225 W/m2
    Solar constant = 1361 W/m2
    SMA: 7000 km
    ECC: 0
    INC: 0
    RAAN: 0
    AOP: 0
    TA: 0
    */

    run_test("e2e_tests/pyramid")?;

    Ok(())
}

#[test]
pub fn test_nut() -> Result<()> {
    /*
    One Nut of 4 m external radious, 2 m internal radious, 4 m heigth, thickness 5 cm.
    Density 2700 kg/m3,
    Specific Heat 900 J/(K kg) y
    Thermal Conductivity 237 W/(K m)
    Alpha sun = 1
    Alpha_ir = 1
    Initial Temperature 293.15 K
    Sun Pointing (45º pointing to the middle of the nut)
    Albedo = 0.2
    Earth_ir = 225 W/m2
    Solar constant = 1361 W/m2
    SMA: 7000 km
    ECC: 0
    INC: 0
    RAAN: 0
    AOP: 0
    TA: 0
    */

    run_test("e2e_tests/nut")?;

    Ok(())
}
