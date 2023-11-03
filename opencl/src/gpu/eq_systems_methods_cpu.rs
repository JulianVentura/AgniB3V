use nalgebra::ComplexField;

use crate::fem::structures::{Matrix, Vector};

pub fn jacobi_method_cpu(a: Matrix, b: Vector) -> Vector {
    let size = b.len();
    let mut x = vec![0.0; size];

    let mut x_res = vec![0.0; size];

    for _ in 0..3 {
        for i in 0..size {
            let mut sum = 0.0;
            for j in 0..size {
                if i != j {
                    sum += a[(i, j)] * x[j];
                }
            }
            x_res[i] = (b[i] - sum) / a[(i, i)];
        }
        x = x_res.clone();
    }
    test_convergence(a, size);
    Vector::from_vec(x_res)
}

fn test_convergence(a: Matrix, size: usize) {
    let mut sum = 0.0;
    for i in 0..size {
        for j in 0..size {
            if i != j {
                sum += a[(i, j)].abs();
            }
        }
        if sum > a[(i, i)].abs() {
            println!("Not diagonally dominant, may not converge");
            return;
        }
        sum = 0.0;
    }
    println!("Diagonally dominant, should converge");
}

pub fn gauss_seidel_cpu(a: Matrix, b: Vector) -> Vector {
    let size = b.len();
    let mut x_res = vec![0.0; size];

    for _ in 0..10 {
        for i in 0..size {
            let mut sum = 0.0;
            for j in 0..size {
                if i != j {
                    sum += a[(i, j)] * x_res[j];
                }
            }
            x_res[i] = (b[i] - sum) / a[(i, i)];
        }
    }
    Vector::from_vec(x_res)
}

pub struct LUDecomposition {
    l: Matrix,
    u: Matrix,
}
pub fn lu_decomposition_old(a: Matrix) -> LUDecomposition {
    let n = a.nrows();
    if n == 1 {
        let l = Matrix::from_element(1, 1, 1.0);
        let u = Matrix::from_element(1, 1, a[(0, 0)]);

        return LUDecomposition { l, u };
    }
    let mut l = Matrix::zeros(n, n);
    let mut u = Matrix::zeros(n, n);

    let a11 = a[(0, 0)];
    let a12 = Vector::from_vec(a.row(0).into_iter().skip(1).cloned().collect::<Vec<f64>>());
    let a21 = Vector::from_vec(
        a.column(0)
            .into_iter()
            .skip(1)
            .cloned()
            .collect::<Vec<f64>>(),
    );
    let a22 = a.view((1, 1), (n - 1, n - 1)).to_owned();

    l[(0, 0)] = 1.0;
    u[(0, 0)] = a11;
    for i in 0..n - 1 {
        u[(0, i + 1)] = a12[i];
        l[(i + 1, 0)] = a21[i] / a11;
    }

    let s22 = a22 - &l.view((1, 0), (n - 1, 1)) * &u.view((0, 1), (1, n - 1));
    let lu = lu_decomposition(s22);
    for i in 0..n - 1 {
        for j in 0..n - 1 {
            u[(i + 1, j + 1)] = lu.u[(i, j)];
            l[(i + 1, j + 1)] = lu.l[(i, j)];
        }
    }

    LUDecomposition { l, u }
}

pub fn lu_decomposition(a: Matrix) -> LUDecomposition {
    let n = a.nrows();
    let mut l = Matrix::zeros(n, n);
    let mut u = Matrix::zeros(n, n);

    for i in 0..n {
        for k in i..n {
            let mut sum = 0.0;
            for j in 0..i {
                sum += l[(i, j)] * u[(j, k)];
            }
            u[(i, k)] = a[(i, k)] - sum;
        }

        for k in i..n {
            if i == k {
                l[(i, i)] = 1.0;
            } else {
                let mut sum = 0.0;
                for j in 0..i {
                    sum += l[(k, j)] * u[(j, i)];
                }
                l[(k, i)] = (a[(k, i)] - sum) / u[(i, i)];
            }
        }
    }

    LUDecomposition { l, u }
}

pub fn lu_solve(lu: &LUDecomposition, b: Vector) -> Vector {
    let n = b.len();
    let mut y = vec![0.0; n];
    let mut x = vec![0.0; n];

    y[0] = b[0];
    for i in 1..n {
        let mut sum = 0.0;
        for j in 0..i {
            sum += lu.l[(i, j)] * y[j];
        }
        y[i] = b[i] - sum;
    }

    x[n - 1] = y[n - 1] / lu.u[(n - 1, n - 1)];
    for i in (0..n - 1).rev() {
        let mut sum = 0.0;
        for j in i + 1..n {
            sum += lu.u[(i, j)] * x[j];
        }
        x[i] = (y[i] - sum) / lu.u[(i, i)];
    }
    Vector::from_vec(x)
}
pub mod test {
    use crate::fem::structures::Matrix;

    fn assert_matrix_eq_float(a: Matrix, b: Matrix, precision: f64) {
        assert_eq!(a.nrows(), b.nrows());
        assert_eq!(a.ncols(), b.ncols());
        for i in 0..a.nrows() {
            for j in 0..a.ncols() {
                assert!((a[(i, j)] - b[(i, j)]).abs() < precision);
            }
        }
    }

    fn assert_matrix_eq_float_2(a: Matrix, b: Vec<Vec<f64>>, precision: f64) {
        assert_eq!(a.nrows(), b.len());
        if b.len() == 0 {
            return;
        }
        assert_eq!(a.ncols(), b[0].len());
        for i in 0..a.nrows() {
            for j in 0..a.ncols() {
                assert!((a[(i, j)] - b[i][j]).abs() < precision);
            }
        }
    }

    #[test]
    pub fn test_lu_decomposition_1() {
        let a = Matrix::from_vec(2, 2, vec![1.0, 3.0, 2.0, 4.0]); //Filled by column
        let lu = super::lu_decomposition(a);
        let l = lu.l;
        let u = lu.u;
        assert_eq!(l, Matrix::from_vec(2, 2, vec![1.0, 3.0, 0.0, 1.0])); //Filled by column
        assert_eq!(u, Matrix::from_vec(2, 2, vec![1.0, 0.0, 2.0, -2.0])); //Filled by column
    }

    #[test]
    pub fn test_lu_decomposition_2() {
        let a = Matrix::from_vec(3, 3, vec![5.0, 2.0, 3.0, 6.0, 1.0, 0.0, 7.0, 8.0, 1.0]); //Filled by column
        let lu = super::lu_decomposition(a);
        let l = lu.l;
        let u = lu.u;
        assert_matrix_eq_float(
            l,
            Matrix::from_vec(3, 3, vec![1.0, 0.4, 0.6, 0.0, 1.0, 2.57, 0.0, 0.0, 1.0]),
            0.01,
        ); //Filled by column
        assert_matrix_eq_float(
            u,
            Matrix::from_vec(3, 3, vec![5.0, 0.0, 0.0, 6.0, -1.4, 0.0, 7.0, 5.2, -16.57]),
            0.01,
        ); //Filled by column
    }

    #[test]
    pub fn test_lu_decomposition_3() {
        let a = Matrix::from_vec(
            10,
            10,
            vec![
                5.0, 2.0, 3.0, 1.33, 4.89, 2.54, 5.0, 3.6, 3.98, 4.3, 6.0, 1.0, 0.0, 5.6, 0.0,
                4.23, 7.6, 0.0, 8.78, 454.77, 7.0, 8.0, 1.0, 4.3, 5.4, 22.4, 78.3, 7.3, 5.6, 0.0,
                6.0, 2.0, 1.23, 1.236, 2.6, 45.0, 5.3, 5.3, 44.0, 8.0, 3.6, 0.0, 2.8, 2.3, 0.0,
                1.3, 8.3, 0.0, 1.4, 9.3, 0.0, 1.0, 1.3, 5.3, 0.0, 8.9, 99.0, 8.0, 7.0, 1.0, 6.1,
                0.0, 4.2, 0.0, 6.4, 0.0, 15.0, 8.0, 0.0, 3.6, 44.3, 0.0, 2.2, 2.3, 5.3, 6.3, 2.6,
                1.0, 0.0, 6.0, 4.9, 2.123, 5.3, 14.0, 0.0, 1.23, 6.23, 0.0, 0.0, 0.0, 4.12, 1.4,
                1.3, 0.0, 4.3, 0.0, 14.0, 0.0, 0.0, 0.0,
            ],
        ); //Filled by column
        let lu = super::lu_decomposition(a);
        let l = lu.l;
        let u = lu.u;
        let L = vec![
            vec![1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            vec![0.4, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            vec![
                0.6,
                2.571428571428571,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            vec![
                0.266,
                -2.86,
                -1.044568965517241,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            vec![
                0.978,
                4.191428571428571,
                1.4025,
                -0.099794691412499,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            vec![
                0.508,
                -0.844285714285714,
                -1.402068965517241,
                -13.676617758376807,
                -8.358307432950832,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            vec![
                1.0,
                -1.142857142857143,
                -4.661206896551724,
                2.5505237460939,
                -5.531027646622009,
                0.773179454337525,
                1.0,
                0.0,
                0.0,
                0.0,
            ],
            vec![
                0.72,
                3.085714285714286,
                0.831896551724138,
                -1.14628897087253,
                -0.075452781262509,
                0.157218084702653,
                0.095791995738045,
                1.0,
                0.0,
                0.0,
            ],
            vec![
                0.796,
                -2.86,
                -0.899137931034483,
                -12.692305067374391,
                -6.077232788905211,
                0.976642325593235,
                -0.207507271030967,
                -6.48532935552203,
                1.0,
                0.0,
            ],
            vec![
                0.86,
                -321.15,
                -100.411379310344828,
                89.60256779649198,
                52.323698308722285,
                -3.763850942172137,
                -0.902696003863724,
                172.08155990392869,
                171.521300647463942,
                1.0,
            ],
        ];
        let U = vec![
            vec![5.0, 6.0, 7.0, 6.0, 3.6, 0.0, 6.1, 44.3, 4.9, 4.12],
            vec![
                0.0, -1.4, 5.2, -0.4, -1.44, 1.0, -2.44, -17.72, 0.163, -0.248,
            ],
            vec![
                0.0,
                0.0,
                -16.571428571428571,
                -1.341428571428571,
                4.342857142857143,
                -1.271428571428571,
                6.814285714285714,
                21.185714285714286,
                1.940857142857143,
                -0.534285714285714,
            ],
            vec![
                0.0,
                0.0,
                0.0,
                -2.905214655172414,
                1.760413793103448,
                6.831905172413793,
                -1.483008620689655,
                -38.033060344827586,
                15.190139137931034,
                -2.363298275862069,
            ],
            vec![
                0.0,
                0.0,
                0.0,
                0.0,
                -3.400320048758935,
                -1.726462131559511,
                0.9562536123362,
                2.738252479414988,
                -6.681559752217253,
                1.823605377844654,
            ],
            vec![
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                86.968709510072635,
                -7.894638982463939,
                -498.73778281032294,
                153.502830283310598,
                -20.131121059450445,
            ],
            vec![
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                53.049710668328869,
                534.562949449490115,
                -183.820914433756567,
                38.785184501438674,
            ],
            vec![
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                -10.027987146771019,
                4.737734178672945,
                -4.878432997189248,
            ],
            vec![
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                -6.832406694852099,
                -27.31155688289603,
            ],
            vec![
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                5462.745862241134069,
            ],
        ];
        assert_matrix_eq_float_2(l, L, 0.01); //Filled by column
        assert_matrix_eq_float_2(u, U, 0.01); //Filled by column
    }
}
