directory ?= models
method ?= Implicit

build:
	cargo build --release
	./target/release/opencl $(directory) $(method)
