extern crate ocl;
use std::io::{self, Write};

use ocl::{flags, Buffer, Context, Device, Kernel, Platform, Program, Queue};

use crate::fem::structures::{Matrix, Vector};

fn parse_kernel(path: &str) -> std::io::Result<String> {
    Ok(std::fs::read_to_string(path)?)
}

pub fn jacobi_method(a: Matrix, b: Vector) -> ocl::Result<Vector> {
    let src = match parse_kernel("./src/gpu/jacobi_method.cl") {
        Ok(x) => x,
        Err(e) => {
            println!("Error: {}", e);
            panic!("Error: {}", e);
        }
    };

    // (1) Define which platform and device(s) to use. Create a context,
    // queue, and program then define some dims (compare to step 1 above).
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

    let size = b.len() as i32;
    // (2) Create a `Buffer`:
    let buffer_b = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size)
        .copy_host_slice(b.as_slice())
        .build()?;

    let mut buffer_x = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size)
        .copy_host_slice(vec![0.0; size as usize].as_slice())
        .build()?;

    let buffer_x_res = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size)
        .copy_host_slice(vec![0.0; size as usize].as_slice())
        .build()?;

    let size_a = a.len() as i32;
    let buffer_a = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_a)
        .copy_host_slice(a.as_slice())
        .build()?;

    // (3) Create a kernel with arguments matching those in the source above:
    let mut kernel = Kernel::builder()
        .program(&program)
        .name("jacobi_method")
        .queue(queue.clone())
        .global_work_size(size)
        .arg(&buffer_b)
        .arg(&buffer_x)
        .arg(&buffer_x_res)
        .arg(&buffer_a)
        .arg(&size)
        .build()?;

    // (4) Run the kernel (default parameters shown for demonstration purposes):
    for _ in 0..2 {
        unsafe {
            kernel.enq()?;
        }
        queue.finish()?;
        let mut values = vec![0.0; size as usize];
        buffer_x_res
            .cmd()
            .queue(&queue)
            .offset(0)
            .read(&mut values)
            .enq()?;

        buffer_x = Buffer::<f64>::builder()
            .queue(queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size)
            .copy_host_slice(values.as_slice())
            .build()?;

        kernel = Kernel::builder()
            .program(&program)
            .name("jacobi_method")
            .queue(queue.clone())
            .global_work_size(size)
            .arg(&buffer_b)
            .arg(&buffer_x)
            .arg(&buffer_x_res)
            .arg(&buffer_a)
            .arg(&size)
            .build()?;
    }

    let mut values = vec![0.0; size as usize];

    buffer_x_res
        .cmd()
        .queue(&queue)
        .offset(0)
        .read(&mut values)
        .enq()?;

    Ok(Vector::from_vec(values))
}
