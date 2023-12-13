extern crate anyhow;

#[macro_export]
macro_rules! err {
    ($fmt:expr $(, $arg:expr)*) => {
        return Err(anyhow::anyhow!($fmt, $($arg)*))
    };
}

pub use err;
