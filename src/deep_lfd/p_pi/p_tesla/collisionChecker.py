'''
Collison Checking class for robot singulation policy

Author: Michael Laskey

'''

import math
import IPython
import numpy as np
import cv2

from alan.rgbd.basic_imaging import sin, cos
from alan.rgbd.conversions import gripperLenPixels


def findValidPlacement(bgMat, robotState, searchDim = 0):
    """
    Find the valid placement of the pose (i.e. no collsions)

    Parameters 
    ----------
        bgMat : (WxHx1) shape numpy array
        A binary image of the workspace

        robotState : (3,) shape numpy array
        [x, y, theta] x and y as pixel indices of paddle in image coordinates
        theta as degree rotation of paddle where positive x axis is 0 degrees
        and increases counterclockwise in standard frame/clockwise in image frame

        searchDim : int
        0 or 1- whether to search in x or y (affects output)
    
    Returns 
    -------
        (3,) shape numpy array
            [x, y, theta] as first valid placement found by searching 
            left/up from robotState theta unchanged from input; 
            only one of x, y changed

        (WxHx1) shape numpy array
            binary image of the workspace with the new pose marked on it

        copy of binary image with checked paddle positions marked
    """
    dim = 3
    if len(robotState) != 3:
        raise Exception("Robot state for placement must be 3-dimensional: x, y, theta.")
    if searchDim != 0 and searchDim != 1:
        raise Exception("Placement search can only occur in dimension 0 or 1 (x or y).")

    
    foundPos = False
    checkedAll = False
    debug_img = np.copy(bgMat)
    while not (foundPos or checkedAll):
        didCollide, debug_img = doesCollide(bgMat, robotState,debug_img)
        if didCollide:
            robotState[searchDim] -= 1;
            if robotState[searchDim] < 0:
                checkedAll = True
                robotState[searchDim] = -14
                break;
        else:
            foundPos = True
    robotState[searchDim] -= -2
    return robotState, debug_img


def doesCollide(bgMat, robotState,debug_img):
    """
    Checks if the robot's paddle is in collsion
    
    Parameters
    ----------
     bgMat : (WxHx1) shape numpy array
        A binary image of the workspace

    robotState : (3,) shape numpy array
        [x, y, theta] x and y as pixel indices of paddle in image coordinates
        theta as degree rotation of paddle where positive x axis is 0 degrees
        and increases counterclockwise in standard frame/clockwise in image frame

    Returns 
    -------
        bool
            True if the robot is in collsion. False otherwise

        (WxHx1) shape numpy array
            binary image of the workspace with the new pose marked on it
"""
    if len(robotState) != 3:
        raise Exception("Robot state for placement must be 3-dimensional: x, y, theta.")

    origPos = robotState[0:2]

  


    collides = False

    for d in range(int(gripperLenPixels())/2):
        trig = [cos, sin]
        currPos = np.copy(origPos)
        print currPos
        currPos[1] += d

        currPix = bgMat[currPos[1],currPos[0],0]
        debug_img[currPos[1],currPos[0],0] = 128

        if currPix > 128:
            collides = True

    for d in range(int(gripperLenPixels())/2):
        trig = [cos, sin]
        currPos = np.copy(origPos)
        currPos[1] -= d

        currPix = bgMat[currPos[1],currPos[0],0]
        debug_img[currPos[1],currPos[0],0] = 128

        if currPix > 128:
            collides = True

   

    return collides, debug_img
