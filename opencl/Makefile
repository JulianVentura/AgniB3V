config_path ?= models/config.json

build:
	cargo build --release
	./target/release/opencl $(config_path)
