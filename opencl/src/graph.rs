use std::error::Error;

use csv;
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct Node {
    idx: i16,
    x: f32,
    y: f32,
    z: f32,
    neigh_1: i16,
    neigh_2: i16,
    neigh_3: i16,
}

#[derive(Debug, Deserialize)]
pub struct Graph {
    nodes: Vec<Node>,
}

impl Graph {
    /// Reads data from a file into a reader and deserializes each record
    /// into a `Node` struct.
    /// Returns a Result with a `Graph` struct or an error.
    pub fn new_from_file(path: &str) -> Result<Graph, Box<dyn Error>> {
        let mut graph = Graph {
            nodes: Vec::new(),
        };

        let mut reader = csv::ReaderBuilder::new()
            .has_headers(false)
            .from_path(path)?;

        for result in reader.deserialize() {
            let node: Node = result?;

            graph.add_node(node)
        }

        Ok(graph)
    }

    pub fn add_node(&mut self, node: Node) {
        self.nodes.push(node);
    }

    pub fn get_nodes(&self) -> &Vec<Node> {
        &self.nodes
    }
}