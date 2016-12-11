import numpy
from triangle import Triangle
import multiprocessing
from functools import partial

"""
Author: Thomas Elgin (https://github.com/telgin)
"""

def bestMutation(shape, model, cycles=50, startHeat=100, heatDiv=1.01, alpha=.5):
    """
    Mutates a shape for a given number of cycles and returns the best scoring change
    :param shape: The shape to mutate
    :param model: The model object
    :param cycles: The number of cycles (attempts at mutation)
    :param startHeat: The initial maximum random number which a point can change by
    :param heatDiv: The amount to divide the heat by every time the shape mutates into a better position
    :param alpha: The alpha value to use when calculating color
    :return: An array representing the best change. [score, color, replacement, bounds]
    """

    bestShape = shape
    score, color, replacement, bounds = model.scoreShape(bestShape, alpha)
    bestChange = [score, color, replacement, bounds]

    curHeat = startHeat

    for j in range(cycles):
        bestShape.mutate(heat=curHeat)

        score, color, replacement, bounds = model.scoreShape(bestShape, alpha)
        change = [score, color, replacement, bounds]

        if score > bestChange[0]:
            bestChange = change
            curHeat = int(curHeat / heatDiv)
            curHeat = max(curHeat, 10)
        else:
            bestShape.undoMutate()


    return bestChange


def bestShapeOfX(model, shapetype=Triangle, bestof=10, cycles=100, startHeat=100, heatDiv=1.01, alpha=.5):
    """
    Finds the best shape of a certain number of shapes. This amounts to a number of calls
    to bestMutation with different starting shapes. The best shape/change of all calls is returned.
    :param model: The model object
    :param shapetype: The type of shape (class)
    :param bestof: The number of attempts at getting the best mutation with different shapes
    :param cycles: The number of cycles (attempts at mutation)
    :param startHeat: The initial maximum random number which a point can change by
    :param heatDiv: The amount to divide the heat by every time the shape mutates into a better position
    :param alpha: The alpha value to use when calculating color
    :return: The best shape and the best change
    """

    bestChange = [-1, None, None, None]
    bestShape = None
    scores = []
    for i in range(bestof):
        shape = shapetype(model.getImgBounds())
        change = bestMutation(shape, model, cycles, startHeat, heatDiv, alpha)

        if change[0] > bestChange[0]:
            bestChange = change
            bestShape = shape

        scores.append(change[0])

    return bestShape, bestChange


def par_inner(model, shapetype, cycles, startHeat, heatDiv, alpha, i):
    """
    Function for use with parallel processing. Used to create a partial function which
    wraps the bestMutation function.
    :param model: The model object
    :param shapetype: The type of shape (class)
    :param cycles: The number of cycles (attempts at mutation)
    :param startHeat: The initial maximum random number which a point can change by
    :param heatDiv: The amount to divide the heat by every time the shape mutates into a better position
    :param alpha: The alpha value to use when calculating color
    :param i: Unused (needed for parallel call)
    :return: The best shape and the best change
    """

    shape = shapetype(model.getImgBounds())
    return shape, bestMutation(shape, model, cycles, startHeat, heatDiv, alpha)


def bestShapeOfXPar(model, shapetype=Triangle, bestof=10, cycles=100, startHeat=100, heatDiv=1.01, alpha=.5):
    """
    Same function as bestShapeOfX but runs in parallel. The parallel advantage happens
    only with bestof > 1
    :param model: The model object
    :param shapetype: The type of shape (class)
    :param bestof: The number of attempts at getting the best mutation with different shapes
    :param cycles: The number of cycles (attempts at mutation)
    :param startHeat: The initial maximum random number which a point can change by
    :param heatDiv: The amount to divide the heat by every time the shape mutates into a better position
    :param alpha: The alpha value to use when calculating color
    :return: The best shape and the best change
    """

    pool = multiprocessing.Pool(4)
    partial_func = partial(par_inner, model, shapetype, cycles, startHeat, heatDiv, alpha)
    shapes, changes = zip(*pool.map_async(partial_func, range(0, bestof)).get(9999999)) # timeout to avoid library bug
    scores = [change[0] for change in changes]

    bestScoreIdx = numpy.argmax(scores)

    return shapes[bestScoreIdx], changes[bestScoreIdx]


def fitShapes(model, shapes=[1], shapetype=Triangle, cycles=100, startHeat=100, heatDiv=1.01, alpha=.5, savename='polygons'):
    """
    Uses the model to fit shapes to an image. SVGs are saved at the numbers of shapes specified, thus
    the total number of shapes fit will be the max value in the shapes list.
    :param model: The model object
    :param shapes: A list of the numbers of shapes to save at
    :param shapetype: The type of shape (class)
    :param cycles: The number of cycles (attempts at mutation) per shape
    :param startHeat: The initial maximum random number which a point can change by
    :param heatDiv: The amount to divide the heat by every time the shape mutates into a better position
    :param alpha: The alpha value to use when calculating color
    :param savename: The prefix of the SVG file name
    """

    # From graphing the effect of the bestof param, it was found that
    # bestof=1 is significantly faster but produces noticeably poorer
    # results at lower shape counts. To optimize the processing, there
    # needs to be a cutoff where it's safe to use bestof=1. This boundary
    # is only used if the user is saving an image below the boundary,
    # otherwise all processing is done at bestof=1
    QUALITY_OPTIMIZATION_BOUNDARY = 100

    quality_savepoints = [n for n in shapes if n < QUALITY_OPTIMIZATION_BOUNDARY]
    max_quality_savepoint = None
    if len(quality_savepoints) > 0:
        max_quality_savepoint = max(quality_savepoints)

    for i in range(max(shapes)):

        # optimization step:
        if max_quality_savepoint is not None and i <= max_quality_savepoint:
            bestof = 10
        else:
            bestof = 1

        # optimization step:
        # use parallel processing if bestof > 1
        if bestof > 1:
            shape, change = bestShapeOfXPar(model, shapetype, bestof, cycles, startHeat, heatDiv, alpha)
        else:
            shape, change = bestShapeOfX(model, shapetype, bestof, cycles, startHeat, heatDiv, alpha)

        # Repeat until a shape is found. This doesn't usually happen,
        while change[0] < 0: # if best score is invalid

            print 'fitting polygon:', i+1, '-- invalid fit, trying again...'

            # optimization step:
            # use parallel processing if bestof > 1
            if bestof > 1:
                shape, change = bestShapeOfXPar(model, shapetype, bestof, cycles, startHeat, heatDiv, alpha)
            else:
                shape, change = bestShapeOfX(model, shapetype, bestof, cycles, startHeat, heatDiv, alpha)

        # show status
        print 'fitting polygon:', i+1, '-- image similarity:', change[0]*100, '%'

        # add the change to the model
        model.replaceSubsection(change[2], change[3])

        # set the shape's color
        color = numpy.ndarray.tolist(change[1])
        color.append(alpha)
        shape.color = color

        # add the shape to the model's list of used shapes
        # (these will be used to generate the SVG later)
        model.addShape(shape)

        # write an SVG file if the number of shapes is right
        if i+1 in shapes:
            num = str(i+1)
            while len(num) < 5:
                num = '0' + num

            model.writeSVG(savename + '_' + num + '.svg')
