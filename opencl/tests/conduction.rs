use anyhow::Result;
use opencl::fem::executor::run_solver;
use serde::Deserialize;
use std::{fs::remove_dir_all, fs::File, io::BufReader, io::Read};

#[derive(Deserialize)]
pub struct VTK {
    name: String,
    time: f64,
}

#[derive(Deserialize)]
pub struct VTKSeries {
    files: Vec<VTK>,
}

fn compare_files(file_path1: String, file_path2: String) -> Result<()> {
    // Read the contents of the first file
    let file1 = File::open(file_path1)?;
    let mut buf_reader1 = BufReader::new(file1);
    let mut contents1 = String::new();
    buf_reader1.read_to_string(&mut contents1)?;

    // Read the contents of the second file
    let file2 = File::open(file_path2)?;
    let mut buf_reader2 = BufReader::new(file2);
    let mut contents2 = String::new();
    buf_reader2.read_to_string(&mut contents2)?;

    // Compare the contents of the two files
    assert!(contents1 == contents2, "Files are not identical");

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
        compare_files(
            format!("{}/{}", actual_results, actual_file_json.files[i].name),
            format!("{}/{}", new_results, new_file_json.files[i].name),
        )?;
    }

    Ok(())
}

#[test]
pub fn test_1() -> Result<()> {
    /*
    Cube of 1 m x 1 m x 1 m
    Material: Aluminuim, density: 2700 kg/m3, specific heat: 900 J/(K kg), thermal conductivity: 237 W/(K m)
    One of the faces has an initial temperature of 573 K (300 C), the rest 273 K (0 C)
    There are no fluxes
    */

    let vtk_path = "Unit_tests/Test_1/test_1.vtk".to_string();
    let json_path = "Unit_tests/Test_1/test_1_out.json".to_string();
    let actual_results_path = "Unit_tests/Test_1/test_1_results".to_string();
    let results_path = "Unit_tests/Test_1".to_string();
    let new_results_name = "test_1_new".to_string();
    let actual_results_name = "test_1_results".to_string();

    run_solver(&vtk_path, &json_path, &results_path, &new_results_name)?;

    compare_results(
        actual_results_path,
        format!("{}/{}_results", results_path, new_results_name),
        actual_results_name,
        format!("{}_results", new_results_name),
    )?;

    remove_dir_all(format!("{}/{}_results", results_path, new_results_name))?;

    Ok(())
}
