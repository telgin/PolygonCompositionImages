#Polygon Composition Image Generator
Polygon composition images are images which approximate another image with a series of translucent polygons. Using fewer polygons results in an artistic/abstract effect. This was a term project which I made for my class in computer vision. For the moment, the only shapes implemented are triangles and squares, but the code is written in a way to accept any polygon so you could theoretically implement another shape using the existing shapes as a guide. It's also fun to experiment with placing constraints on existing shapes. For instance, the squares cannot be rotated which leads to an interesting effect.

##Examples:
Bee/Flower made from 100 triangles:

![image](https://github.com/telgin/PolygonCompositionImages/blob/master/examples/bee_100.png?raw=true "Bee 100 Triangles")

Bee/Flower made from 1000 triangles:

![image](https://github.com/telgin/PolygonCompositionImages/blob/master/examples/bee_1000.png?raw=true "Bee 1000 Triangles")

Original Image [OC]:

![image](https://github.com/telgin/PolygonCompositionImages/blob/master/examples/bee.png?raw=true "Original")

Frog made from 1000 triangles:

![image](https://github.com/telgin/PolygonCompositionImages/blob/master/examples/frog_1000.png?raw=true "Frog 1000 Triangles")

Checkerboard made from 200 triangles:

![image](https://github.com/telgin/PolygonCompositionImages/blob/master/examples/checkerboard_200.png?raw=true "Checkerboard 200 Triangles")

Frog eye made from 1000 squares:

![image](https://github.com/telgin/PolygonCompositionImages/blob/master/examples/frog_eye_squares_1000.png?raw=true "Frog Eye 1000 Squares")


##Dependencies:
```text
Python 2.7
--> Numpy ("pip install numpy")
--> Matplotlib ("pip install matplotlib")
--> Python Image Library (PIL) ("pip install Pillow")
--> SVGWrite ("pip install svgwrite")
--> ArgParse ("pip install argparse")
```

##Usage:
```text
polygon_images.py [-h] target_image shape N [N ...]

Polygon Composition Image Generator

positional arguments:
  target_image  Path to target image location.
  shape         Type of shape: square, triangle
  N             Saves SVG files at these numbers of polygons.

optional arguments:
  -h, --help    show this help message and exit
```

###Usage Example:
```text
python polygon_images.py ~/Pictures/fireworks.png triangle 10 20 100 500 1000

-- The program will run until 1000 triangles, saving SVG files in your current directory for
each of the numbers specified. Because you are wanting to save a number below 100, triangles
1-20 will be calculated using bestof=10 and using parallel processing. This produces higher
quality for lower levels at the expense of time. Triangles 21-1000 will be calculated using
bestof=1 which runs faster.
```

##PNG Conversion:
```text
At the moment, this is only outputing SVG's. If you need a PNG for some reason and are running
Linux, I recommended Inkscape.

On ubuntu:
sudo add-apt-repository ppa:inkscape.dev/stable
sudo apt-get update
sudo apt-get install inkscape

Ex:
\#do specific SVG
inkscape -z -e output.png input.svg

\#do all SVGs
find -type f -name '*.svg' -exec inkscape -z -e {}.png {} \;
```
