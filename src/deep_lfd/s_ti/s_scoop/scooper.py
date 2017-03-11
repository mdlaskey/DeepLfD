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
        self.yumi = yumi
        yumi.set_z('fine')

        self.options = Options()
        self.bc = BinaryCamera(self.options)

        self.net = Net(self.option)
        self.sess = self.net.load(self.Options.policies_dir+'net_file.ckpt')
        
        self.bc.open(threshTolerance=self.options.THRESH_TOLERANCE)
       
        self.T = 60

    def eval_policy(self,state):
        netn = Net(self.Options)
        sess = netn.load(var_path=self.var_path)
        outval = netn.output(sess, state,channels=3)
      
        pos_r, pos_l = rescale(outval)
        

        return pos_r,pos_l


    def move_to_pose(self,p_r,p_l):

        yumi.left.goto_pose_delta(p_l[0:3])
        yumi.left.goto_pose_delta(np.zeros(3), [0.0,0.0,p_l[3]])

        yumi.right.goto_pose_delta(p_r[0:3])
        yumi.right.goto_pose_delta(np.zeros(3), [0.0,0.0,p_r[3]])



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
        for i in range(self.T):
            state = self.bc.read_color_frame()
            pos_r,pos_l = self.eval_policy(get_state(state))
            self.move_to_pose(pos_r,pos_l)



    def go_to_initial_state():
        '''
        FILL IN WITH JACKY'S CODE 
        '''
        


if __name__ == "__main__":
   
    
    yumi = YuMiRobot()
    scooper = Scooper(yumi)

    while True: 
        scooper.rollout()


