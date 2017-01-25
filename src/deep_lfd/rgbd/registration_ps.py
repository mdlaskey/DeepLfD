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
 

        
    def get_image_bounds(self):
        """
        Get the robot bounds of the image specifed by an option file

        Returns: 
        numpy array: 
            (2,) shape array that is the (x,y) lower bound in robot pose

        numpy array
            (2,) shape array that is the (x,y) upper bound in robot pose

        """

        c1 = np.array([0,0])
        c2 = np.array([self.width,self.height])

        c1 = self.pixel_to_robot(c1)
        c2 = self.pixel_to_robot(c2)


        return c1,c2

    def offset_camera(self,pixel):
        """
        Accounts for the orign shift when using the options file

        Parameters
        ----------
        pixel: (2,) shape numpy array

        Returns
        -------
        numpy array: 
            (2,) shape array that is the (x,y) pixel when shifted

        """
        pixel[0] = pixel[0]-self.p_x_off
        pixel[1] = pixel[1]-self.p_y_off

        return pixel


      
    def offset_cam_back(self,pixel):
        """
        Goes from shifted camera origin back to original camera orign

        Parameters
        ----------
        pixel: (2,) shape numpy array

        Returns
        -------
        numpy array: 
            (2,) shape array that is the (x,y) pixel of the original camera

        """
        pixel[0] = pixel[0]+self.p_x_off
        pixel[1] = pixel[1]+self.p_y_off

        return pixel



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



    def chessboard_to_robot(self,cords):
        """
        Translates a point from cheesboard frame to robot

        Parameters
        ----------
        pixel: (2,) shape numpy array
            Position in the cheesboard fraem

        Returns
        -------
        numpy array: 
            (2,) shape array that is the (x,y) pose in robot frame

        """
        #Translate to Robot Frame
        #+X in Chessboard is +X in Chessboard
        #+X in Robot is -Y in Chessboard
        c_r = np.zeros(2)
        c_r[0] = -cords[1]+self.x_off
        c_r[1] = cords[0] + self.y_off

        return c_r

    def robot_to_chessboard(self,cords):
        """
        Translates a point from robot frame to chessboard

        Parameters
        ----------
        pixel: (2,) shape numpy array
            (x,y) pose in robot frame

        Returns
        -------
        numpy array: 
            (2,) shape array that is position in the cheesboard fraem

        """
        #Translate to Chessboard Frame
        #+Y in Robot is +X in Chessboard
        #+X in Robot is -Y in Chessboard
        temp = cords[0]

        cords[0] = cords[1] - self.y_off
        cords[1] = -(temp - self.x_off)
        c_z = np.zeros(4)
        c_z[0:2] = cords
        c_z[3] = 1.0
        return c_z

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

  
    def register_chessboard(self):
        """
        Compute the transformation between robot pose and camera pose using chessboard registration 
        techniques

        Returns
        -------
        numpy array: 
            (3,4) shape array that is the computed transformation

        """

        p_mm = self.get_corners_mm()
        c_mm = self.find_chessboard()
     
        
        dist_coef = np.zeros(4)

        ret,r_vec,t_vec = cv2.solvePnP(p_mm.T,c_mm.T,self.C,dist_coef)


        #IPython.embed()

        r_mat,j = cv2.Rodrigues(r_vec)
       
        trans = np.zeros([3,4])
    
        trans[0:3,0:3] = r_mat
        trans[:,3] = t_vec[:,0]

        self.trans = trans
        return trans

    def get_corners_mm(self):
        """
        Computes each mm position of a cheeseboard given an origin that is the center of 
        the chessboard

        Returns
        -------
        numpy array: 
            (3,54) shape array that is each corner in the chessboard

        """
        top_right = np.zeros(2)
        points = np.zeros([3,54],dtype=np.float32)

        #TOP RIGHT CORNER 
        top_right[0] = int(self.Column/2)*self.W
        top_right[1] = self.H*0.5+self.H*int(self.Row/2-1)
        idx = 0
        for i in range(self.Column):
            for j in range(self.Row):
                point = np.copy(top_right)
                point[0] = point[0] - i*self.W
                point[1] = point[1] - j*self.H
                points[0:2,idx] = point
                idx += 1
                

        return points

    





    def find_chessboard(self,debug=False):
        """
        Finds the cheeseboard in the image and recovers each corner

        Parameters
        ----------
        debug: Boolean
            If True, shows image with cheeseboard corners overlayed (Defaul False)

        Returns
        -------
        numpy array: 
            (2,54) shape array that is each corner in the chessboard

        """
      

        ic = np.array([self.Row,self.Column])
        img = self.bc.read_raw()
        ret,ic = cv2.findChessboardCorners(img,(6,9))


        ic_np = np.zeros([2,54])

        for i in range(self.Column*self.Row):
            ic_np[:,i] = ic[i][0,:]

        if(debug):
            for i in range(len(ic)):
                p = ic[i]
                img[int(p[0][1]),int(p[0][0]),2] = 255
            
            cv2.imshow('debug',img)
            cv2.waitKey(30)
            IPython.embed()

        return ic_np

    def robot_to_pixel_scale(self,scale):
        """
        Not Supported
        """
        base = np.zeros(2)
        measures = np.array([0,scale])

        base_p = self.robot_to_pixel(base)
        m_p = self.robot_to_pixel(measures)

        return LA.norm(m_p-base_p)


if __name__ == "__main__":

    """
    Run to register camera make sure cheesboard can be seen in image

    """

    reg = RegWC(calibrate=True)
    trans = reg.register_chessboard()
 
  
    c_m = reg.find_chessboard()
    p_m = reg.get_corners_mm()
    top_right = p_m[:,0]

    print "Point A in Pixel Space",reg.chessboard_to_robot(p_m[:,0])

    points = reg.pixel_to_robot(c_m[:,0])

    print "Point A in From Projection", points
    

    print "Two Numbers Should be Near Equal for Correction Registration"

    #Save Registration To File
    trans = reg.trans
    pickle.dump(trans,open('data/registration/registration.pckl','wb'))

    print "Registration file saved"

    IPython.embed()






    
    
