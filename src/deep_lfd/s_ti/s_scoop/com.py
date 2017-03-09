import sys, os, time, cv2, argparse
import tty, termios
import numpy as np
import IPython
from alan.control import YuMiRobot, YuMiState
from alan.control.yumi_subscriber import YuMiSubscriber

from deep_lfd.core.common import Common
from deep_lfd.rgbd.registration_ps import RegPS
from deep_lfd.rgbd.bincam_2D import BinaryCamera

from core import RigidTransform, YamlConfig



###############CHANGGE FOR DIFFERENT PRIMITIVES##########################
from deep_lfd.p_pi.p_grasp_rss.options import Grasp_Options as Options 

from deep_lfd.tensor.nets.net_grasp import Net_Grasp as Net 
#########################################################################


def get_label(poses):
    #Hack up the poses 

    return poses

def get_state(image):
    #CROP VALUES 
    org = [0,0]
    dim = [0,0]
    IPython.embed()
    crop_image = image[org[0]:org[0]+dim[0],org[1]:org[1]+dim[1]]


    return crop_image 




if __name__ == '__main__':
    options = Options()
    # sub = YuMiSubscriber()
    # sub.start()

    # while True:
    #     timeLeft, pose_l = sub.left.get_pose()
    #     print pose_l.euler_angles

    yumi = YuMiRobot()
    com = Grasp_COM()

    com.go_to_initial_state(yumi)
