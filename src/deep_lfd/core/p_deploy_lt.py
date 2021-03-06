'''
Policy wrapper class 

Author: Michael Laskey
'''
import sys
import tty, termios
from alan.rgbd.bincam_2D import BinaryCamera 
from alan.rgbd.registration_wc import RegWC
from alan.control import YuMiRobot, YuMiState, YuMiControlException
from alan.debug.ar_overlay import AR_Debug
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np




class  Policy():

    def __init__(self, yumi,com,cam,debug = False):
        '''
        Initialization class for a Policy

        Parameters
        ----------
        yumi : An instianted yumi robot 
        com : The common class for the robot
        cam : An open bincam class

        debug : bool 

            A bool to indicate whether or not to display a training set point for 
            debuging. 

        '''
        self.yumi = yumi
        self.com = com

        self.bc = cam
        self.cp = self.com.get_cp(yumi)
        if(debug):
            debug_ar = AR_Debug(self.bc,self.com)
            debug_ar.check_test_error()



    def rollout(self):
        '''
        Evaluates the current policy and then executes the motion 
        specified in the the common class


        '''
        
        time.sleep(.5)
       
        for i in range(5):
            frame = self.bc.read_binary_frame()

        frame = self.bc.read_binary_frame(options = self.com.Options)

        pos,rot = self.com.eval_policy(frame)

        #Get pose 
        posit = np.zeros(3)
        posit[0] = pos[0]
        posit[1] = pos[1]
        #98.1641694101 68.9216331179 -179.993896484
        #107.07569885   98.12541199 -169.56536865
        posit[2] = self.cp.position[2] 

        posit = posit - self.cp.position 
      
        self.com.move_to_pose(self.yumi,posit,rot)

        try:
            self.com.execute_motion(self.yumi)  
        except YuMiControlException, e:
            print str(e)
            self.yumi.set_v(1500)
            self.com.error_handler(self.yumi)
       



if __name__ == "__main__":
   
    
    yumi = YuMiRobot()
    options = Options()
    com = COM(train=False)
    bincam = BinaryCamera(options)
    yumi.set_z('fine')
    
    
    bincam.open(threshTolerance= options.THRESH_TOLERANCE)

    frame = bincam.display_frame()

    yumi.set_v(1500)
    
    debug_overlay(bincam,options.binaries_dir+'rollout0_frame_0.jpg')
    
    
    pi = Policy(yumi,com,bincam=bincam)

    while True:
        pi.rollout()

    print "Done."
