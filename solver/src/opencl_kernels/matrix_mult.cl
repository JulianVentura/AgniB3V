// t^4
// The `fourth_elevation` kernel function is performing the fourth power elevation of each element in the input array `t` 
// and storing the result in the output array `t_4`.
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
// Based on BLAS Standard Library function "sgemv" (http://www.bealto.com/gpu-gemv.html)    
// The `gemv1` kernel function is performing a matrix-vector multiplication. It takes in three input arrays `a`, `x`, and two integers `m` and `n`.
// The `a` array represents a matrix of size `m x n`, the `x` array represents a vector of size `n`, and the `y` array represents the output vector of size `m`.
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
// The `vec_sum` kernel function is performing element-wise addition of two input arrays `a` and `b`, and storing the result in the output array `c`.
// The size of the arrays is specified by the integer `n`. Each element of `c` is calculated by adding the corresponding elements from `a` and `b`.
__kernel void vec_sum(__global double *a, __global double *b,
                      __global double *c, int n) {
  int i = get_global_id(0);
  if (i < n) {
    c[i] = a[i] + b[i];
  }
}