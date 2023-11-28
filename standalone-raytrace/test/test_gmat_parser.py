from .test_config import *
from src import gmat_parser

def _is_in_interval(value, center, epsilon):
    return value <= center + epsilon and value >= center - epsilon

def test_parse_report_file():
    parameters = gmat_parser.parse_report_file(GMAT_REPORT_FILE_PATH)
    assert parameters["Sat.X"][0] == '7000'
    assert parameters["Sat.X"][-1] == '6436.596020641517'
    assert parameters["Sat.Y"][0] == '0'
    assert parameters["Sat.Y"][-1] == '2749.0033407397'
    assert parameters["Sat.Z"][0] == '0'
    assert parameters["Sat.Z"][-1] == '-0.1119942899460718'
    assert parameters["Sun.X"] == '25212844.34650287'
    assert parameters["Sun.Y"] == '-132968705.362406'
    assert parameters["Sun.Z"] == '-57648316.13335131'
    assert parameters["BetaAngle"] == '-23.07197787367823'
    assert parameters["UTC"] == '01 Jan 2000 00:00:00.000'
    assert parameters["SMA"] == '7000'
    assert parameters["Sat.Altitude"] == '621.8637000177523'
    assert parameters["ElapsedSecs"][0] == '0'
    assert parameters["ElapsedSecs"][-1] == '12000.0000001397'

def test_parse_eclipse_locator_file():
    parameters = gmat_parser.parse_report_file(GMAT_REPORT_FILE_PATH)
    eclipse_start_and_finish, period = gmat_parser.parse_eclipse_locator(GMAT_ECLIPSE_LOCATOR_FILE_PATH, parameters)
    assert _is_in_interval(eclipse_start_and_finish[0], 594.2, 0.1)
    assert _is_in_interval(eclipse_start_and_finish[1], 2637.5, 0.1)
    assert _is_in_interval(period, 5828.5, 0.1)

def test_parse_no_eclipse_locator_file():
    parameters = gmat_parser.parse_report_file(GMAT_REPORT_FILE_PATH)
    eclipse_start_and_finish, period = gmat_parser.parse_eclipse_locator(GMAT_ECLIPSE_LOCATOR_FILE_PATH_NO_ECLIPSE, parameters)
    assert eclipse_start_and_finish == (-1, -1)
    assert _is_in_interval(period, 5828.5, 0.1)
