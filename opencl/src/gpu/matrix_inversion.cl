#define AGT(y, x, size) (y * size + x)

__kernel void pivot_search_k(__global double *m, __global short *k_array,
                             const unsigned short size) {

  const int x = get_global_id(0);
  short k = -2;

  if (m[AGT(x, x, size)] != 0.0) {
    k = -1;
    k_array[x] = k;
    return;
  }

  for (int h = 0; h < size; ++h) {
    if (m[AGT(h, x, size)] != 0.0) {
      k = h;
      break;
    }
  }

  if (k == -2) {
    printf("ERROR: Singular matrix found");
  }

  k_array[x] = k;
}

__kernel void pivot(__global double *m, __global double *n,
                    __global short *k_array, const unsigned short size,
                    const unsigned short y) {

  const short k = k_array[y];
  if (k < 0) {
    return;
  }

  int x = get_global_id(0);

  __global double *matrix = 0;

  if (x < size) {
    matrix = m;
  } else {
    x -= size;
    matrix = n;
  }

  matrix[AGT(y, x, size)] += matrix[AGT(k, x, size)];
}

__kernel void scale_row(__global double *m, __global double *n,
                        const unsigned short size, const unsigned short y) {

  int x = get_global_id(0);

  __global double *matrix = 0;

  if (x < size) {
    matrix = m;
  } else {
    x -= size;
    matrix = n;
  }

  matrix[AGT(y, x, size)] /= m[AGT(y, y, size)];
}

__kernel void reduce_column(__global double *m, __global double *n,
                            const unsigned short size, const unsigned short x) {

  const int y = get_global_id(0);
  int i = get_global_id(1) + x;

  if (x == y) {
    return;
  }

  __global double *matrix = 0;

  if (i < size) {
    matrix = m;
  } else {
    matrix = n;
    i -= size;
  }

  double Rj = matrix[AGT(x, i, size)];
  double Ri = m[AGT(y, x, size)];
  matrix[AGT(y, i, size)] -= Rj * Ri;
}
