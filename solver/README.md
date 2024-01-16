# Solver



## Installation

Install Rust.  The recommended way is [Rustup]( https://www.rust-lang.org/tools/install).

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Build with cargo

```bash
cargo build --release
mv target/release/solver solver
```



## Usage

**Run with CPU**

```bash
./solver <directory-path> Implicit
```

**Run with GPU**

```bash
./solver <directory-path> GPU
```



## Test

Execute tests:

```bash
cargo test
```

