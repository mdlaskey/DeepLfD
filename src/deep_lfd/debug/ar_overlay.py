''''
    A class used to display overlays on a webcam image that allows to reprodduce 
    test and training configurations. The class also shows what the neural network 
    predictions on both the image in the database and the recreated image.  

    Author: Michael Laskey 

'''




import sys
import tty, termios
from deep_lfd.rgbd.bincam_2D import BinaryCamera 
from deep_lfd.rgbd.registration_wc import RegWC
from alan.control import YuMiRobot, YuMiState, YuMiControlException
from alan.lfd_amazon.amazon_overlay import makeOverlay,generalOverlay
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np


#For unit test only 
from deep_lfd.p_pi.p_grasp_rss.options import Grasp_Options as Options
from deep_lfd.p_pi.p_grasp_rss.com import Grasp_COM as COM





class AR_Debug():
	
	def __init__(self,bc,com):
		self.bc = bc
		self.com = com
		self.options = self.com.Options
		#load train set
		self.load_files()
		#load test set

	def load_files(self):
		#Load Data
		train_file = open(self.options.train_file,'r')
		test_file = open(self.options.test_file,'r')

		self.test_data = []
		self.train_data = []

		for line in train_file:
			line = line.split()
			img = line[0]
			label = [float(line[1]),float(line[2]),float(line[3])]
			self.train_data.append([img, label])

		for line in test_file:
			line = line.split()
			img = line[0]
			label = [float(line[1]),float(line[2]),float(line[3])]
			self.test_data.append([img, label])

		num_test = len(self.test_data)
		num_train = len(self.train_data)

	def get_initial_state(self,sample_iter):
		''''
		Gets an initial state sample corresponding to the given rollout number from the initial trained neural net. 
		Then displays the initial state and waits for the user to place the objects in the correct configuration

		Parameters
		----------
		sample_iter : int
			The rollout number corresponding to the trained initial state sample. 
			If no rollout exists will throw an exception

		'''

		#get random image from train
		len_train = len(self.train_data)

		num_rollout = -1
		sample = 0

		while not num_rollout == sample_iter:
			i = np.random.randint(len_train)

			[img_p, label] = self.train_data[i]

			#get_num_rollout 
			split_img_p = img_p.split('/')
			file_name = split_img_p[-1]
			f_split = file_name.split('_')
			rollout = f_split[0]
			num_rollout = int(rollout[7:])
			sample += 1

			if(sample > 5000):
				raise Exception('Sample Iteration Can Not be Found in Original Training File')


		#load image
		img = cv2.imread(img_p)
		p_img = self.debug_overlay(img)


	def get_rollout_info(self,img_p):
		''''
		Gets the rollout number and frame number from the path specified in a training or test file

		Parameters
		----------
		img_p : String
			String that gives an absolute path to the image

		Returns 
		-------
		int
			The rollout number
		int 
			The frame number

		'''

		#get_num_rollout 
		split_img_p = img_p.split('/')
		file_name = split_img_p[-1]
		f_split = file_name.split('_')
		rollout = f_split[0]
		num_rollout = int(rollout[7:])

		#get frame number 
		frame_num = int(f_split[1])

		return num_rollout,frame_num


	


	def debug_overlay(self,img):
		''''
		Displays an image to be be made as an overlay 
		Waits for user to press ESC Key On Display Window to Exit

		Parameters
		----------
		img : Numpy Array
			Binary Image to be displayed as reference 

		output: None

		'''
		frame = self.bc.read_binary_frame()
		display_img = np.zeros([frame.shape[0],frame.shape[1],3])


		while (1):
			a = cv2.waitKey(30)

			if a == 1048603:
				cv2.destroyWindow("camera")
				break
			time.sleep(.005)       
			frame = self.bc.read_binary_frame()

			display_img[:,:,1] = img[:,:,0]
			display_img[:,:,2] = frame[:,:,0]

			cv2.imshow("cam", display_img)
			#cv2.imshow("cam",self.bc.read_color_frame())
			cv2.waitKey(30)

		return frame


	def check_test_error(self,use_synthetic = False):
		''''
		Gets an image from the test set. Asks a users to recreate it. 
		Reports net predicion on recreated scene, the data point and the test label

		Parameters
		----------
		use_synthetic : Bool
			If True, draws data from the synthetic dataset (Default False)

		Returns 
		-------
		None

		'''

		#get random image from train
		len_test = len(self.test_data)
		i = np.random.randint(len_test)

		[img_p, label] = self.test_data[i]

		#load image
		img = cv2.imread(img_p)
		p_img = self.debug_overlay(img)

		print "----------LABEL IN TEST-------------"
		print self.com.eval_label(label)
		print "----------NET PREDICTION ON REAL----------------"
		print self.com.eval_policy(p_img)
		print "----------NET PREDICTIN ON DATASET---------"
		print self.com.eval_policy(img)

	def check_train_error(self,use_synthetic = False):
		''''
		Gets an image from the training set. Asks a users to recreate it. 
		Reports net predicion on recreated scene, the data point and the test label

		Parameters
		----------
		use_synthetic : Bool
			If True, draws data from the synthetic dataset (Default False)

		Returns 
		-------
		None

		'''

		#get random image from train
		len_train = len(self.train_data)
		i = np.random.randint(len_train)

		[img_p, label] = self.train_data[4288]
		

		#load image
		img = cv2.imread(img_p)
		p_img = self.debug_overlay(img)

		print "----------LABEL IN TRAINING-------------"
		print self.com.eval_label(label)
		print "----------NET PREDICTION ON REAL----------------"
		print self.com.eval_policy(p_img)
		print "----------NET PREDICTIN ON DATASET---------"
		print self.com.eval_policy(img)


	def check_test_error_of_image(self,img_p,use_synthetic = False):
		''''
		Gets an image from baseline test rollout. Asks a users to recreate it. 
		Reports net predicion on recreated scene, the data point and the test label

		Parameters
		----------
		use_synthetic : Bool
			If True, draws data from the synthetic dataset (Default False)

		Returns 
		-------
		None

		'''

		#load image
		img = cv2.imread(img_p)
		p_img = self.debug_overlay(img)

		print "----------NET PREDICTION ON REAL----------------"
		print self.com.eval_policy(p_img)
		print "----------NET PREDICTIN ON DATASET---------"
		print self.com.eval_policy(img)


if __name__ == '__main__':

    # new participants name to create dir for their demonstration
    dr = "/Sammy/"

    #Put the net name next to the ckpt file the net is save as 
    net_list = ['neural_net_0/','grasp_net_11-28-2016_09h57m38s.ckpt']

