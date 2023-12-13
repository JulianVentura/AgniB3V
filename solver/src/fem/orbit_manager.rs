pub struct OrbitParameters {
    pub orbit_period: f64,
    pub orbit_divisions: Vec<f64>,
    pub eclipse_start: f64,
    pub eclipse_end: f64,
}

pub struct OrbitManager {
    orbit_period: f64,
    time_divisions: Vec<f64>,
    eclipse_divisions: Vec<(usize, bool)>,
    division_idx: usize,
}

impl OrbitManager {
    pub fn new(parameters: &OrbitParameters) -> Self {
        let expanded_divisions = Self::expand_time_divisions(
            &parameters.orbit_divisions,
            parameters.eclipse_start,
            parameters.eclipse_end,
        );

        let eclipse_divisions = Self::expand_eclipse_divisions(
            &expanded_divisions,
            parameters.eclipse_start,
            parameters.eclipse_end,
        );

        OrbitManager {
            orbit_period: parameters.orbit_period,
            time_divisions: expanded_divisions.iter().map(|(_, x)| *x).collect(),
            eclipse_divisions,
            division_idx: 0,
        }
    }

    pub fn eclipse_divisions(&self) -> &Vec<(usize, bool)> {
        &self.eclipse_divisions
    }

    pub fn time_to_next(&mut self, time: f64) -> f64 {
        let orbit_time = time % self.orbit_period;
        self.update_division_idx(orbit_time);
        let next_idx = (self.division_idx + 1) % self.time_divisions.len();

        match next_idx {
            0 => self.orbit_period - orbit_time,
            _ => self.time_divisions[next_idx] - orbit_time,
        }
    }

    pub fn current_index(&mut self, time: f64) -> usize {
        let orbit_time = time % self.orbit_period;
        self.update_division_idx(orbit_time);
        self.division_idx
    }

    fn update_division_idx(&mut self, orbit_time: f64) {
        let divisions = &self.time_divisions;
        let idx = &mut self.division_idx;

        loop {
            let next_idx = (*idx + 1) % divisions.len();
            if next_idx == 0 {
                if divisions[*idx] <= orbit_time && orbit_time < self.orbit_period {
                    return;
                }
            } else {
                if divisions[*idx] <= orbit_time && orbit_time < divisions[next_idx] {
                    return;
                }
            }

            *idx = next_idx;
        }
    }

    //TODO:
    // - Optimization: If the eclipse start or end happens to be equal or very close to a division,
    // we could save on one new division.
    fn expand_time_divisions(
        orbit_divisions: &Vec<f64>,
        eclipse_start: f64,
        eclipse_end: f64,
    ) -> Vec<(usize, f64)> {
        let mut expanded_divisions = vec![];

        let mut first = eclipse_start;
        let mut last = eclipse_end;
        if eclipse_end < eclipse_start {
            first = eclipse_end;
            last = eclipse_start;
        }

        for (idx, orbit_time) in orbit_divisions.iter().enumerate() {
            let next_idx = (idx + 1) % orbit_divisions.len();
            expanded_divisions.push((idx, *orbit_time));

            if &first < &orbit_divisions[next_idx] && &first > orbit_time {
                expanded_divisions.push((idx, first));
            }

            if &last < &orbit_divisions[next_idx] && &last > orbit_time {
                expanded_divisions.push((idx, last));
            }
        }

        expanded_divisions
    }

    fn expand_eclipse_divisions(
        expanded_time_divisions: &Vec<(usize, f64)>,
        eclipse_start: f64,
        eclipse_end: f64,
    ) -> Vec<(usize, bool)> {
        let mut eclipse_divisions = vec![];

        for (idx, orbit_time) in expanded_time_divisions {
            let in_eclipse = Self::is_in_eclipse(eclipse_start, eclipse_end, *orbit_time);
            eclipse_divisions.push((*idx, in_eclipse));
        }

        eclipse_divisions
    }

    fn is_in_eclipse(eclipse_start: f64, eclipse_end: f64, orbit_time: f64) -> bool {
        if eclipse_start <= eclipse_end {
            return orbit_time >= eclipse_start && orbit_time < eclipse_end;
        } else {
            return orbit_time < eclipse_end || orbit_time >= eclipse_start;
        }
    }
}

#[cfg(test)]
mod tests {

    use super::OrbitParameters;

    use super::OrbitManager;

    fn assert_float_eq(value_1: f64, value_2: f64, precision: f64) {
        assert!(
            (value_1 - value_2).abs() < precision,
            "value1 {} != {}",
            value_1,
            value_2
        );
    }

    fn assert_expanded_eq(result: &Vec<(usize, f64)>, expected: &Vec<(usize, f64)>) {
        for (x, y) in result.iter().zip(expected) {
            assert!(x.0 == y.0);
            assert_float_eq(x.1, y.1, 0.01);
        }
    }

    fn assert_eclipse_eq(result: &Vec<(usize, bool)>, expected: &Vec<(usize, bool)>) {
        for (x, y) in result.iter().zip(expected) {
            assert!(x.0 == y.0);
            assert!(x.1 == y.1);
        }
    }

    #[test]
    fn test_is_in_eclipse_1() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 1500.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_2() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 500.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_3() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 2500.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_4() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 2000.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_5() {
        let start = 1000.0;
        let end = 2000.0;
        let time = 1000.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_6() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 2500.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_7() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 1500.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_8() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 3500.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_9() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 3000.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(is_in_eclipse);
    }

    #[test]
    fn test_is_in_eclipse_10() {
        let start = 3000.0;
        let end = 2000.0;
        let time = 2000.0;
        let is_in_eclipse = OrbitManager::is_in_eclipse(start, end, time);
        assert!(!is_in_eclipse);
    }

    #[test]
    fn test_expand_divisions_1() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 30.0;
        let end = 400.0;

        let expected = vec![
            (0, 0.0),
            (0, 30.0),
            (1, 100.0),
            (2, 300.0),
            (2, 400.0),
            (3, 500.0),
        ];
        let result = OrbitManager::expand_time_divisions(&divisions, start, end);
        assert_expanded_eq(&result, &expected);
    }

    #[test]
    fn test_expand_divisions_2() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 30.0;
        let end = 600.0;

        let expected = vec![
            (0, 0.0),
            (0, 30.0),
            (1, 100.0),
            (2, 300.0),
            (3, 500.0),
            (3, 600.0),
        ];
        let result = OrbitManager::expand_time_divisions(&divisions, start, end);
        assert_expanded_eq(&result, &expected);
    }

    #[test]
    fn test_expand_divisions_3() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 120.0;
        let end = 150.0;

        let expected = vec![
            (0, 0.0),
            (1, 100.0),
            (1, 120.0),
            (1, 150.0),
            (2, 300.0),
            (3, 500.0),
        ];
        let result = OrbitManager::expand_time_divisions(&divisions, start, end);
        assert_expanded_eq(&result, &expected);
    }

    #[test]
    fn test_expand_divisions_4() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 1.0;
        let end = 600.0;

        let expected = vec![
            (0, 0.0),
            (0, 1.0),
            (1, 100.0),
            (2, 300.0),
            (3, 500.0),
            (3, 600.0),
        ];
        let result = OrbitManager::expand_time_divisions(&divisions, start, end);
        assert_expanded_eq(&result, &expected);
    }

    #[test]
    fn test_expand_divisions_5() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 450.0;
        let end = 80.0;

        let expected = vec![
            (0, 0.0),
            (0, 80.0),
            (1, 100.0),
            (2, 300.0),
            (2, 450.0),
            (3, 500.0),
            (3, 600.0),
        ];
        let result = OrbitManager::expand_time_divisions(&divisions, start, end);
        assert_expanded_eq(&result, &expected);
    }

    #[test]
    fn test_expand_divisions_6() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 450.0;
        let end = 420.0;

        let expected = vec![
            (0, 0.0),
            (1, 100.0),
            (2, 300.0),
            (2, 420.0),
            (2, 450.0),
            (3, 500.0),
            (3, 600.0),
        ];
        let result = OrbitManager::expand_time_divisions(&divisions, start, end);
        assert_expanded_eq(&result, &expected);
    }

    #[test]
    fn test_expand_divisions_7() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = -1.0;
        let end = -1.0;

        let expected = vec![(0, 0.0), (1, 100.0), (2, 300.0), (3, 500.0), (3, 600.0)];
        let result = OrbitManager::expand_time_divisions(&divisions, start, end);
        assert_expanded_eq(&result, &expected);
    }

    #[test]
    fn test_expand_eclipse_1() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 30.0;
        let end = 400.0;

        let expected = vec![
            (0, false),
            (0, true),
            (1, true),
            (2, true),
            (2, false),
            (3, false),
        ];
        let expanded = OrbitManager::expand_time_divisions(&divisions, start, end);
        let result = OrbitManager::expand_eclipse_divisions(&expanded, start, end);
        assert_eclipse_eq(&result, &expected);
    }

    #[test]
    fn test_expand_eclipse_2() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 30.0;
        let end = 600.0;

        let expected = vec![
            (0, false),
            (0, true),
            (1, true),
            (2, true),
            (3, true),
            (3, false),
        ];
        let expanded = OrbitManager::expand_time_divisions(&divisions, start, end);
        let result = OrbitManager::expand_eclipse_divisions(&expanded, start, end);
        assert_eclipse_eq(&result, &expected);
    }

    #[test]
    fn test_expand_eclipse_3() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 120.0;
        let end = 150.0;

        let expected = vec![
            (0, false),
            (1, false),
            (1, true),
            (1, false),
            (2, false),
            (3, false),
        ];
        let expanded = OrbitManager::expand_time_divisions(&divisions, start, end);
        let result = OrbitManager::expand_eclipse_divisions(&expanded, start, end);
        assert_eclipse_eq(&result, &expected);
    }

    #[test]
    fn test_expand_eclipse_4() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 1.0;
        let end = 600.0;

        let expected = vec![
            (0, false),
            (0, true),
            (1, true),
            (2, true),
            (3, true),
            (3, true),
        ];
        let expanded = OrbitManager::expand_time_divisions(&divisions, start, end);
        let result = OrbitManager::expand_eclipse_divisions(&expanded, start, end);
        assert_eclipse_eq(&result, &expected);
    }

    #[test]
    fn test_expand_eclipse_5() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 450.0;
        let end = 80.0;

        let expected = vec![
            (0, true),
            (0, false),
            (1, false),
            (2, false),
            (2, true),
            (3, true),
            (3, true),
        ];
        let expanded = OrbitManager::expand_time_divisions(&divisions, start, end);
        let result = OrbitManager::expand_eclipse_divisions(&expanded, start, end);
        assert_eclipse_eq(&result, &expected);
    }

    #[test]
    fn test_expand_eclipse_6() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = 450.0;
        let end = 420.0;

        let expected = vec![
            (0, true),
            (1, true),
            (2, true),
            (2, false),
            (2, true),
            (3, true),
            (3, true),
        ];
        let expanded = OrbitManager::expand_time_divisions(&divisions, start, end);
        let result = OrbitManager::expand_eclipse_divisions(&expanded, start, end);
        assert_eclipse_eq(&result, &expected);
    }

    #[test]
    fn test_expand_eclipse_7() {
        let divisions = vec![0.0, 100.0, 300.0, 500.0];
        let start = -1.0;
        let end = -1.0;

        let expected = vec![(0, false), (1, false), (2, false), (3, false), (3, false)];
        let expanded = OrbitManager::expand_time_divisions(&divisions, start, end);
        let result = OrbitManager::expand_eclipse_divisions(&expanded, start, end);
        assert_eclipse_eq(&result, &expected);
    }

    #[test]
    fn test_update_division_idx_1() {
        let orbit_time = 5.0;
        let division_idx = 0;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 0;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_2() {
        let orbit_time = 11.0;
        let division_idx = 0;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 1;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_3() {
        let orbit_time = 12.0;
        let division_idx = 1;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 1;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_4() {
        let orbit_time = 21.0;
        let division_idx = 1;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 2;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_5() {
        let orbit_time = 25.0;
        let division_idx = 2;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 2;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_6() {
        let orbit_time = 3.0;
        let division_idx = 2;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 0;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_7() {
        let orbit_time = 25.0;
        let division_idx = 0;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 2;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_8() {
        let orbit_time = 15.0;
        let division_idx = 0;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 1;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_9() {
        let orbit_time = 45.0;
        let division_idx = 1;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0, 30.0, 40.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 4;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_10() {
        let orbit_time = 25.0;
        let division_idx = 3;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0, 30.0, 40.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 2;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_11() {
        let orbit_time = 5.0;
        let division_idx = 2;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0, 30.0, 40.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 0;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_update_division_idx_12() {
        let orbit_time = 0.0;
        let division_idx = 0;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0, 30.0, 40.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        manager.division_idx = division_idx;
        manager.update_division_idx(orbit_time);

        let actual_division_idx = 0;

        assert_eq!(manager.division_idx, actual_division_idx);
    }

    #[test]
    fn test_time_to_next_1() {
        let period = 6000.0;
        let orbit_time = 5.0 + period;

        let props = OrbitParameters {
            orbit_period: period,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        let time_left = manager.time_to_next(orbit_time);

        let actual_time = 5.0;

        assert_float_eq(time_left, actual_time, 0.0001);
    }

    #[test]
    fn test_time_to_next_2() {
        let period = 6000.0;
        let orbit_time = 11.0 + period;

        let props = OrbitParameters {
            orbit_period: period,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        let time_left = manager.time_to_next(orbit_time);

        let actual_time = 9.0;

        assert_float_eq(time_left, actual_time, 0.0001);
    }

    #[test]
    fn test_time_to_next_3() {
        let period = 6000.0;
        let orbit_time = 12.0 + period;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        let time_left = manager.time_to_next(orbit_time);

        let actual_time = 8.0;

        assert_float_eq(time_left, actual_time, 0.0001);
    }

    #[test]
    fn test_time_to_next_4() {
        let orbit_time = 21.0;

        let props = OrbitParameters {
            orbit_period: 6000.0,
            orbit_divisions: vec![0.0, 10.0, 20.0],
            eclipse_start: 1000.0,
            eclipse_end: 2000.0,
        };

        let mut manager = OrbitManager::new(&props);
        let time_left = manager.time_to_next(orbit_time);

        let actual_time = 5979.0;

        assert_float_eq(time_left, actual_time, 0.0001);
    }
}
