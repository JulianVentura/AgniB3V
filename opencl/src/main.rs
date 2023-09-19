pub mod graph;

fn main() {
    if let Ok(ex_graph) = graph::Graph::new_from_file("./Cube.csv") {
        println!("{:?}", ex_graph);
    } else {
        println!("Error");
    }
}
