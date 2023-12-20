import numpy as np
from typing import Tuple
import struct

FACTOR = (1 << 16) - 1


def process_entry(x):
    return x * FACTOR


def serialize_view_factors(
    filename: str,
    earth_ir_view_factors: list[Tuple[np.ndarray, float]],
    earth_albedo_view_factors: list[Tuple[np.ndarray, float]],
    sun_view_factors: list[Tuple[np.ndarray, float]],
    element_view_factors: np.matrix,
):
    file = open(filename, "wb")
    serialize_multiple_vectors(file, earth_ir_view_factors)
    serialize_multiple_vectors(file, earth_albedo_view_factors)
    serialize_multiple_vectors(file, sun_view_factors)
    serialize_matrix(file, element_view_factors)
    file.close()


def serialize_multiple_vectors(file, values):
    values_len = len(values)
    file.write(struct.pack(">H", values_len))
    for m in values:
        serialize_vector(file, m)


def serialize_matrix(file, m: np.ndarray):
    rows, columns = m.shape
    m = process_entry(m).astype("u2")
    m = np.ascontiguousarray(m, dtype=">u2")
    file.write(struct.pack(">HH", rows, columns))
    file.write(m.tobytes(order="C"))


def serialize_vector(file, data: Tuple[np.ndarray, float]):
    (v, start_time) = data
    size = len(v)
    m = process_entry(v).astype("u2")
    m = np.ascontiguousarray(m, dtype=">u2")
    file.write(struct.pack(">Hf", size, start_time))
    file.write(m.tobytes(order="C"))
