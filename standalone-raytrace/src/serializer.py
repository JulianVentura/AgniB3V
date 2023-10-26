import numpy as np
import struct

FACTOR = 1 << 16


def process_entry(x):
    return x * FACTOR


def serialize_view_factors(
    path: str,
    earth_view_factors: np.matrix,
    sun_view_factors: np.matrix,
    element_view_factors: np.matrix,
):
    file = open(path, "wb")
    serialize_multiple(file, earth_view_factors, serialize_vector)
    serialize_multiple(file, sun_view_factors, serialize_vector)
    serialize_multiple(file, element_view_factors, serialize_matrix)
    file.close()


def serialize_multiple(file, values, serialize_fn):
    values_len = len(values)
    file.write(struct.pack(">H", values_len))
    for m in values:
        serialize_fn(file, m)


def serialize_matrix(file, m: np.ndarray):
    rows, columns = m.shape
    m = process_entry(m).astype("u2")
    m = np.ascontiguousarray(m, dtype=">u2")
    file.write(struct.pack(">HH", rows, columns))
    file.write(m.tobytes(order="C"))


def serialize_vector(file, v: np.ndarray):
    size = len(v)
    m = process_entry(v).astype("u2")
    m = np.ascontiguousarray(m, dtype=">u2")
    file.write(struct.pack(">H", size))
    file.write(m.tobytes(order="C"))
