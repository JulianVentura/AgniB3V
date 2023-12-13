extern crate ocl;

use ocl::{Context, Device, Platform, Program, Queue};

use anyhow::{Context as Ctx, Result};

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
        let device = Device::first(platform).with_context(|| "Couldn't open opencl device")?;
        let context = Context::builder()
            .platform(platform)
            .devices(device.clone())
            .build()
            .with_context(|| "Couldn't create opencl context")?;
        let program = Program::builder()
            .devices(device)
            .src(src)
            .build(&context)
            .with_context(|| "Couldn't create opencl program")?;

        let queue =
            Queue::new(&context, device, None).with_context(|| "Couldn't create opencl queue")?;

        Ok(OpenCL {
            platform,
            device,
            context,
            program,
            queue,
        })
    }
}
