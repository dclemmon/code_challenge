#! /usr/bin/env python3

"""
    This is the coding challenge submission for Cameron Lemmon
    This reads in a yaml file that describes several polygons,
    it then finds the neighbors, and colorizes them.
"""

import sys
import random

import sympy
import yaml

from PIL import Image, ImageDraw
from sympy import Polygon


COLORS = {'RED', 'GREEN', 'BLUE', 'YELLOW'}


class Layout:
    """
        A class to contain our polygons
    """
    def __init__(self, *args):
        """
            Given data about the piece's points, build out data
        """
        self.polygons = list(args)

    def add_polygon(self, poly):
        """
            Add a polygon in our layout
        """
        self.polygons.append(poly)

    def find_neighbors(self):
        """
            Find all the neighbors and assign the links
        """
        for poly in self.polygons:
            for pgon in poly.wiggle().values():
                for shape in self.polygons:
                    if poly is shape:
                        # We found ourselves...
                        continue
                    # Check for an intersection with our wiggled polygon
                    is_neighbor = pgon.intersection(shape)
                    if is_neighbor:
                        # Make our connections if we found any intersection
                        poly.add_neighbor(shape)

    def show_neighbors(self):
        """
            show our neighbor relationships
        """
        for elem in self.polygons:
            print(f"Polygon {elem.label} has the neighbors: {[x.label for x in elem.neighbors]}")

    def colorize(self):
        """
            Colorize the layout using red, green, blue, and yellow with no two
            neighbors colored the same
        """
        for shape in self.polygons:
            choices = COLORS.difference({x.color for x in shape.neighbors})
            shape.color = random.choice(list(choices))

    @classmethod
    def from_yaml_file(cls, file_name):
        """
            Build our layout from a yaml file
            (additional classmethods could be created to expanded to include
            other file types)
        """
        polygons = []
        with open(file_name, encoding='utf-8', mode='r') as stream:
            data = yaml.load(stream, Loader=yaml.Loader)
        for name, points in data.get('layout', {}).items():
            converted_points = []
            for point in points.get('points'):
                converted_points.append(tuple(map(int, point.split(','))))
            polygons.append(Poly(*converted_points, name=name))
        layout = cls(*polygons)
        return layout


class Poly(Polygon):
    """
       Build out our polygon a bit
    """

    def __init__(self, *args, n=0, name=None, **kwargs):
        """
           Expand what it means to be a polygon in this case
        """
        self._neighbors = set()
        self.label = name
        self.color = None

    def __new__(cls, *args, n=0, **kwargs):
        return super().__new__(cls, *args, n=n, **kwargs)

    def add_neighbor(self, neighbor):
        """Add a neighbor"""
        self._neighbors.add(neighbor)

    def wiggle(self, amount=1):
        """
            Move around!  This returns four versions of the polygon
            moved by the provided amount in each cardinal direction.
        """
        wiggled = {}
        directions = {
            'north': (0, amount),
            'east': (amount, 0),
            'south': (0, -1 * amount),
            'west': (-1 * amount, 0)
        }
        for direction, value in directions.items():
            new_poly_points = [x + value for x in self.vertices]
            wiggled[direction] = sympy.Polygon(*new_poly_points)
        return wiggled

    @property
    def neighbors(self):
        """Return neighbors"""
        return self._neighbors


def draw_layout(layout, scale=1):
    """
    Given an layout, show us!
    """
    img = Image.new(mode='RGB', size=(100,100))
    draw = ImageDraw.Draw(img)
    for shape in layout.polygons:
        points = [(x * scale, y * scale) for (x, y) in shape.vertices]
        draw.polygon(points, fill=shape.color, outline='BLACK')
    img.show()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 code_challenge.py test.yaml")
        sys.exit(1)
    layout = Layout.from_yaml_file(sys.argv[1])
    layout.find_neighbors()
    layout.show_neighbors()
    layout.colorize()
    for elem in layout.polygons:
        print(f'Polygon {elem.label} is {elem.color}')
    draw_layout(layout, scale=2)
