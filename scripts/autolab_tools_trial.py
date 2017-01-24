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
from perception import DepthImage, RgbdForegroundMaskQueryImageDetector

from dexnet.planning.grasp_planner import SegmentationBasedGraspState
from core import RigidTransform, YamlConfig
from perception.primesense_sensor import PrimesenseSensor
from perception.kinect2_sensor import Kinect2Sensor





if __name__ == '__main__':

	ps = PrimesenseSensor()
	yml_file = '/home/autolab/Workspace/jeff_working/dexnet_reorg/data/experiments/grasping_gym/cfg/default_lfd.yaml'
	cfg = YamlConfig(yml_file)

	grasp_state = SegmentationBasedGraspState(cfg)



	ps.start()

	color_im,d_img,ir_img = ps.frames()
	median_depth = ps.median_depth(0)
	intrs = ps.ir_intrinsics

	grasp_state.get_grasp_state(color_im,d_img,intrs)
	



	IPython.embed()







