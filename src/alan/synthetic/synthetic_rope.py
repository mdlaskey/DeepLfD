import numpy as np
import cv2
from scipy import interpolate
from random import randint
import IPython
from alan.rgbd.basic_imaging import cos,sin
from alan.synthetic.synthetic_util import rand_sign
from alan.core.points import Point

"""
generates rope using non-holonomic car model dynamics (moves with turn radius)
generates labels at ends of rope
parameters:
    h, w of image matrix
    l, w of rope
returns:
    image matrix with rope drawn
    [left label, right label]
"""
def get_rope_car(h = 420, w = 420, rope_l_pixels = 800 , rope_w_pixels = 8, pix_per_step = 10, steps_per_curve = 10, lo_turn_delta = 5, hi_turn_delta = 10):

        #randomize start
        init_pos = np.array([randint(0, w - 1), randint(0, h - 1), randint(0, 360)])
        all_positions = np.array([init_pos])

        #dependent parameter (use float division)
        num_curves = int(rope_l_pixels/(steps_per_curve * pix_per_step * 1.0))

        #point generation
        for c in range(num_curves):
            turn_delta = rand_sign() * randint(lo_turn_delta, hi_turn_delta)

            for s in range(steps_per_curve):
                curr_pos = all_positions[-1]
                delta_pos = np.array([pix_per_step * cos(curr_pos[2]), pix_per_step * sin(curr_pos[2]), turn_delta])

                all_positions = np.append(all_positions, [curr_pos + delta_pos], axis = 0)

        #center the points (avoid leaving image bounds)
        mid_x_points = (min(all_positions[:,0]) + max(all_positions[:,0]))/2.0
        mid_y_points = (min(all_positions[:,1]) + max(all_positions[:,1]))/2.0

        for pos in all_positions:
            pos[0] -= (mid_x_points - w/2.0)
            pos[1] -= (mid_y_points - h/2.0)

        #draw rope
        image = np.zeros((h, w))
        prev_pos = all_positions[0]
        for curr_pos in all_positions[1:]:
            cv2.line(image, (int(prev_pos[0]), int(prev_pos[1])), (int(curr_pos[0]), int(curr_pos[1])), 255, rope_w_pixels)
            prev_pos = curr_pos

        #get endpoint labels, sorted by x
        labels = [all_positions[0], all_positions[-1]]

        if labels[0][0] > labels[1][0]:
            labels = [labels[1], labels[0]]

        #labels = [[l[0], l[1], l[2] + 90] for l in labels]
        #Ignoring Rotation for Now
        labels = [[l[0], l[1], 0] for l in labels]


        #rejection sampling
        for num_label in range(2):
            c_label = labels[num_label]
            #case 1- endpoints not in image
            if check_bounds(c_label, [w, h]) == -1:
                return image, labels, -1
            #case 2- endpoint on top of other rope segment
            if check_overlap(c_label, [w, h], image, rope_w_pixels) == -1:
                return image, labels, -1

        return image, labels, 1

def check_bounds(label, bounds):
    bound_tolerance = 5
    for dim in range(2):
        if label[dim] < bound_tolerance or label[dim] > (bounds[dim] - 1 - bound_tolerance):
            return -1
    return 0

def check_overlap(label, bounds, image, rope_w_pixels):
    lb = []
    ub = []
    for dim in range(2):
        lb.append(int(max(0, label[dim] - rope_w_pixels)))
        ub.append(int(min(bounds[dim] - 1, label[dim] + rope_w_pixels)))

    pixel_sum = 0
    for x in range(lb[0], ub[0]):
        for y in range(lb[1], ub[1]):
            pixel_sum += (image[y][x]/255.0)

    #if more than 60% of adjacent (2 * rope_w x 2 * rope_w) pixels are white, endpoint is probably lying on rope
    expected_sum =  0.6 * (ub[1] - lb[1]) * (ub[0] - lb[0])
    if pixel_sum > expected_sum:
        return -1
    return 0
