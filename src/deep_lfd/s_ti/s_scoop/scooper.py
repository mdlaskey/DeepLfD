''''
Class to deploy the sinuglation policy for a YuMi YuMi
The policy is represented as a neural network controller, that takes
in an image and outputs a push motion. 

Author: Michael Laskey


'''
import sys
import tty, termios
from yumipy import YuMiRobot, YuMiState, YuMiControlException
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np

from deep_lfd.rgbd.bincam_2D import BinaryCamera 
from deep_lfd.rgbd.registration_wc import RegWC
#from deep_lfd.core.p_deploy_lt import Policy 

from deep_lfd.s_ti.s_scoop.options import Scoop_Options as Options
from deep_lfd.s_ti.s_scoop.com import get_state, rescale

from deep_lfd.tensor.nets.net_scooping import NetScooping as Net 



class Scooper():

    def __init__(self,yumi):
        '''
        Initialization class for Singulator

        Paramters
        ---------
        yumi : YuMiRobot
            an initialized yumi robot class 

        '''
        if yumi:
            self.yumi = yumi
            yumi.set_z('fine')

        self.options = Options()
        self.bc = BinaryCamera(self.options)

        self.net = Net()
        self.sess = self.net.load(self.options.policies_dir+'scoop_net_03-13-2017_10h27m15s.ckpt')
        
        self.bc.open(threshTolerance=self.options.THRESH_TOLERANCE)
       
        self.T = 10000

    def eval_policy(self,state):
        # cv2.imshow('debugi',state)
        # cv2.waitKey(30)
        outval = self.net.output(self.sess, state,channels=3)
    
        return rescale(outval)

    def move_to_pose(self,p_l,p_r):
        # y_l = p_l[0]
        # y_r = p_r[0]
        
        l = np.array([-1.0*p_l[0],p_l[1],0.0])
        r = np.array([p_r[0],-1.0*p_r[1],0.0])
        print "LEFT POSE ",p_l
        print "RIGHT POSE ",p_r

        print "DELTA LEFT POSE ",l
        print "DELTA RIGHT POSE ",r
        yumi.left.goto_pose_delta(l[0:3], [p_l[2],0,0])
        yumi.right.goto_pose_delta(r[0:3], [p_r[2],0,0])

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
        self.go_to_initial_state()
        for i in range(5):
            self.bc.read_raw()

        for i in range(self.T):
            state = self.bc.read_raw()
            # cv2.imshow('debug',state)
            # cv2.waitKey(30)
            pos_l,pos_r = self.eval_policy(get_state(state))
            self.move_to_pose(pos_l,pos_r)

    def go_to_initial_state(self):
        '''
        FILL IN WITH JACKY'S CODE 
        '''
        self.yumi.left.open_gripper()
        #self.yumi.right.open_gripper()
        self.yumi.left.goto_state(YuMiState([-43.37, -94.83, 49.89, -88.25, -22.95, 129.29, 63.68]))
        self.yumi.right.goto_state(YuMiState([37.82, -57.81, 37.31, 77.0, 46.81, -38.72, -83.49]))

        self.yumi.left.goto_state(YuMiState([-86.15, -43.34, 26.81, -52.19, -37.63, 92.99, 111.3]))
        self.yumi.right.goto_state(YuMiState([85.42, -40.77, 26.49, 48.5, -31.53, 90, -111.79]))

        #self.yumi.right.close_gripper(3)
        _ = raw_input("Place cup in left gripper. [ENTER] to confirm.")
        self.yumi.left.close_gripper()
        _ = raw_input("Place object in place. [ENTER] to confirm.")
        


if __name__ == "__main__":
   
    
    yumi = YuMiRobot()

    # r = np.array([-0.05,0.0,0.0])

    # yumi.left.goto_pose_delta(r,[0.0,0.0,0.0])



    scooper = Scooper(yumi)

    while True: 
        scooper.rollout()


