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

from deep_lfd.p_pi.p_grasp_rss.options import Grasp_Options as Options
from deep_lfd.p_pi.p_grasp_rss.com import Grasp_COM as COM

from numpy.random import rand



if __name__ == '__main__':

	robot = YuMiRobot()
	com = COM()

	com.go_to_initial_state(robot)
	cp = com.get_cp(robot)


	# #TARGET POSE
	# tar_pose = np.array([0.34450001,  0.0598, 0.0484  ])
	# rot = 56.0

	# for i in range(5):
	# 	pose = robot.left.get_pose()

	# print pose.euler_angles[2]
	# curr_angle = pose.euler_angles[2]

	
	# rotation = rot*np.pi/180.0
	# print "INTENDED STATE ", rotation
	# rotation = -(rotation - curr_angle)
	
	# trans = tar_pose-pose.position

	# rot = rotation*180.0/np.pi

	# com.move_to_pose(robot,trans,rot)

	# for i in range(5):
	# 	pose = robot.left.get_pose()

	# print "GOT TO STATE ", pose.euler_angles[2]
