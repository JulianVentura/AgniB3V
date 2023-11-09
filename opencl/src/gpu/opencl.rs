#![allow(unused_imports)] //TODO: Remove
#![allow(dead_code)]
extern crate ocl;

use ocl::{flags, Buffer, Context, Device, Kernel, Platform, Program, Queue};

use anyhow::Result;

pub struct OpenCL {
    pub platform: ocl::Platform,
    pub device: ocl::Device,
    pub context: ocl::Context,
    pub program: ocl::Program,
    pub queue: ocl::Queue,
}

impl OpenCL {
    pub fn new(src: &str) -> Result<OpenCL> {
        let platform = Platform::default();
        let device = Device::first(platform)?;
        let context = Context::builder()
            .platform(platform)
            .devices(device.clone())
            .build()?;
        let program = Program::builder()
            .devices(device)
            .src(src)
            .build(&context)?;
        let queue = Queue::new(&context, device, None)?;

        Ok(OpenCL {
            platform,
            device,
            context,
            program,
            queue,
        })
    }
}
