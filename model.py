from matplotlib import path
import numpy
import svgwrite
import math

"""
Author: Thomas Elgin (https://github.com/telgin)
"""

class Model:
    """
    Stores a model of the current polygon composition image. The target image,
    the current image, and a list of shapes.
    The target image is the original image.
    The current image is a cache of data used to calculate scores and is equivalent to the
    working approximation of the image with all the shapes applied. This could be written
    out to a file as a PNG, but it would not have the detail of writing an SVG.
    Shapes are lists of points.
    """

    def __init__(self, target, scale=.25):
        self.scale = scale
        img = target.resize([int(scale * dim) for dim in target.size])
        self.target = numpy.array(img)
        self.current = self.mkStarterImg(img)
        self.shapes = []


    def mkStarterImg(self, original):
        """
        Creates a starter image, which is an image where the background
        is the average color of the entire target image.
        :param original: The original (target) image
        :return: A numpy array with the image data of the current image
        """

        # split into channels
        r,g,b = original.split()
        r = numpy.array(r)
        g = numpy.array(g)
        b = numpy.array(b)

        # calculate average color per channel
        ravg = numpy.sum(r)/numpy.prod(r.shape)
        gavg = numpy.sum(g)/numpy.prod(g.shape)
        bavg = numpy.sum(b)/numpy.prod(b.shape)

        # define the rgb background color
        self.background_color = numpy.array([ravg, gavg, bavg]).astype(numpy.uint8)

        # create three channels the size of the image which are each the average color
        r = numpy.ones(r.shape) * ravg
        g = numpy.ones(g.shape) * gavg
        b = numpy.ones(b.shape) * bavg

        # create a 3d numpy array for the image data
        start = numpy.zeros([r.shape[0], r.shape[1], 3])
        start[:,:,0] = r
        start[:,:,1] = g
        start[:,:,2] = b

        return start


    def addShape(self, shape):
        """
        Adds a shape to the model's collection of shapes which are used. It is
        assumed these shapes were already applied to the current image.
        :param shape: The shape object to add
        """
        self.shapes.append(shape)


    def svgColor(self, color):
        """
        Computes an rgb color string in the format expected in SVG files
        :param color: The 1x(3 or 4) color array. Alpha is not used.
        :return: The rgb color string for an SVG file
        """
        return 'rgb(' + str(int(color[0])) + ',' + str(int(color[1])) + ',' + str(int(color[2])) + ')'


    def writeSVG(self, path):
        """
        Writes an svg of the shapes
        :param path: The path of the svg to write
        """

        # compute inverse scale so the SVG is near the original image size
        invScale = 1 / self.scale
        imgSize = numpy.shape(self.target[:,:,0])
        svg = svgwrite.Drawing(path, (int(imgSize[1])*invScale, int(imgSize[0])*invScale), debug=True)

        # background
        svg.add(svg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill=self.svgColor(self.background_color)))

        shapes = svg.add(svg.g(id='shapes'))
        for shape in self.shapes:

            # apply the inverse scale factor to the shape points
            polyPoints = shape.points * invScale

            # reverse x/y because SVG expects them in the other order
            temp = numpy.copy(polyPoints[:, 0])
            polyPoints[:, 0] = polyPoints[:, 1]
            polyPoints[:, 1] = temp

            polyPoints = numpy.ndarray.tolist((polyPoints).astype(numpy.int))

            # add the SVG polygon object
            polygon = svg.polygon(points=polyPoints, fill=self.svgColor(shape.color), opacity=shape.color[3])
            shapes.add(polygon)
        svg.save()

        print 'SVG saved to: ', path


    def replaceSubsection(self, replacement, bounds, sample=False):
        """
        Replaces the current image (working copy) with a rectangle of data
        which corresponds to a shape being applied
        :param replacement: A bounding rectangle for a shape
        :param bounds: The coordinates for the rectangle in the image
        :param sample: For debugging, applies this change to a copy of the target image
        :return: For debugging, the replacement applied to a copy of the target image
        """
        self.current[bounds[0]:bounds[1], bounds[2]:bounds[3], :] = replacement

        if sample:
            targetCopy = numpy.copy(self.target)
            targetCopy[bounds[0]:bounds[1], bounds[2]:bounds[3], :] = replacement
            return targetCopy


    def getImgBounds(self):
        """
        Gets the size of the image
        :return: The size of the image
        """
        return numpy.shape(self.target)[:2]


    def scoreShape(self, shape, alpha):
        """
        Scores a given shape according to how much the current (working) image looks
        like the target image. The color for the shape is chosen here, and the choice
        is the most optimal color for the region the shape covers.

        :param shape: The shape to score
        :param alpha: The alpha value to be used when calculating color
        :return score: The score after applying this shape
        :return color: The most optimal color for this shape
        :return replacement: A bounding rectangle containing the shape when applied to the current image
        :return bounds: The bounds (coordinates) of the bounding rectangle in the image
        """

        # get the shape's points
        vertices = shape.points

        # find min and max x/y points to get bounding rectangle
        maxx, maxy = numpy.max(vertices, 0)
        minx, miny = numpy.min(vertices, 0)

        # there is a tendency to create very thin shapes at higher shape counts
        # give a bad score if the shape is too thin
        int_vertices = numpy.ndarray.tolist(vertices.astype(numpy.int))
        for v in range(len(int_vertices)): #I don't know how to do this without a loop
            p1 = int_vertices[v]
            p2 = int_vertices[((v+1)%len(int_vertices))]
            p3 = int_vertices[((v+2)%len(int_vertices))]

            angle = math.degrees(abs(math.atan2(p3[0]-p1[0], p3[1]-p1[1]) -
                                     math.atan2(p2[0]-p1[0], p2[1]-p1[1])))

            # if > 180, we want the other part
            if angle > 180:
                angle = abs(angle-360)

            # all angles must be >= 4 degrees
            if angle < 4:
                return -1, None, None, None

        # calculate which pixels fall inside the shape
        x, y = numpy.mgrid[minx:maxx + 1, miny:maxy + 1]
        points = numpy.transpose(numpy.vstack([x.ravel(), y.ravel()]))
        inside = path.Path(vertices).contains_points(points)
        inside = numpy.reshape(inside, x.shape)

        # make 3d logical and integer representations of which points are inside/outside
        inside_3d = numpy.transpose(numpy.tile(inside, [3,1,1]), axes=[1, 2, 0])
        inside_int_bools = inside_3d.astype(numpy.int)
        outside_int_bools = numpy.logical_not(inside_3d).astype(numpy.int)
        inside_count = numpy.sum(inside_int_bools)

        # a shape with zero pixels inside is pointless
        if inside_count < 1:
            return -1, None, None, None

        # define the working regions of the current and target images
        # this is the bounding rectangle for the shape
        target_rectangle = self.target[minx:maxx + 1, miny:maxy + 1, :]
        target_shape = target_rectangle * inside_int_bools
        current_before = self.current[minx:maxx + 1, miny:maxy + 1, :] * inside_int_bools

        # compute average colors within the target and current images inside the shape
        target_color_sum = numpy.sum(numpy.sum(target_shape, axis=0), axis=0)
        target_avg_color = numpy.uint8(target_color_sum/float(inside_count/3))
        current_color_sum = numpy.sum(numpy.sum(numpy.floor(current_before), axis=0), axis=0)
        current_avg_color = numpy.uint8(current_color_sum/float(inside_count/3))

        # compute optimal color for the shape by solving for "color to add" in the rgba application function
        # this gives the color which would turn the current_avg_color into the target_avg_color if applied
        color = (numpy.int16(target_avg_color) - ((1 - alpha) * current_avg_color)) / alpha

        # the optimal color may be out of bounds (may not be possible to get to target color)
        # so, clip to [0, 255]
        color = numpy.clip(color,0,255).astype(numpy.uint8)

        # compute current_after (what this area would look like with this shape)
        current_after = numpy.int16(alpha * color + (1 - alpha) * current_before) * inside_int_bools

        # compute replacement rectangle (replacing this within the bounds of the current image applies the shape)
        replacement = current_after + (self.current[minx:maxx + 1, miny:maxy + 1, :] * outside_int_bools)
        replacement = numpy.uint8(replacement)
        bounds = [minx, maxx+1, miny, maxy+1]

        # temporarily apply the shape
        current_region = numpy.copy(self.current[minx:maxx + 1, miny:maxy + 1, :])
        self.replaceSubsection(replacement, bounds)

        # compute the difference between images
        target_after_diff = self.target - self.current

        # compute the score of the current image (same as score for shape)
        # this score is % similarity where 1 is exactly the same
        channel_area = numpy.prod(numpy.shape(self.target[:,:,0]))
        score = 1 - (numpy.sum(numpy.abs(target_after_diff)) / float(channel_area*3*255))

        # undo applying this shape because we don't know if it will be used yet
        self.replaceSubsection(current_region, bounds)

        return score, color, replacement, bounds