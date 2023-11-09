extern crate ocl;

use ocl::{flags, Buffer, Kernel};

use crate::fem::structures::Matrix;

use super::opencl::OpenCL;
use anyhow::Result;

fn parse_kernel(path: &str) -> std::io::Result<String> {
    Ok(std::fs::read_to_string(path)?)
}

pub fn matrix_inversion(matrix: Matrix) -> Result<Matrix> {
    let size = matrix.len();
    let n = matrix.shape().0;
    let mut identity = Matrix::identity(n, n);
    let opencl = OpenCL::new("./src/gpu/matrix_inversion.cl")?;

    let matrix_buffer = Buffer::<f64>::builder()
        .queue(opencl.queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size)
        .copy_host_slice(matrix.as_slice())
        .build()?;

    let identity_buffer = Buffer::<f64>::builder()
        .queue(opencl.queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(size)
        .copy_host_slice(identity.as_slice())
        .build()?;

    let k_buffer = Buffer::<i16>::builder()
        .queue(opencl.queue.clone())
        .flags(flags::MEM_READ_WRITE)
        .len(n)
        .fill_val(0)
        .build()?;

    let pivot_search = Kernel::builder()
        .program(&opencl.program)
        .name("pivot_search_k")
        .queue(opencl.queue.clone())
        .global_work_size(n)
        .arg(&matrix_buffer)
        .arg(&k_buffer)
        .arg(n as u16) //width
        .build()?;

    let pivot = Kernel::builder()
        .program(&opencl.program)
        .name("pivot")
        .queue(opencl.queue.clone())
        .global_work_size(2 * n)
        .arg(&matrix_buffer)
        .arg(&identity_buffer)
        .arg(&k_buffer)
        .arg(n as u16) //width
        .arg(0 as u16) //row
        .build()?;

    let scale_row = Kernel::builder()
        .program(&opencl.program)
        .name("scale_row")
        .queue(opencl.queue.clone())
        .global_work_size(2 * n)
        .arg(&matrix_buffer)
        .arg(&identity_buffer)
        .arg(n as u16) //width
        .arg(0 as u16) //row
        .build()?;

    let reduce_column = Kernel::builder()
        .program(&opencl.program)
        .name("reduce_column")
        .queue(opencl.queue.clone())
        .global_work_size((n, n + 1))
        .arg(&matrix_buffer)
        .arg(&identity_buffer)
        .arg(n as u16) //width
        .arg(0 as u16) //column
        .build()?;

    unsafe {
        pivot_search.enq()?;
        for y in 0..n {
            pivot.set_arg(3, y as u16)?;
            pivot.enq()?;
        }

        for y in 0..n {
            scale_row.set_arg(3, y as u16)?;
            scale_row.enq()?;
            reduce_column.set_arg(3, y as u16)?;
            reduce_column.enq()?;
        }
    }

    opencl.queue.finish()?;

    identity_buffer
        .cmd()
        .queue(&opencl.queue)
        .offset(0)
        .read(identity.as_mut_slice())
        .enq()?;

    Ok(identity)
}
