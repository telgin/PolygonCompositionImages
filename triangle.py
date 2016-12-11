from shape import Shape
import random
import numpy

"""
Author: Thomas Elgin (https://github.com/telgin)
"""

class Triangle(Shape):
    """
    Triangle implementation. Defines triangle specific logic of
    which there should not be that much.
    """

    def randomizePoints(self):
        """
        Randomizes the points, essentially creating a new small triangle
        somewhere within the bounds of the image
        """

        self.points = numpy.uint32(numpy.zeros([3, 2]))

        # pick a random point on the image
        self.points[0] = [random.randint(0, self.imageBounds[0]-1), random.randint(0, self.imageBounds[1]-1)]

        # keep other points close to first point (start with small shape)
        modRange = 15

        xmod1 = self.boundX(random.randint(-modRange, modRange) + self.points[0][0])
        ymod1 = self.boundY(random.randint(-modRange, modRange) + self.points[0][1])
        self.points[1] = [xmod1, ymod1]

        xmod2 = self.boundX(random.randint(-modRange, modRange) + self.points[0][0])
        ymod2 = self.boundY(random.randint(-modRange, modRange) + self.points[0][1])
        self.points[2] = [xmod2, ymod2]
