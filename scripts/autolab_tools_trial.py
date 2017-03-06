import copy
import cPickle as pkl
import cv2
import IPython
import json
import logging
import matplotlib.pyplot as plt
import numbers
import numpy as np
import os
import random
import sklearn.decomposition as sd
import sys
from time import sleep, time

from core import Box, Point, RigidTransform
from perception import DepthImage, ColorImage, RgbdForegroundMaskQueryImageDetector

from dexnet.planning.grasp_planner import SegmentationBasedGraspState
from core import RigidTransform, YamlConfig
from perception.primesense_sensor import PrimesenseSensor
from perception.primesense_sensor import SensorOperator
from perception.kinect2_sensor import Kinect2Sensor
from deep_lfd.rgbd.registration_ps import RegPS

from visualization import Visualizer2D as vis2d



if __name__ == '__main__':

	# ps = PrimesenseSensor(frame = 'primesense_overhead')
	# ps2 = PrimesenseSensor(frame ='primsense_desk')
	operator = SensorOperator()
	operator.start_multiple()

	# yml_file = '/home/autolab/Workspace/jeff_working/dexnet_reorg/data/experiments/grasping_gym/cfg/default_lfd.yaml'
	# cfg = YamlConfig(yml_file)


	# grasp_state = SegmentationBasedGraspState(cfg)




	# ps.start()

	# ps2 = PrimesenseSensor(frame ='primsense_desk')
	# ps2.start_multiple()

	#IPython.embed()
	# color_im,d_img,ir_img = ps.frames()
	psList = operator.primeSensors()
	color_im,d_img,ir_img = psList[0].frames()
	color_im2,d_img2,ir_img2 = psList[1].frames()
	# for s in psList:
	# 	operator.stop(s)	#SEGFAULT

	IPython.embed()
	# median_depth = ps.median_depth_img()
	# intrs = ps.ir_intrinsics

	# ob_dect = grasp_state.get_grasp_state(color_im,median_depth,intrs)

	# depth = ob_dect.depth_thumbnail
	# intrs = ob_dect.cropped_ir_intrinsics
	# reg = RegPS()
	
	# pos_camera = [100,100,depth[100,100]]

	# print "POINT IN CAMERA ",pos_camera

	# pos_robot = reg.pixel_to_robot(pos_camera,intrs)

	# print "ROBOT POINT ", pos_robot

	# pos_camera_back = reg.robot_to_pixel(pos_robot,intrs)

	# print "BACK IN CAMERA ", pos_camera_back

	# ps.close()
	#ps2.close()
