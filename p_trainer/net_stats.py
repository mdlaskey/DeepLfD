import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')
from tensor import net_grasp_align #specific: fetches specific net file
import IPython
import cv2
from tensor import inputdata
from alan.p_trainer.compile_sup import Compile_Sup #specific: imports compile_reg from sup
#from alan.rgbd.binaryThreshBox import transform_image
import numpy as np, argparse

from alan.rgbd.registration_wc import RegWC

from alan.p_grasp_align.options import Grasp_AlignOptions as options #specific: imports options from specific options file
from alan.p_grasp_align.com import Grasp_AlignCOM as COM


Options = options()
com = COM(train=False)


#Load Data
train_file = open(Options.train_file,'r')
test_file = open(Options.test_file,'r')

test_data = []
train_data = []

for line in train_file:
	line = line.split()
	img = line[0]
	label = [float(line[1]),float(line[2]),float(line[3])]
	train_data.append([img, label])

for line in test_file:
	line = line.split()
	img = line[0]
	label = [float(line[1]),float(line[2]),float(line[3])]
	test_data.append([img, label])

num_test = len(test_data)
num_train = len(train_data)

test_stats = np.zeros([num_test,3])
train_stats = np.zeros([num_train,3])

#Calculate Net Differneces on Test
for i in range(num_test):
	item = test_data[i]
	img_name = item[0]
	img = cv2.imread(img_name)
	label = item[1]

	pos = com.eval_policy(img)
	pos_p = com.eval_label(label)
	test_stats[i,:] = pos_p - pos

#Calculate Net Differences on Train
for i in range(num_train):
	item = train_data[i]
	img_name = item[0]
	img = cv2.imread(img_name)
	label = item[1]

	pos = com.eval_policy(img)
	pos_p = com.eval_label(label)
	train_stats[i,:] = pos_p - pos



#Report Averages

x_error_train = np.sum(train_stats[:,0])/num_train
y_error_train = np.sum(train_stats[:,1])/num_train
rot_error_train = np.sum(train_stats[:,2])/num_train

print "X TRAIN EROR ", x_error_train
print "Y TRAIN ERROR ", y_error_train
print "ROT TRAIN ERROR ", rot_error_train

x_error_test = np.sum(test_stats[:,0])/num_test
y_error_test = np.sum(test_stats[:,1])/num_test
rot_error_test = np.sum(test_stats[:,2])/num_test

print "X TEST EROR ", x_error_test
print "Y TEST ERROR ", y_error_test
print "ROT TEST ERROR ", rot_error_test
