directory ?= models
method ?= Implicit

build:
	cargo build --release
	./target/release/solver "$(directory)" $(method)
