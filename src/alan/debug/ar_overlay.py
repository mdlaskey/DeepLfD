import sys
import tty, termios
from alan.rgbd.bincam_2D import BinaryCamera 
from alan.rgbd.registration_wc import RegWC
from alan.control import YuMiRobot, YuMiState, YuMiControlException
from alan.lfd_amazon.amazon_overlay import makeOverlay,generalOverlay
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np


def debug_overlay(bc,img_n):
	img = cv2.imread(img_n)
	frame = bc.read_binary_frame()
	display_img = np.zeros([frame.shape[0],frame.shape[1],3])

	while (1):
		a = cv2.waitKey(30)

		if a == 1048603:
			cv2.destroyWindow("camera")
			break
		time.sleep(.005)       
		frame = bc.read_binary_frame()

		display_img[:,:,0] = img[:,:,0]
		display_img[:,:,1] = frame[:,:,0]

		cv2.imshow("cam", display_img)
		#cv2.imshow("cam",bc.read_color_frame())
		cv2.waitKey(30)
