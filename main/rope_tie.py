import sys
import tty, termios
from alan.rgbd.bincam_2D import BinaryCamera 
from alan.rgbd.registration_wc import RegWC
from alan.core.p_deploy import Policy 
from alan.control import YuMiRobot, YuMiState, YuMiControlException
from alan.debug.ar_overlay import debug_overlay
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np

from alan.p_singulate_L.options import Singulate_LOptions as Options_L
from alan.p_singulate_L.com import Singulate_LCOM as COM_L

from alan.lfd_amazon.options import AmazonOptions as Options_R
from alan.lfd_amazon.amazon_com import Amazon_COM as COM_R

if __name__ == "__main__":
   
    
    yumi = YuMiRobot()
    options = Options_R()
    com_r = COM_R(train=False)
    bincam = BinaryCamera(options)
    yumi.set_z('fine')
    
    
    bincam.open(threshTolerance= options.THRESH_TOLERANCE)
    frame = bincam.display_frame()
    yumi.set_v(1500) 
    
    pi_R = Policy(yumi,com,bincam=bincam, ex_motion = False)

    options = Options_L()
    com_l = COM_L(train=False)
   
    yumi.set_z('fine')

    yumi.set_v(1500)
    pi_L = Policy(yumi,com,bincam=bincam,ex_motion = False)


    pos_r,rot_r =  pi_R.rollout()
    pos_l,rot_l =  pi_L.rollout()

    com_r.move_to_pose(yumi,pos_r,rot_r)
    com_l.move_to_pose(yumi,pos_l,rot_l)

    com_r.execute_motion(yumi)
    com_l.execute_motion(yumi)



    print "Done."
