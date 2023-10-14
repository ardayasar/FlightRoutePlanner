import json
import matplotlib.pyplot as plt
import random


def random_color():
    return (random.random(), random.random(), random.random())


with open('airports.json', 'r') as file:
    data = json.load(file)

fig, ax = plt.subplots(figsize=(10, 10))


def get_runway_point(airport_runway_code, point_type="start"):
    airport_code, runway_mark = airport_runway_code.split('-')
    for runway in data[airport_code]['runways']:
        if runway['runwayMark'] == runway_mark:
            if point_type == "start":
                return runway['runwayStartPoint']
            elif point_type == "end":
                return runway['runwayEndPoint']
    return None


MILES_EXTENSION = 250


def calculate_extension(start_point, end_point, miles):
    delta_x = end_point[0] - start_point[0]
    delta_z = end_point[2] - start_point[2]

    magnitude = (delta_x**2 + delta_z**2)**0.5
    unit_delta_x = delta_x / magnitude
    unit_delta_z = delta_z / magnitude

    extended_x = end_point[0] + miles * unit_delta_x
    extended_z = end_point[2] + miles * unit_delta_z

    return (extended_x, extended_z)


selection_one = "KCIA-RW18"
selection_two = "KKBI-RW29"

point_one = get_runway_point(selection_one, "start")
point_two = get_runway_point(selection_two, "end")

if point_one and point_two:
    runway_end_one = get_runway_point(selection_one, "end")
    extended_takeoff_point = calculate_extension(point_one, runway_end_one, MILES_EXTENSION)

    runway_start_two = get_runway_point(selection_two, "start")
    extended_landing_point = calculate_extension(runway_start_two, point_two, MILES_EXTENSION)

    ax.plot([point_one[0], runway_end_one[0], extended_takeoff_point[0], extended_landing_point[0], point_two[0],
             runway_start_two[0]],
            [point_one[2], runway_end_one[2], extended_takeoff_point[1], extended_landing_point[1], point_two[2],
             runway_start_two[2]], 'purple', linestyle='--')

    ax.scatter(extended_takeoff_point[0], extended_takeoff_point[1], c='blue', marker='o')
    ax.scatter(extended_landing_point[0], extended_landing_point[1], c='red', marker='o')

for airport_code, airport_data in data.items():
    current_color = random_color()
    tower_x, _, tower_z = airport_data['towerPosition']
    ax.scatter(tower_x, tower_z, c=current_color, marker='o', label=f'Tower {airport_code}')

    for runway in airport_data['runways']:
        runway_start_x, _, runway_start_z = runway['runwayStartPoint']
        runway_end_x, _, runway_end_z = runway['runwayEndPoint']

        ax.scatter([runway_start_x, runway_end_x], [runway_start_z, runway_end_z], c=current_color, marker='x')
        ax.plot([runway_start_x, runway_end_x], [runway_start_z, runway_end_z], color=current_color)

ax.invert_yaxis()
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Z Coordinate')
ax.set_title('Airport and Runway Layout')
ax.legend()
plt.show()
