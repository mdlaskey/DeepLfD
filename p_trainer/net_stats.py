import sys, os

#from tensor import net_grasp_align #specific: fetches specific net file
import IPython
import cv2
#from tensor import inputdata
from compile_sup import Compile_Sup 
#from alan.rgbd.binaryThreshBox import transform_image
import numpy as np, argparse
from perception import DepthImage, ColorImage, RgbdForegroundMaskQueryImageDetector


from deep_lfd.p_pi.p_grasp_rss.options import Grasp_Options as Options
from deep_lfd.p_pi.p_grasp_rss.com import Grasp_COM as COM



options = Options()
com = COM()


#Load Data
train_file = open(options.train_file,'r')
test_file = open(options.test_file,'r')

test_data = []
train_data = []

#SAMPLE 200 

count = 100
c = 0
for line in train_file:
	line = line.split()
	img = line[0]
	label = [float(line[1]),float(line[2]),float(line[3]),float(line[4])]
	train_data.append([img, label])
	c += 1

c = 0
for line in test_file:
	line = line
	line = line.split()
	img = line[0]
	label = [float(line[1]),float(line[2]),float(line[3]),float(line[4])]
	test_data.append([img, label])
	c+= 1

num_test = len(test_data)
num_train = len(train_data)

test_stats = np.zeros([num_test,4])
train_stats = np.zeros([num_train,4])

#Calculate Net Differneces on Test
for i in range(num_test):
	item = test_data[i]
	img_name = item[0]
	img = DepthImage.open(img_name)
	label = item[1]

	pos,rot = com.eval_policy(img)
	pos_t,rot_t = com.eval_label(label)

	val_net = np.array([pos[0],pos[1],rot,pos[2]])
	val_true = np.array([pos_t[0],pos_t[1],rot_t,pos_t[2]])
	test_stats[i,:] = np.abs(val_net - val_true)

#Calculate Net Differences on Train
for i in range(num_train):
	item = train_data[i]
	img_name = item[0]
	img = DepthImage.open(img_name)
	label = item[1]


	pos,rot = com.eval_policy(img)
	pos_t,rot_t = com.eval_label(label)

	val_net = np.array([pos[0],pos[1],rot,pos[2]])
	val_true = np.array([pos_t[0],pos_t[1],rot_t,pos_t[2]])
	train_stats[i,:] = np.abs(val_net - val_true)



#Report Averages

x_error_train = np.sum(train_stats[:,0])/num_train
y_error_train = np.sum(train_stats[:,1])/num_train
rot_error_train = np.sum(train_stats[:,2])/num_train
z_error_train = np.sum(train_stats[:,3])/num_train

print "X TRAIN EROR ", x_error_train
print "Y TRAIN ERROR ", y_error_train
print "ROT TRAIN ERROR ", rot_error_train
print "Z TRAIN ERROR ", z_error_train

x_error_test = np.sum(test_stats[:,0])/num_test
y_error_test = np.sum(test_stats[:,1])/num_test
rot_error_test = np.sum(test_stats[:,2])/num_test
z_error_test = np.sum(test_stats[:,3])/num_test

print "X TEST EROR ", x_error_test
print "Y TEST ERROR ", y_error_test
print "ROT TEST ERROR ", rot_error_test
print "Z TEST ERROR ", z_error_test