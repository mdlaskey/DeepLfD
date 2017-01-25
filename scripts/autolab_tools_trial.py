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
from perception import DepthImage, RgbdForegroundMaskQueryImageDetector, Image
from visualization import Visualizer2D as vis2D 
from core import RigidTransform, YamlConfig


if __name__ == '__main__':

	f_path = 'data/test_images/seg_depth_im_11.npy'

	test_img = Image.open(f_path)

	IPython.embed()







