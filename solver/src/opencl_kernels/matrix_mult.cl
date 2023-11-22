// t^4
__kernel void fourth_elevation(__global double *t, __global double *t_4,
                               int n) {
  int i = get_global_id(0);
  if (i < n) {
    double t_i = t[i];
    double t_i2 = t_i * t_i;
    t_4[i] = t_i2 * t_i2;
  }
}

// a * x = y
__kernel void gemv1(__global const double *a, __global const double *x,
                    __global double *y, int m, int n) {
  double sum = 0.0f;
  int i = get_global_id(0); // row index
  for (int k = 0; k < n; k++) {
    sum += a[i + m * k] * x[k];
  }
  y[i] = sum;
}

// a + b = c
__kernel void vec_sum(__global double *a, __global double *b,
                      __global double *c, int n) {
  int i = get_global_id(0);
  if (i < n) {
    c[i] = a[i] + b[i];
  }
}

#define ROW_DIM 0
#define COL_DIM 1
// P threads per row compute 1/P-th of each dot product.
// WORK has P columns and get_local_size(0) rows.
__kernel void gemv2(__global const double *a, __global const double *x,
                    __global double *y, __local double *work, int m, int n) {
  // Compute partial dot product
  double sum = (double)0;
  for (int k = get_global_id(COL_DIM); k < n; k += get_global_size(COL_DIM)) {
    sum += a[get_global_id(ROW_DIM) + m * k] * x[k];
  }

  // Each thread stores its partial sum in WORK
  int rows = get_local_size(ROW_DIM); // rows in group
  int cols = get_local_size(COL_DIM); // initial cols in group
  int ii = get_local_id(ROW_DIM);     // local row index in group, 0<=ii<rows
  int jj = get_local_id(COL_DIM);     // block index in column, 0<=jj<cols
  work[ii + rows * jj] = sum;
  barrier(CLK_LOCAL_MEM_FENCE); // sync group

  // Reduce sums in log2(cols) steps
  while (cols > 1) {
    cols >>= 1;
    if (jj < cols)
      work[ii + rows * jj] += work[ii + rows * (jj + cols)];
    barrier(CLK_LOCAL_MEM_FENCE); // sync group
  }

  // Write final result in Y
  if (jj == 0)
    y[get_global_id(ROW_DIM)] = work[ii];
}