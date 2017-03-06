#from alan.rgbd.basic_imaging import draw_box
from alan.core.points import Point

import numpy as np

import IPython
import cv2

"""
Parameters:
    2D binary matrix
See for reference:
    http://docs.opencv.org/trunk/d1/d32/tutorial_py_contour_properties.html
    http://docs.opencv.org/2.4/modules/imgproc/doc/structural_analysis_and_shape_descriptors.html#boundingrect
Returns:
    array of two Points that correspond to low and high vertices of foreground bounding box
"""
def get_pixel_bounds(matrix):
    pixel_points = cv2.findNonZero(matrix)
    x, y, w, h = cv2.boundingRect(pixel_points)

    v_low = Point(np.array([x, y]), "pixel_2D")
    v_high = Point(np.array([x + w, y + h]), "pixel_2D")

    return [v_low, v_high]


def re_binarize(matrix):
    w,h = matrix.shape

    for i in range(w):
        for j in range(h):
            if(matrix[i,j]>125):
                matrix[i,j] = 255.0
            else:
                matrix[i,j] = 0.0 
    return matrix

"""
Parameters:
    2D binary matrix
Returns:
    the input matrix with one bounding box drawn that encompasses all objects
"""
def draw_bounds(matrix):
    bounds = get_pixel_bounds(matrix)
    return draw_box(matrix, bounds)

def rand_sign():
    num = np.random.randint(2)

    if(num == 0):
        return -1
    else:
        return 1