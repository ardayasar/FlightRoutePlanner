import matplotlib.pyplot as plt
import numpy as np
import itertools

def distance(point1, point2):
    return np.linalg.norm(point1 - point2)

def total_distance(points_order, points):
    return sum(distance(points[i], points[j]) for i, j in zip(points_order[:-1], points_order[1:]))

def find_path(num_points, points, filename):

    shortest_path = None
    shortest_distance = float('inf')

    for perm in itertools.permutations(range(num_points)):
        current_distance = total_distance(perm, points)
        if current_distance < shortest_distance:
            shortest_distance = current_distance
            shortest_path = perm

    # Plot points and the shortest path
    plt.scatter(points[:, 0], points[:, 1], s=50, c='red', marker='o')
    for i, j in zip(shortest_path[:-1], shortest_path[1:]):
        plt.plot([points[i][0], points[j][0]], [points[i][1], points[j][1]], 'k-')

    plt.title("Shortest Path among Random Points")
    plt.savefig(filename)
    plt.close()  # Close the current plot

counter = 0
while True:
    num_points = 7
    points = np.random.rand(num_points, 2)
    filename = f"shortest_path_{counter}.png"  # create a new filename for each image
    find_path(num_points, points, filename)
    counter += 1
