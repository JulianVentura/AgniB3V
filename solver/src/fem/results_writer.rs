use anyhow::Result;
use log::error;
use std::sync::mpsc;
use std::thread;

use crate::fem::parser;

use super::element::Element;
use super::parser::ParserConfig;
use super::point::Point;
use super::structures::Vector;

enum Message {
    Result(Vector),
    Close,
}

pub struct ResultsWriterWorker {
    tx: mpsc::Sender<Message>,
    worker: Option<thread::JoinHandle<()>>,
}

impl ResultsWriterWorker {
    pub fn new(
        config: ParserConfig,
        points: Vec<Point>,
        elements: Vec<Element>,
        snapshot_period: f64,
    ) -> Self {
        let (sender, receiver) = mpsc::channel::<Message>();
        ResultsWriterWorker {
            tx: sender,
            worker: Some(thread::spawn(move || {
                Self::work(receiver, config, points, elements, snapshot_period)
            })),
        }
    }

    fn work(
        rx: mpsc::Receiver<Message>,
        config: ParserConfig,
        points: Vec<Point>,
        elements: Vec<Element>,
        snapshot_period: f64,
    ) {
        println!("Results writer worker started");

        let mut id = 0;
        loop {
            match rx.recv() {
                Ok(m) => match m {
                    Message::Result(result) => {
                        if let Err(e) = parser::write_partial_vtk_result(
                            &config, &points, &elements, result, id,
                        ) {
                            error!("Worker thread error writing result {e:?}");
                            panic!();
                        }
                        id += 1;
                    }
                    Message::Close => break,
                },
                Err(_) => break, //Sender disconnected
            }
        }

        if let Err(e) = parser::write_vtk_series(&config, id, snapshot_period) {
            error!("Worker thread error writing vtk series {e:?}");
            panic!();
        }

        println!("Results writer worker shut down");
    }

    pub fn write_result(&mut self, result: Vector) -> Result<()> {
        self.tx.send(Message::Result(result))?;
        Ok(())
    }

    pub fn finish(self) -> Result<()> {
        if let Some(worker) = self.worker {
            self.tx.send(Message::Close)?;
            let _ = worker.join();
        }
        Ok(())
    }
}
