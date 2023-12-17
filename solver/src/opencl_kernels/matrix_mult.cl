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
// Based on BLAS Standard Library function "sgemv" (http://www.bealto.com/gpu-gemv.html)    
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