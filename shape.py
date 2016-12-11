import numpy
import random

"""
Author: Thomas Elgin (https://github.com/telgin)
"""

class Shape:
    """
    The shape class holds the points of a polygon. It is assumed that the
    polygon has no crossing edges, meaning that the vertices are stored
    in clockwise order.
    """
    def __init__(self, bounds):
        """
        Creates a shape and randomizes the points
        :param bounds: The bounds of the image (max/min values of points)
        """
        self.points = numpy.zeros(1)
        self.oldPoints = numpy.zeros(1)
        self.imageBounds = bounds
        self.color = [0, 0, 0, 0]
        self.randomizePoints()

    def mutate(self, heat=10):
        """
        Mutates a vertex of the polygon which amounts to adding a random
        number to both x and y where the range is the length of the heat.
        :param heat: The length of the range of the random number. The range
        is centered on the current number.
        """
        self.oldPoints = numpy.copy(self.points)

        i = random.randint(0, numpy.shape(self.points)[0]-1)
        x = self.points[i][0]
        y = self.points[i][1]

        xmod = random.randint(0,heat)-(heat//2)
        ymod = random.randint(0,heat)-(heat//2)

        self.points[i][0] = min(self.imageBounds[0]-1, max(0, x+xmod))
        self.points[i][1] = min(self.imageBounds[1]-1, max(0, y+ymod))

    def undoMutate(self):
        """
        Undoes the last mutate by restoring the old points. Necessary for
        simulated annealing.
        """
        self.points = self.oldPoints

    def randomizePoints(self):
        """
        Randomize the points of the shape. Implemented in subclasses.
        """
        pass

    def boundX(self, num):
        """
        Clips the number to the bounds of the image in the x direction
        :param num: The x value
        :return: num clipped to the bounds of the image
        """
        return min(self.imageBounds[0]-1, max(0, num))

    def boundY(self, num):
        """
        Clips the number to the bounds of the image in the y direction
        :param num: The y value
        :return: num clipped to the bounds of the image
        """
        return min(self.imageBounds[1]-1, max(0, num))

    def pointsBounded(self, points):
        """
        Tells if the given points are bounded within the image
        :param points: A list of points
        :return: True if all points are within the bounds, false otherwise.
        """
        xs = points[:,0]
        xbounded = (xs >= 0).all() and (xs < self.imageBounds[0]).all()
        if not xbounded:
            return False

        ys = points[:,1]
        ybounded = (ys >= 0).all() and (ys < self.imageBounds[1]).all()
        return ybounded

    def __str__(self):
        return str(self.points)