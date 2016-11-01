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

from alan.p_singulate_L.options import Singulate_LOptions as Options
from alan.p_singulate_L.com import Singulate_LCOM as COM


if __name__ == "__main__":
   
    
    yumi = YuMiRobot()
    options = Options()
    com = COM(train=False)
    bincam = BinaryCamera(options)
    yumi.set_z('fine')
    
    
    bincam.open(threshTolerance= options.THRESH_TOLERANCE)

    frame = bincam.display_frame()

    yumi.set_v(1500)
    
    debug_overlay(bincam,options.binaries_dir+'rollout10_frame_0.jpg')
    
    
    pi = Policy(yumi,com,bincam=bincam)

    while True:
        pi.rollout()

    print "Done."
