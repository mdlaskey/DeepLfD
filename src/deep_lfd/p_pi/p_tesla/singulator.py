''''
Class to deploy the sinuglation policy for a YuMi YuMi
The policy is represented as a neural network controller, that takes
in an image and outputs a push motion. 

Author: Michael Laskey


'''
import sys
import tty, termios
from alan.control import YuMiRobot, YuMiState, YuMiControlException
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np

from deep_lfd.rgbd.bincam_2D import BinaryCamera 
from deep_lfd.rgbd.registration_wc import RegWC
from deep_lfd.core.p_deploy_lt import Policy 

from deep_lfd.p_pi.p_tesla.options import Tesla_Options as Options
from deep_lfd.p_pi.p_tesla.com import Tesla_COM as COM



class Singulator():

    def __init__(self,yumi):
        '''
        Initialization class for Singulator

        Paramters
        ---------
        yumi : YuMiRobot
            an initialized yumi robot class 

        '''
        self.yumi = yumi
        self.options = Options()
        self.com = COM()
        self.bc = BinaryCamera(self.options)
        yumi.set_z('fine')
        self.bc.open(threshTolerance= self.options.THRESH_TOLERANCE)
        self.pi = Policy(yumi,self.com, self.bc)



    def rollout(self,target_pose=None):
        '''
        function call to roll out a trained policy
        allows for a goal position to be specified 

        Parameters
        ----------
        target_pose : (2,) shape numpy array 

        Target (x,y) position to push to. Specified in robot coordinate frame
        (Not supported yet)

        '''

        self.com.target_pose = target_pose
        self.pi.rollout()
        


if __name__ == "__main__":
   
    
    yumi = YuMiRobot()
    singulator = Singulator(yumi)


    while (1):
        frame = singulator.bc.read_binary_frame()
        out = frame#+o
        cv2.imshow("camera", out)
        print("reading")
        a = cv2.waitKey(30)
        if a == 1048603:
            cv2.destroyWindow("camera")
            break
        time.sleep(.005)        
    

    while True: 
        singulator.rollout()


