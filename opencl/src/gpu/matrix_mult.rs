extern crate ocl;
use std::io::{self, Write};

use ocl::{flags, Buffer, Context, Device, Kernel, Platform, Program, Queue};

use crate::fem::structures::{Matrix, Vector};

pub struct Kernels {
    pub kernel_t_4: Kernel,
    pub kernel_f: Kernel,
    pub kernel_f_sum: Kernel,
    pub kernel_d_temp: Kernel,
    pub kernel_b_f: Kernel,
}
pub struct Buffers {
    pub buffer_t: Buffer<f64>,
    pub buffer_t_4: Buffer<f64>,
    pub buffer_f: Buffer<f64>,
    pub buffer_h: Buffer<f64>,
    pub buffer_f_const: Buffer<f64>,
    pub buffer_d: Buffer<f64>,
    pub buffer_b: Buffer<f64>,
}
pub struct MatrixMult {
    pub queue: Queue,
    pub kernels: Kernels,
    pub buffers: Buffers,
}

fn parse_kernel(path: &str) -> std::io::Result<String> {
    Ok(std::fs::read_to_string(path)?)
}

pub fn compile_kernel(
    t: &Vector,
    h: &Matrix,
    f_const: &Vector,
    d: &Matrix,
) -> ocl::Result<(MatrixMult)> {
    let src = match parse_kernel("./src/gpu/matrix_mult.cl") {
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

    let size_t = t.len() as i32;
    // (2) Create a `Buffer`:
    let buffer_t = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_t)
        .copy_host_slice(t.as_slice())
        .build()?;

    let buffer_t_4 = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_t)
        .copy_host_slice(vec![0.0; size_t as usize].as_slice())
        .build()?;

    let buffer_f = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_t)
        .copy_host_slice(vec![0.0; size_t as usize].as_slice())
        .build()?;

    let size_h = h.len() as i32;
    let buffer_h = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_h)
        .copy_host_slice(h.as_slice())
        .build()?;

    let buffer_f_const = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_t)
        .copy_host_slice(f_const.as_slice())
        .build()?;

    let size_d = d.len() as i32;
    let buffer_d = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_d)
        .copy_host_slice(d.as_slice())
        .build()?;

    let buffer_b = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_t)
        .copy_host_slice(vec![0.0; size_t as usize].as_slice())
        .build()?;

    let buffer_work = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_t)
        .copy_host_slice(vec![0.0; size_t as usize].as_slice())
        .build()?;
    let buffer_work2 = Buffer::<f64>::builder()
        .queue(queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size_t)
        .copy_host_slice(vec![0.0; size_t as usize].as_slice())
        .build()?;
    // (3) Create a kernel with arguments matching those in the source above:
    let mut kernel_t_4 = Kernel::builder()
        .program(&program)
        .name("fourth_elevation")
        .queue(queue.clone())
        .global_work_size(size_t)
        .arg(&buffer_t)
        .arg(&buffer_t_4)
        .arg(&size_t)
        .build()?;
    let threads = 4;
    let mut kernel_f = Kernel::builder()
        .program(&program)
        .name("gemv2")
        .queue(queue.clone())
        .global_work_size([size_t, threads])
        .arg(&buffer_h)
        .arg(&buffer_t_4)
        .arg(&buffer_f)
        .arg(&buffer_work)
        .arg(&size_t)
        .arg(&size_t)
        .build()?;

    let mut kernel_f_sum = Kernel::builder()
        .program(&program)
        .name("vec_sum")
        .queue(queue.clone())
        .global_work_size(size_t)
        .arg(&buffer_f)
        .arg(&buffer_f_const)
        .arg(&buffer_f)
        .arg(&size_t)
        .build()?;

    let mut kernel_d_temp = Kernel::builder()
        .program(&program)
        .name("gemv2")
        .queue(queue.clone())
        .global_work_size([size_t, threads])
        .arg(&buffer_d)
        .arg(&buffer_t)
        .arg(&buffer_b)
        .arg(&buffer_work2)
        .arg(&size_t)
        .arg(&size_t)
        .build()?;

    let mut kernel_b_f = Kernel::builder()
        .program(&program)
        .name("vec_sum")
        .queue(queue.clone())
        .global_work_size(size_t)
        .arg(&buffer_b)
        .arg(&buffer_f)
        .arg(&buffer_b)
        .arg(&size_t)
        .build()?;

    let kernels = Kernels {
        kernel_t_4,
        kernel_f,
        kernel_f_sum,
        kernel_d_temp,
        kernel_b_f,
    };

    let buffers = Buffers {
        buffer_t,
        buffer_t_4,
        buffer_f,
        buffer_h,
        buffer_f_const,
        buffer_d,
        buffer_b,
    };

    let matrix_mult = MatrixMult {
        queue,
        kernels,
        buffers,
    };

    Ok(matrix_mult)
}

pub fn matrix_mult(t: &Vector, f_const: &Vector, matrix_mult: &MatrixMult) -> ocl::Result<Vector> {
    let size_t = t.len() as i32;
    matrix_mult
        .buffers
        .buffer_t
        .cmd()
        .write(t.as_slice())
        .enq()?;
    matrix_mult
        .buffers
        .buffer_f_const
        .cmd()
        .write(f_const.as_slice())
        .enq()?;
    // (4) Run the kernel (default parameters shown for demonstration purposes):
    unsafe {
        matrix_mult.kernels.kernel_t_4.enq()?;
        matrix_mult.kernels.kernel_f.enq()?;
        matrix_mult.kernels.kernel_f_sum.enq()?;
        matrix_mult.kernels.kernel_d_temp.enq()?;
        matrix_mult.kernels.kernel_b_f.enq()?;
    }

    matrix_mult.queue.finish()?;
    let mut values = vec![0.0; size_t as usize];

    matrix_mult
        .buffers
        .buffer_b
        .cmd()
        .queue(&matrix_mult.queue)
        .offset(0)
        .read(&mut values)
        .enq()?;

    Ok(Vector::from_vec(values))
}
