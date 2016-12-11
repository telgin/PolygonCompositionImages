from PIL import Image
from model import Model
from shapefitting import *
from square import Square
from triangle import Triangle
import os
import argparse
import sys

"""
Author: Thomas Elgin (https://github.com/telgin)
"""

# define shapetypes
shapetypes = {}
shapetypes['square'] = Square
shapetypes['triangle'] = Triangle

def parseArgs():
    """
    Parse command line arguments
    :return: The args object
    """

    parser = argparse.ArgumentParser(description='Polygon Composition Image Generator')
    parser.add_argument('target_image', help='Path to target image location.')
    parser.add_argument('shape', type=str, help='Type of shape: ' + ', '.join(shapetypes.keys()))
    parser.add_argument('polygons', metavar='N', type=int, nargs='+', help='Saves SVG files at these numbers of polygons.')

    args = parser.parse_args(sys.argv[1:])

    if not os.path.exists(args.target_image) :
        print 'The specificied target image file does not exist: ' + args.target_image
        exit()
    elif '.' not in args.target_image:
        print 'Invalid target image name: ' + args.target_image
        exit()
    args.filename = os.path.basename(args.target_image).split('.')[0]

    args.shape = args.shape.lower()
    if args.shape not in shapetypes:
        print 'Invalid shape type: ' + args.shape
        print 'Choose one of the following: ' + ', '.join(shapetypes.keys())
        exit()


    return args

def main():
    """
    Entry Point
    """

    args = parseArgs()
    img = Image.open(args.target_image)

    # remove alpha component if it exists
    if len(img.split()) == 4:
        noa = Image.new("RGB", img.size, (255, 255, 255))
        noa.paste(img, mask=img.split()[3])
        img = noa

    # calculate scaling factor:
    # scaling the image down significantly reduces computation time and while I would normally
    # be against this sort of thing, for this application you are not generally looking to
    # output an image which includes the very fine detail anyways.
    # ideally, largest image dimension is 315 (sort of tested, sort of arbitrary)
    IDEAL_SIDE_SIZE = 315

    max_side = max(img.size)
    if max_side <= IDEAL_SIDE_SIZE:
        scale_factor = 1
    else:
        scale_factor = IDEAL_SIDE_SIZE / float(max_side)

    # create model
    model = Model(img, scale=scale_factor)

    # fit polygons
    fitShapes(model, shapes=args.polygons, shapetype=shapetypes[args.shape], cycles=100, startHeat=100,
        heatDiv=1.1, alpha=.5, savename=args.filename)


main()

