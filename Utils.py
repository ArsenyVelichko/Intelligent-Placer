from matplotlib import pyplot as plt

import re

def get_cmap(n, name='hsv'):
    return plt.cm.get_cmap(name, n)

def parse_poly(str):
    points = re.findall('\((.*?)\)', str)

    polygon = []
    for point in points:
        x, y = list(map(float, point.split(',')))
        polygon.append((x, y))

    return  polygon