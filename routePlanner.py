import math
import matplotlib.pyplot as plt
import random
import bezier
import numpy as np
# import time
airports = {
    "AP1": {
        "airportName": "AIRPORT-1",
        "airportLocation": [10, 10]
    },
    "AP2": {
        "airportName": "AIRPORT-2",
        "airportLocation": [20, 20]
    },
    "AP3": {
        "airportName": "AIRPORT-2",
        "airportLocation": [15, 15]
    }
}


def generate_runway(airport_location):
    """Generate a random runway for a given airport location."""
    heading = random.randint(0, 360)
    length = random.randint(1, 3)

    radian_angle = math.radians(heading)

    half_length_delta_x = (length / 2) * math.sin(radian_angle)
    half_length_delta_y = (length / 2) * math.cos(radian_angle)

    runway_start = [airport_location[0] - half_length_delta_x, airport_location[1] - half_length_delta_y]
    runway_end = [airport_location[0] + half_length_delta_x, airport_location[1] + half_length_delta_y]

    return {
        "runwayMark": f"RW{heading}",
        "runwayStartPoint": runway_start,
        "runwayEndPoint": runway_end,
        "runwaySurface": "",
        "runwayApproach": heading,
        "runwayApproachStartDistance": 6
    }


def compute_distance(point1, point2):
    """Compute Euclidean distance between two points."""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def calculate_approach_point(runway, reverse=False):
    radian_angle = math.radians(runway["runwayApproach"])

    delta_x = runway["runwayApproachStartDistance"] * math.sin(radian_angle)
    delta_y = runway["runwayApproachStartDistance"] * math.cos(radian_angle)

    if reverse:
        return [runway["runwayStartPoint"][0] - delta_x, runway["runwayStartPoint"][1] - delta_y]
    else:
        return [runway["runwayStartPoint"][0] + delta_x, runway["runwayStartPoint"][1] + delta_y]


def get_route(departure_code, arrival_code, database):
    if departure_code not in database or arrival_code not in database:
        return "Invalid airport code provided."

    departure_runway = database[departure_code]["runways"][0]
    arrival_runway = database[arrival_code]["runways"][0]

    departure_lineup_point = calculate_approach_point(departure_runway, reverse=True)
    arrival_lineup_point = calculate_approach_point(arrival_runway)

    distance = compute_distance(departure_lineup_point, arrival_lineup_point)

    return {
        "Departure": departure_code,
        "Line-up Point Departure": departure_lineup_point,
        "Arrival": arrival_code,
        "Line-up Point Arrival": arrival_lineup_point,
        "Distance": distance
    }


def plot_route(route, database):
    departure_point = route["Line-up Point Departure"]
    arrival_point = route["Line-up Point Arrival"]
    departure_airport = database[route["Departure"]]
    arrival_airport = database[route["Arrival"]]

    departure_runway = departure_airport["runways"][0]
    arrival_runway = arrival_airport["runways"][0]

    radian_angle = math.radians(departure_runway["runwayApproach"])
    straight_path_x = departure_runway["runwayEndPoint"][0] + 1 * math.sin(radian_angle)
    straight_path_y = departure_runway["runwayEndPoint"][1] + 1 * math.cos(radian_angle)
    straight_path_point = [straight_path_x, straight_path_y]

    control_distance = 1 #Curve control
    control_point_1_x = straight_path_point[0] + control_distance * math.sin(radian_angle)
    control_point_1_y = straight_path_point[1] + control_distance * math.cos(radian_angle)
    control_point_1 = [control_point_1_x, control_point_1_y]

    radian_angle_arrival = math.radians(arrival_runway["runwayApproach"])
    control_point_2_x = arrival_runway["runwayStartPoint"][0] - control_distance * math.sin(radian_angle_arrival)
    control_point_2_y = arrival_runway["runwayStartPoint"][1] - control_distance * math.cos(radian_angle_arrival)
    control_point_2 = [control_point_2_x, control_point_2_y]

    control_point_3 = [
        control_point_1[0] + 0.33 * (control_point_2[0] - control_point_1[0]),
        control_point_1[1] + 0.33 * (control_point_2[1] - control_point_1[1])
    ]

    control_point_4 = [
        control_point_1[0] + 0.67 * (control_point_2[0] - control_point_1[0]),
        control_point_1[1] + 0.67 * (control_point_2[1] - control_point_1[1])
    ]

    alignment_distance = 1 #Curve control
    align_point_x = arrival_runway["runwayStartPoint"][0] - alignment_distance * math.sin(radian_angle_arrival)
    align_point_y = arrival_runway["runwayStartPoint"][1] - alignment_distance * math.cos(radian_angle_arrival)
    align_point = [align_point_x, align_point_y]

    nodes = np.asfortranarray(
        [
            [straight_path_point[0], control_point_1[0], control_point_3[0], control_point_4[0], control_point_2[0],
             align_point[0]],
            [straight_path_point[1], control_point_1[1], control_point_3[1], control_point_4[1], control_point_2[1],
             align_point[1]]
        ]
    )

    curve = bezier.Curve(nodes, degree=5)
    curve_vals = curve.evaluate_multi(np.linspace(0.0, 1.0, 200))

    for code, data in database.items():
        plt.scatter(*data["airportLocation"], marker='o', label=f"{code} - {data['airportName']}")
        for runway in data["runways"]:
            plt.plot([runway["runwayStartPoint"][0], runway["runwayEndPoint"][0]],
                     [runway["runwayStartPoint"][1], runway["runwayEndPoint"][1]], 'k-')

    plt.plot([departure_runway["runwayStartPoint"][0], departure_runway["runwayEndPoint"][0], straight_path_point[0],
              *curve_vals[0, :], arrival_runway["runwayStartPoint"][0]],
             [departure_runway["runwayStartPoint"][1], departure_runway["runwayEndPoint"][1], straight_path_point[1],
              *curve_vals[1, :], arrival_runway["runwayStartPoint"][1]], 'r-')

    plt.annotate("Start", departure_runway["runwayStartPoint"], xytext=(-20, 5), textcoords='offset points')
    plt.annotate("End", departure_runway["runwayEndPoint"], xytext=(-10, 5), textcoords='offset points')
    plt.annotate("+1 Mile", straight_path_point, xytext=(5, 5), textcoords='offset points')
    # plt.annotate("CP1", control_point_1, xytext=(10, -15), textcoords='offset points')
    # plt.annotate("CP2", control_point_2, xytext=(-25, 10), textcoords='offset points')
    # plt.annotate("CP3", control_point_3, xytext=(10, 10), textcoords='offset points')
    # plt.annotate("CP4", control_point_4, xytext=(10, -10), textcoords='offset points')
    plt.annotate("Align", align_point, xytext=(-30, 10), textcoords='offset points')
    plt.annotate("End", arrival_runway["runwayEndPoint"], xytext=(-20, -10), textcoords='offset points')

    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.title('Flight Route Planner')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_route_multiple(route_array, database):
    for route in route_array:
        departure_point = route["Line-up Point Departure"]
        arrival_point = route["Line-up Point Arrival"]
        departure_airport = database[route["Departure"]]
        arrival_airport = database[route["Arrival"]]

        departure_runway = departure_airport["runways"][0]
        arrival_runway = arrival_airport["runways"][0]

        radian_angle = math.radians(departure_runway["runwayApproach"])
        straight_path_x = departure_runway["runwayEndPoint"][0] + 1 * math.sin(radian_angle)
        straight_path_y = departure_runway["runwayEndPoint"][1] + 1 * math.cos(radian_angle)
        straight_path_point = [straight_path_x, straight_path_y]

        control_distance = 3  # Curve control
        control_point_1_x = straight_path_point[0] + control_distance * math.sin(radian_angle)
        control_point_1_y = straight_path_point[1] + control_distance * math.cos(radian_angle)
        control_point_1 = [control_point_1_x, control_point_1_y]

        radian_angle_arrival = math.radians(arrival_runway["runwayApproach"])
        control_point_2_x = arrival_runway["runwayStartPoint"][0] - control_distance * math.sin(radian_angle_arrival)
        control_point_2_y = arrival_runway["runwayStartPoint"][1] - control_distance * math.cos(radian_angle_arrival)
        control_point_2 = [control_point_2_x, control_point_2_y]

        control_point_3 = [
            control_point_1[0] + 0.33 * (control_point_2[0] - control_point_1[0]),
            control_point_1[1] + 0.33 * (control_point_2[1] - control_point_1[1])
        ]

        control_point_4 = [
            control_point_1[0] + 0.67 * (control_point_2[0] - control_point_1[0]),
            control_point_1[1] + 0.67 * (control_point_2[1] - control_point_1[1])
        ]

        alignment_distance = 1  # Curve control
        align_point_x = arrival_runway["runwayStartPoint"][0] - alignment_distance * math.sin(radian_angle_arrival)
        align_point_y = arrival_runway["runwayStartPoint"][1] - alignment_distance * math.cos(radian_angle_arrival)
        align_point = [align_point_x, align_point_y]

        nodes = np.asfortranarray(
            [
                [straight_path_point[0], control_point_1[0], control_point_3[0], control_point_4[0], control_point_2[0],
                 align_point[0]],
                [straight_path_point[1], control_point_1[1], control_point_3[1], control_point_4[1], control_point_2[1],
                 align_point[1]]
            ]
        )

        curve = bezier.Curve(nodes, degree=5)
        curve_vals = curve.evaluate_multi(np.linspace(0.0, 1.0, 200))

        for code, data in database.items():
            # plt.scatter(*data["airportLocation"], marker='o', label=f"{code} - {data['airportName']}")
            for runway in data["runways"]:
                plt.plot([runway["runwayStartPoint"][0], runway["runwayEndPoint"][0]],
                         [runway["runwayStartPoint"][1], runway["runwayEndPoint"][1]], 'k-')

        plt.plot(
            [departure_runway["runwayStartPoint"][0], departure_runway["runwayEndPoint"][0], straight_path_point[0],
             *curve_vals[0, :], arrival_runway["runwayStartPoint"][0]],
            [departure_runway["runwayStartPoint"][1], departure_runway["runwayEndPoint"][1], straight_path_point[1],
             *curve_vals[1, :], arrival_runway["runwayStartPoint"][1]], 'r-')

        plt.annotate("Start", departure_runway["runwayStartPoint"], xytext=(-20, 5), textcoords='offset points')
        plt.annotate("End", departure_runway["runwayEndPoint"], xytext=(-10, 5), textcoords='offset points')
        plt.annotate("+1 Mile", straight_path_point, xytext=(5, 5), textcoords='offset points')
        # plt.annotate("CP1", control_point_1, xytext=(10, -15), textcoords='offset points')
        # plt.annotate("CP2", control_point_2, xytext=(-25, 10), textcoords='offset points')
        # plt.annotate("CP3", control_point_3, xytext=(10, 10), textcoords='offset points')
        # plt.annotate("CP4", control_point_4, xytext=(10, -10), textcoords='offset points')
        plt.annotate("Align", align_point, xytext=(-30, 10), textcoords='offset points')
        plt.annotate("End", arrival_runway["runwayEndPoint"], xytext=(-20, -10), textcoords='offset points')

        plt.xlabel('Latitude')
        plt.ylabel('Longitude')
        plt.title('Flight Route Planner')
        plt.legend()
    plt.grid(True)
    plt.show()

while True:

    for airport_code, airport_data in airports.items():
        airports[airport_code]["runways"] = [generate_runway(airport_data["airportLocation"]) for _ in range(1)]

    route1 = get_route("AP1", "AP2", airports)
    # route2 = get_route("AP3", "AP2", airports)

    plot_route_multiple([route1], airports)


    # time.sleep(5)
