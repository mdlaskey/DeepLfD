import math
import IPython
import numpy as np
import cv2

from alan.rgbd.basic_imaging import sin, cos
from alan.rgbd.conversions import gripperLenPixels

"""
parameters:
    bgMat- matrix with 0 for each background pixel
    robotState = [x, y, theta]
        x and y as pixel indices of paddle
        theta as degree rotation of paddle where positive x axis is 0 degrees
        and increases counterclockwise in standard frame/clockwise in image frame
    search_dim = 0 to search in x, 1 to search in y
    search_dir = 0 to search left/up, 1 to search right/down
returns:
    [x, y, theta] as first valid placement found by searching left/up from robotState
        theta unchanged from input; only one of x, y changed
    copy of binary image with checked paddle positions marked
"""
def find_valid_placement(bg_mat, robot_state, search_dim = 1, search_dir = 1):
    dim = 3
    if len(robot_state) != 3:
        raise Exception("Robot state for placement must be 3-dimensional: x, y, theta.")
    if search_dim != 0 and search_dim != 1:
        raise Exception("Placement search can only occur in dimension 0 or 1 (x or y).")
    if search_dir != 0 and search_dir != 1:
        raise Exception("Placement search can only occur in direction 0 or 1 (positive or negative).")

    #copy to preserve non-marked original
    bg_copy = np.copy(bg_mat)

    if (search_dir == 0):
        search_dir = -1
    

    found_pos = False
    checked_all = False

    while not (found_pos or checked_all):
        did_collide, bg_copy = does_collide(bg_copy, robot_state)
        if did_collide:
            if robot_state[search_dim] == 0:
                checked_all = True
            else:
                robot_state[search_dim] = robot_state[search_dim] + search_dir;
        else:
            found_pos = True

    return robot_state, bg_copy

"""
parameters:
    bgMat- matrix with 0 for each background pixel
    robotState = [x, y, theta]
        x and y as pixel indices of paddle
        theta as degree rotation of paddle where positive x axis is 0 degrees
        and increases counterclockwise in standard frame/clockwise in image frame
returns:
    True if any pixels in the specified region belong to object
    binary image with gray pixels in checked gripper position
"""
def does_collide(bg_mat, robot_state):
    if len(robot_state) != 3:
        raise Exception("Robot state for placement must be 3-dimensional: x, y, theta.")

    orig_pos = robot_state[0:2]

    collides = False
    for d in range(int(gripperLenPixels())):
        trig = [cos, sin]
        curr_pos = [int(orig_pos[i] + d * trig[i](robot_state[2])) for i in range(len(orig_pos))]

        curr_pix = bg_mat[curr_pos[1]][curr_pos[0]]
        bg_mat[curr_pos[1]][curr_pos[0]] = 128

        if curr_pix > 128:
            collides = True

    return collides, bg_mat