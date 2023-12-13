use anyhow::Result;
use std::sync::mpsc;
use std::thread;

enum Message {
    Result(String),
    Close,
}

pub struct ResultsWriterWorker {
    tx: mpsc::Sender<Message>,
    worker: Option<thread::JoinHandle<()>>,
}

impl ResultsWriterWorker {
    pub fn new() -> Self {
        let (sender, receiver) = mpsc::channel::<Message>();
        ResultsWriterWorker {
            tx: sender,
            worker: Some(thread::spawn(move || Self::work(receiver))),
        }
    }

    fn work(rx: mpsc::Receiver<Message>) {
        println!("Results writer worker started");
        loop {
            match rx.recv() {
                Ok(m) => match m {
                    Message::Result(v) => println!("From worker: {v}"),
                    Message::Close => break,
                },
                Err(_) => break, //Sender disconnected
            }
        }
        println!("Results writer worker shut down");
    }

    pub fn send(&mut self, text: String) -> Result<()> {
        self.tx.send(Message::Result(text))?;
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
