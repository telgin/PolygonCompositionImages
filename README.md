Polygon Composition Image Generator

Dependencies:
Python 2.7
--> Numpy ("pip install numpy")
--> Matplotlib ("pip install matplotlib")
--> Python Image Library (PIL) ("pip install Pillow")
--> SVGWrite ("pip install svgwrite")
--> ArgParse ("pip install argparse")


Usage:
polygon_images.py [-h] target_image shape N [N ...]

Polygon Composition Image Generator

positional arguments:
  target_image  Path to target image location.
  shape         Type of shape: square, triangle
  N             Saves SVG files at these numbers of polygons.

optional arguments:
  -h, --help    show this help message and exit


Usage Example:
python polygon_images.py ~/Pictures/fireworks.png triangle 10 20 100 500 1000

-- The program will run until 1000 triangles, saving SVG files in your current directory for
each of the numbers specified. Because you are wanting to save a number below 100, triangles
1-20 will be calculated using bestof=10 and using parallel processing. This produces higher
quality for lower levels at the expense of time. Triangles 21-1000 will be calculated using
bestof=1 which runs faster.


PNG Conversion:
At the moment, this is only outputing SVG's. If you need a PNG for some reason and are running
Linux, you can use Inkscape.

On ubuntu:
sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt-get update
sudo apt-get install inkscape

Ex:
#do specific SVG
inkscape -z -e output.png input.svg

#do all SVGs
find -type f -name '*.svg' -exec inkscape -z -e {}.png {} \;