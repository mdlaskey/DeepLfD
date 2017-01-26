"""
Class for Registring a Primesense using a chessboard and 
the conversion to go from 2D robot pose (x,y) to 2D image pixel (x,y). 
Author: Michael Laskey

"""

import copy
import IPython
import logging
import numpy as np
import cv2
import scipy.spatial.distance as ssd
import scipy.optimize as opt
import pickle
from core import RigidTransform, PointCloud, NormalCloud, Point
from deep_lfd.rgbd import bincam_2D as b2
from numpy import linalg as LA

class RegPS():
    def __init__(self):
        
        
        #Load Parameters
        
        self.trans = RigidTransform.load('/home/autolab/Public/alan/calib/primesense_overhead/primesense_overhead_to_world.tf')
        if(self.trans == None):
            raise Exception('No Transformation Found, Need to Register')
 

  

    def pixel_to_robot(self,pose,intrs_frame):
        """
        Takes a point in pixel space and converts it to robot space

        Parameters
        ----------
        pixel: (3,) shape numpy array
            Pixel position in the image 

        Returns
        -------
        numpy array: 
            (2,) shape array that is the (x,y) pixel of the original camera
    
        """

        x_y = np.array([pose[0],pose[1]])
        x_y = Point(x_y,frame='primesense_overhead')
        depth = np.array(pose[2])
        robot_location_camera = intrs_frame.deproject_pixel(depth,x_y)

       
        T_world = self.trans*robot_location_camera

        return T_world



    def robot_to_pixel(self,cords,intrs):
        """
        Takes a point in robot space and converts it to pixel space

        Parameters
        ----------
        pixel: (3,) shape numpy array
            (x,y) Robot pose 

        Returns
        -------
        numpy array: 
            (2,) shape array that is the (x,y) pixel position

        """

        trans_inv = self.trans.inverse()

        T_world = trans_inv*cords

        return intrs.project(T_world)

  
   










    
    
