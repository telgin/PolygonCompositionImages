from shape import Shape
import random
import numpy

"""
Author: Thomas Elgin (https://github.com/telgin)
"""

class Square(Shape):
    """
    Quadrilateral implementation.
    """

    def randomizePoints(self):
        """
        Randomizes the points, essentially creating a new small shape
        somewhere within the bounds of the image
        """

        self.points = numpy.uint32(numpy.zeros([4, 2]))

        startsize = 5

        # pick a random point on the image (upper left of square)
        self.points[0] = [random.randint(0, self.imageBounds[0]-(startsize+1)),
                          random.randint(0, self.imageBounds[1]-(startsize+1))]

        #upper right
        self.points[1] = [self.points[0][0], self.points[0][1]+startsize]

        #lower right
        self.points[2] = [self.points[0][0]+startsize, self.points[0][1]+startsize]

        #lower left
        self.points[3] = [self.points[0][0]+startsize, self.points[0][1]]


    def mutate(self, heat=10):
        """
        Redefine mutate so we're not modifying individual vertices. The definition of a
        square would not allow for that. This will translate or scale the vertices randomly.
        :param heat: The length of the range of the random number. The range
        is centered on the current number.
        """

        # must have this in order to allow undoMutate
        self.oldPoints = numpy.copy(self.points)

        # randomly choose translate or scale
        if random.random() > .5: # scale

            center = numpy.average(self.points, axis=0)

            # (python do-while) init points to something out of bounds, try different
            # scale operations until you get one where all points are within the bounds
            points = numpy.array([[-1,-1], [-1, -1], [-1, -1], [-1, -1]])
            while not self.pointsBounded(points):

                # calculate scale factor from heat
                rand = (float(random.randint(0, heat)) / 100) / 2
                if random.random() > .5:
                    scale = 1 + (rand * 2)
                else:
                    scale = 1 - rand

                # apply scale factor
                points = numpy.copy(self.points)
                points = numpy.transpose([points[:, 0] - center[0], points[:, 1] - center[1]])
                points *= scale
                points = numpy.transpose([points[:, 0] + center[0], points[:, 1] + center[1]])
                points = numpy.round(points).astype(numpy.int)

            self.points = points

        else: # translate

            # decide how much to translate based on heat
            xmod = random.randint(0,heat)-(heat//2)
            ymod = random.randint(0,heat)-(heat//2)

            # compute min/max for x/y
            maxx, maxy = numpy.max(self.points, 0).astype(numpy.int)
            minx, miny = numpy.min(self.points, 0).astype(numpy.int)

            # make sure translation does not result in any points outside bounds
            xmod = max(xmod, -minx)
            xmod = min(xmod, (self.imageBounds[0]-1)-maxx)
            ymod = max(ymod, -miny)
            ymod = min(ymod, (self.imageBounds[1]-1)-maxy)

            self.points = numpy.transpose([self.points[:, 0] + xmod, self.points[:, 1] + ymod])




