from typing import Any
import math
import dateparser

GMAT_PARAMETER_NAMES = {
    "Sat.EarthMJ2000Eq.X",
    "Sat.EarthMJ2000Eq.Y",
    "Sat.EarthMJ2000Eq.Z",
    "Sun.EarthMJ2000Eq.X",
    "Sun.EarthMJ2000Eq.Y",
    "Sun.EarthMJ2000Eq.Z",
    "Sat.Earth.BetaAngle",
    "Sat.UTCGregorian",
    "Sat.Earth.SMA",
    "Sat.Earth.Altitude",
    "Sat.ElapsedSecs",
}

GMAT_ECLIPSE_NAMES = {
    "Start Time (UTC)",
    "Stop Time (UTC)",
    "Type",
    "Event Number",
    "Duration",
    "Total Duration (s)",
}

INTERNAL_PARAMETERS = {
    "Sat.X",
    "Sat.Y",
    "Sat.Z",
    "Sun.X",
    "Sun.Y",
    "Sun.Z",
    "BetaAngle",
    "UTC",
    "SMA",
    "Sat.Altitude",
    "ElapsedSecs",
}

INTERNAL_CONSTANT_PARAMETERS = {
    "Sun.X",
    "Sun.Y",
    "Sun.Z",
    "BetaAngle",
    "UTC",
    "SMA",
    "Sat.Altitude",
}


EARTH_MU = 398600.4415


class Position:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z


class GMATParameters:
    def __init__(
        self,
        beta_angle: float,
        sun_position: Position,
        sat_position: list[Position],
        elapsed_secs: list[float],
        altitude: float,
        eclipse_start_finish: tuple[float, float],
        period: float,
    ):
        self.beta_angle = beta_angle
        self.sun_position = sun_position
        self.sat_position = sat_position
        self.elapsed_secs = elapsed_secs
        self.altitude = altitude
        self.eclipse_start_finish = eclipse_start_finish
        self.period = period


def split_line(line: str) -> list[str]:
    filtered_line = filter(lambda x: len(x) > 0, line.split("  "))
    return list(map(lambda x: x.strip(), filtered_line))


def translate_parameters(params: list[str]) -> list[str]:
    sat = ""
    for param in params:
        if param.endswith("EarthMJ2000Eq.X") and not param.startswith("Sun"):
            sat = param.split(".")[0]

    translation = {
        f"{sat}.EarthMJ2000Eq.X": "Sat.X",
        f"{sat}.EarthMJ2000Eq.Y": "Sat.Y",
        f"{sat}.EarthMJ2000Eq.Z": "Sat.Z",
        "Sun.EarthMJ2000Eq.X": "Sun.X",
        "Sun.EarthMJ2000Eq.Y": "Sun.Y",
        "Sun.EarthMJ2000Eq.Z": "Sun.Z",
        f"{sat}.Earth.BetaAngle": "BetaAngle",
        f"{sat}.UTCGregorian": "UTC",
        f"{sat}.Earth.SMA": "SMA",
        f"{sat}.Earth.Altitude": "Sat.Altitude",
        f"{sat}.ElapsedSecs": "ElapsedSecs",
    }

    return list(map(lambda x: translation[x] if x in translation else x, params))


def calculate_eclipse_start_and_finish(data, start_epoch, period, idx_from_param):
    eclipse_start = dateparser.parse(data[idx_from_param["Start Time (UTC)"]])
    eclipse_finish = dateparser.parse(data[idx_from_param["Stop Time (UTC)"]])
    start_epoch = dateparser.parse(start_epoch)

    eclipse_start_secs = (eclipse_start - start_epoch).total_seconds()
    eclipse_finish_secs = (eclipse_finish - start_epoch).total_seconds() - period
    if eclipse_start_secs > period:
        eclipse_start_secs -= period

    return (eclipse_start_secs, eclipse_finish_secs)


def parse_report_file(report_filename):
    file = open(report_filename, "r")

    lines = list()

    for line in file.readlines():
        lines.append(line)

    header = translate_parameters(split_line(lines[0]))  # lines[0].strip().split()

    idx_from_param = {}

    for idx, p in enumerate(header):
        if p in INTERNAL_PARAMETERS:
            idx_from_param[p] = idx

    parameters: dict[str, Any] = {p: list() for p in idx_from_param.keys()}

    for line in lines[1::]:
        values = split_line(line)  # line.strip().split()
        for p in INTERNAL_PARAMETERS:
            parameters[p].append(values[idx_from_param[p]])

    for p in INTERNAL_CONSTANT_PARAMETERS:
        parameters[p] = parameters[p][0]

    file.close()

    return parameters


def parse_eclipse_locator(eclipse_locator_filename, parameters):
    file = open(eclipse_locator_filename, "r")

    start_epoch: float = parameters["UTC"]
    sma: float = parameters["SMA"]

    period = 2 * math.pi * math.sqrt(float(sma) ** 3 / EARTH_MU)

    line = ""
    while not line.startswith("Start Time"):
        line = file.readline()
    header = split_line(line)
    idx_from_param = {}

    for idx, p in enumerate(header):
        if p in GMAT_ECLIPSE_NAMES:
            idx_from_param[p] = idx
    # Find the Event Number 2 of type Umbra

    type_id = idx_from_param["Type"]
    event_number_id = idx_from_param["Event Number"]

    eclipse_start_and_finish: tuple[float, float] = ()
    for line in file.readlines():
        if len(line) <= 1 or line.startswith("Number of"):
            break
        data = split_line(line)
        if data[type_id] == "Umbra" and data[event_number_id] == "2":
            eclipse_start_and_finish = calculate_eclipse_start_and_finish(
                data, start_epoch, period, idx_from_param
            )
            break

    file.close()

    return eclipse_start_and_finish, period


def parse_gmat(report_filename, eclipse_filename) -> GMATParameters:
    parameters = parse_report_file(report_filename)

    eclipse_start_and_finish, period = parse_eclipse_locator(
        eclipse_filename, parameters
    )

    n_steps = 0

    for elapsed_time in parameters["ElapsedSecs"]:
        if float(elapsed_time) < float(period):
            n_steps += 1

    altitude: float = parameters["Sat.Altitude"]
    beta_angle: float = parameters["BetaAngle"]
    sun_position = Position(
        float(parameters["Sun.X"]),
        float(parameters["Sun.Y"]),
        float(parameters["Sun.Z"]),
    )
    sat_position = [
        Position(
            float(parameters["Sat.X"][i]),
            float(parameters["Sat.Y"][i]),
            float(parameters["Sat.Z"][i]),
        )
        for i in range(n_steps)
    ]
    elapsed_secs = [parameters["ElapsedSecs"][i] for i in range(n_steps)]

    return GMATParameters(
        beta_angle,
        sun_position,
        sat_position,
        elapsed_secs,
        altitude,
        eclipse_start_and_finish,
        period,
    )
