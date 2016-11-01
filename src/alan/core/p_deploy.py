import sys
import tty, termios
from alan.rgbd.bincam_2D import BinaryCamera 
from alan.rgbd.registration_wc import RegWC
from alan.control import YuMiRobot, YuMiState, YuMiControlException
from alan.debug.ar_overlay import debug_overlay
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np

from alan.p_grasp_align.options import Grasp_AlignOptions as Options
from alan.p_grasp_align.com import Grasp_AlignCOM as COM
class  Policy():

    def __init__(self, yumi,com,bincam=None,options = None,ex_motion=True):
        self.yumi = yumi
        self.com = com
        self.options = options 
        self.ex_motion = ex_motion
        if(bincam == None):
            bincam = BinaryCamera(self.com.Options)
            bincam.open(threshTolerance= self.com.Option.THRESH_TOLERANCE)

        self.bc = bincam
        self.cp = self.com.get_cp(yumi)

        sampleFrame = self.bc.read_frame()
        #self.overlay = makeOverlay(sampleFrame)



    def rollout(self):
        time.sleep(.5)
        self.com.go_to_initial_state(self.yumi)
       
        
        for i in range(5):
            frame = self.bc.read_binary_frame()

        if(self.options == None):
            frame = self.bc.read_binary_frame()
        else:
            frame = self.bc.read_binary_frame(options = self.com.Options)
  
        frame = self.jpg_correct(frame)
        cv2.imshow("camera", frame)
        cv2.waitKey(30)
        

        pos,rot = self.com.eval_policy(frame)

        #Get pose 
        posit = np.zeros(3)
        posit[0] = pos[0]
        posit[1] = pos[1]
        #98.1641694101 68.9216331179 -179.993896484
        #107.07569885   98.12541199 -169.56536865
        posit[2] = self.cp.position[2] 

        posit = posit - self.cp.position 

        if(Options.CHECK_COLLISION):
            posit = self.com.check_collision(frame,self.cp,posit,self.reg)

        if(self.ex_motion):
            self.com.move_to_pose(self.yumi,posit,rot)


            try:
                self.com.execute_motion(self.yumi)  
            except YuMiControlException, e:
                print str(e)
                yumi.set_v(1500)
                self.com.error_handler(self.yumi)
        else:
            return [posit, rot]


    def jpg_correct(self,frame): 
        for i in range(3):
            cv2.imwrite('get_jp.jpg',frame)
            frame= cv2.imread('get_jp.jpg')
        return frame



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
