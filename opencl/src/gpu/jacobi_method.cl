int get_matrix_index(int i, int j, int n) { return i * n + j; }

__kernel void jacobi_method(__global double *b, __global double *x,
                            __global double *x_res, __global double *A,
                            const int vectors_len) {
  const int idx = get_global_id(0);
  if (idx < vectors_len) {
    int bi = b[idx];
    int aii = A[get_matrix_index(idx, idx, vectors_len)];
    int sum = 0;
    for (int j = 0; j < vectors_len; j++) {
      if (j != idx) {
        sum += A[get_matrix_index(idx, j, vectors_len)] * x[j];
      }
    }
    x_res[idx] = (bi - sum) / aii;
  }
}
