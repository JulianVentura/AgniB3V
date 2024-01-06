# Solver



## Installation

Install Rust through rustup as recommended in https://www.rust-lang.org/tools/install

```
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Move to solver folder

```
cd solver
```

Build with cargo

```
cargo build --release
mv target/release/solver solver
```



## Usage

**Run with CPU**

```
./solver files/directory Implicit
```

**Run with GPU**

```
./solver files/directory GPU
```



## Test

Execute tests:

```
cargo test
```

