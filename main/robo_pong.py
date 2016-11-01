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
    com = COM_R(train=False)
    bincam = BinaryCamera(options)
    yumi.set_z('fine')
    
    
    bincam.open(threshTolerance= options.THRESH_TOLERANCE)
    frame = bincam.display_frame()
    yumi.set_v(1500)
    debug_overlay(bincam,options.binaries_dir+'rollout10_frame_0.jpg')
    
    
    pi_R = Policy(yumi,com,bincam=bincam)

    options = Options_L()
    com = COM_L(train=False)
   
    yumi.set_z('fine')

    yumi.set_v(1500)
    pi_L = Policy(yumi,com,bincam=bincam,options = options)

    while True:
        pi_R.rollout()
        pi_L.rollout()

    print "Done."
