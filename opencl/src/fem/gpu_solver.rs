use super::element::Element;
use super::point::Point;
use super::solver;
use super::structures::{Matrix, Vector};
use anyhow::{Context as Ctx, Result};

use ocl::{flags, Buffer, Context, Device, Kernel, Platform, Program, Queue};

pub struct GPUSolver {
    pub f_const: Vec<Vector>,
    pub d: Matrix,
    pub h: Matrix,
    program: OpenCLProgram,
    buffers: OpenCLBuffers,
    kernels: OpenCLKernels,
    temp: Vector,
    points: Vec<Point>,
}

pub struct OpenCLProgram {
    pub context: ocl::Context,
    pub program: ocl::Program,
    pub queue: ocl::Queue,
}

pub struct OpenCLKernels {
    pub kernel_t_4: Kernel,
    pub kernel_f: Kernel,
    pub kernel_f_sum: Kernel,
    pub kernel_d_temp: Kernel,
    pub kernel_b_f: Kernel,
    pub kernel_solver: Kernel,
}
pub struct OpenCLBuffers {
    pub buffer_t: Buffer<f64>,
    pub buffer_t_4: Buffer<f64>,
    pub buffer_f: Buffer<f64>,
    pub buffer_h: Buffer<f64>,
    pub buffer_f_const: Buffer<f64>,
    pub buffer_d: Buffer<f64>,
    pub buffer_b: Buffer<f64>,
    pub buffer_a_inverse: Buffer<f64>,
}

impl GPUSolver {
    pub fn new(elements: &Vec<Element>, time_step: f64) -> Result<Self> {
        let n_points = solver::calculate_number_of_points(elements);
        println!("Constructing global M matrix");
        let m = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.m);
        println!("Constructing global K matrix");
        let k = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.k);
        println!("Constructing global E matrix");
        let e = solver::construct_global_matrix(elements, n_points, |e: &Element| &e.e);
        println!("Constructing global L matrix");
        let l = solver::construct_l_matrix(elements, n_points);
        println!("Constructing global flux vector");
        let f_const = solver::construct_global_vector_f_const_array(elements, n_points);
        println!("Constructing points array");
        let points = solver::construct_points_array(elements, n_points);
        let temp = Vector::from_vec(points.iter().map(|p| p.temperature).collect::<Vec<f64>>());

        let h = l - e;

        //Implicit matrices
        let theta = 0.5;
        println!("Constructing D matrix");
        let d = &m / time_step - (1.0 - theta) * &k;
        println!("Constructing A matrix");
        let a = &m / time_step + theta * &k;
        println!("Inverting A matrix");

        let a_inverse = a
            .clone()
            .try_inverse()
            .with_context(|| "Couldn't inverse matrix A")?;

        //TODO: Modify this path to eliminate cwd dependency
        let mut program = Self::start_opencl_program("./src/gpu/matrix_mult.cl")
            .with_context(|| "Couldn't start opencl program")?;
        let buffers =
            Self::start_opencl_buffers(&mut program, &temp, &h, &f_const[0], &d, &a_inverse)
                .with_context(|| "Couldn't start opencl buffers")?;
        let kernels = Self::start_opencl_kernels(&mut program, &buffers, &temp)
            .with_context(|| "Couldn't start opencl kernels")?;

        Ok(GPUSolver {
            f_const,
            d,
            h,
            temp,
            points,
            program,
            buffers,
            kernels,
        })
    }

    //TODO: Optimization:
    //Here we are writing on buffers on every step iteration
    //we instead could be just writing when the f constant changes

    pub fn step(&mut self) -> Result<()> {
        unsafe {
            self.kernels.kernel_t_4.enq()?;
            self.kernels.kernel_f.enq()?;
            self.kernels.kernel_f_sum.enq()?;
            self.kernels.kernel_d_temp.enq()?;
            self.kernels.kernel_b_f.enq()?;
            self.kernels.kernel_solver.enq()?;
        }

        Ok(())
    }

    pub fn points(&self) -> &Vec<Point> {
        &self.points
    }

    pub fn update_f(&mut self, f_index: usize) -> Result<()> {
        self.buffers
            .buffer_f_const
            .cmd()
            .write(self.f_const[f_index].as_slice())
            .enq()?;

        Ok(())
    }

    pub fn temperature(&mut self) -> Result<&Vector> {
        self.program.queue.finish()?;

        self.buffers
            .buffer_t
            .cmd()
            .queue(&self.program.queue)
            .offset(0)
            .read(self.temp.as_mut_slice())
            .enq()?;

        Ok(&self.temp)
    }

    fn start_opencl_program(src_path: &str) -> Result<OpenCLProgram> {
        let kernel_code = std::fs::read_to_string(src_path)
            .with_context(|| format!("Couldn't read kernel code on {src_path}"))?;
        let platform = Platform::default();
        let device = Device::first(platform).with_context(|| "Opencl device not found")?;
        let context = Context::builder()
            .platform(platform)
            .devices(device.clone())
            .build()
            .with_context(|| "Couldn't connect to opencl device")?;
        let program = Program::builder()
            .devices(device)
            .src(kernel_code)
            .build(&context)
            .with_context(|| "Couldn't parse opencl kernel code")?;
        let queue =
            Queue::new(&context, device, None).with_context(|| "Couldn't create opencl queue")?;

        Ok(OpenCLProgram {
            context,
            program,
            queue,
        })
    }

    fn start_opencl_buffers(
        session: &mut OpenCLProgram,
        t: &Vector,
        h: &Matrix,
        f_const: &Vector,
        d: &Matrix,
        a_inverse: &Matrix,
    ) -> Result<OpenCLBuffers> {
        let size_t = t.len() as i32;
        let size_h = h.len() as i32;
        let size_d = d.len() as i32;
        let size_a_inverse = a_inverse.len() as i32;

        let buffer_t = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_t)
            .copy_host_slice(t.as_slice())
            .build()
            .with_context(|| "Couldn't create opencl buffer_t")?;

        let buffer_t_4 = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_t)
            .fill_val(0.0)
            .build()
            .with_context(|| "Couldn't create opencl buffer_t_4")?;

        let buffer_f = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_t)
            .fill_val(0.0)
            .build()
            .with_context(|| "Couldn't create opencl buffer_f")?;

        let buffer_h = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_h)
            .copy_host_slice(h.as_slice())
            .build()
            .with_context(|| "Couldn't create opencl buffer_h")?;

        let buffer_f_const = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_t)
            .copy_host_slice(f_const.as_slice())
            .build()
            .with_context(|| "Couldn't create opencl buffer_f_const")?;

        let buffer_d = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_d)
            .copy_host_slice(d.as_slice())
            .build()
            .with_context(|| "Couldn't create opencl buffer_d")?;

        let buffer_b = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_t)
            .fill_val(0.0)
            .build()
            .with_context(|| "Couldn't create opencl buffer_b")?;

        let buffer_a_inverse = Buffer::<f64>::builder()
            .queue(session.queue.clone())
            .flags(flags::MEM_READ_WRITE)
            .len(size_a_inverse)
            .copy_host_slice(a_inverse.as_slice())
            .build()
            .with_context(|| "Couldn't create opencl buffer_a_inverse")?;

        Ok(OpenCLBuffers {
            buffer_t,
            buffer_t_4,
            buffer_f,
            buffer_h,
            buffer_f_const,
            buffer_d,
            buffer_b,
            buffer_a_inverse,
        })
    }

    fn start_opencl_kernels(
        session: &mut OpenCLProgram,
        buffers: &OpenCLBuffers,
        t: &Vector,
    ) -> Result<OpenCLKernels> {
        let size_t = t.len() as i32;
        let threads = 4;

        let kernel_t_4 = Kernel::builder()
            .program(&session.program)
            .name("fourth_elevation")
            .queue(session.queue.clone())
            .global_work_size(size_t)
            .arg(&buffers.buffer_t)
            .arg(&buffers.buffer_t_4)
            .arg(&size_t)
            .build()
            .with_context(|| "Couldn't create opencl kernel_t_4")?;

        let kernel_f = Kernel::builder()
            .program(&session.program)
            .name("gemv1")
            .queue(session.queue.clone())
            .global_work_size(size_t)
            .arg(&buffers.buffer_h)
            .arg(&buffers.buffer_t_4)
            .arg(&buffers.buffer_f)
            .arg(&size_t)
            .arg(&size_t)
            .build()
            .with_context(|| "Couldn't create opencl kernel_f")?;

        let kernel_f_sum = Kernel::builder()
            .program(&session.program)
            .name("vec_sum")
            .queue(session.queue.clone())
            .global_work_size(size_t)
            .arg(&buffers.buffer_f)
            .arg(&buffers.buffer_f_const)
            .arg(&buffers.buffer_f)
            .arg(&size_t)
            .build()
            .with_context(|| "Couldn't create opencl kernel_f_sum")?;

        let kernel_d_temp = Kernel::builder()
            .program(&session.program)
            .name("gemv1")
            .queue(session.queue.clone())
            .global_work_size([size_t, threads])
            .arg(&buffers.buffer_d)
            .arg(&buffers.buffer_t)
            .arg(&buffers.buffer_b)
            .arg(&size_t)
            .arg(&size_t)
            .build()
            .with_context(|| "Couldn't create opencl kernel_d_temp")?;

        let kernel_b_f = Kernel::builder()
            .program(&session.program)
            .name("vec_sum")
            .queue(session.queue.clone())
            .global_work_size(size_t)
            .arg(&buffers.buffer_b)
            .arg(&buffers.buffer_f)
            .arg(&buffers.buffer_b)
            .arg(&size_t)
            .build()
            .with_context(|| "Couldn't create opencl kernel_b_f")?;

        let kernel_solver = Kernel::builder()
            .program(&session.program)
            .name("gemv1")
            .queue(session.queue.clone())
            .global_work_size(size_t)
            .arg(&buffers.buffer_a_inverse)
            .arg(&buffers.buffer_b)
            .arg(&buffers.buffer_t)
            .arg(&size_t)
            .arg(&size_t)
            .build()
            .with_context(|| "Couldn't create opencl kernel_solver")?;

        Ok(OpenCLKernels {
            kernel_t_4,
            kernel_f,
            kernel_f_sum,
            kernel_d_temp,
            kernel_b_f,
            kernel_solver,
        })
    }
}
