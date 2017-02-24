import sys, os

import IPython
import numpy as np, argparse
import cv2
from numpy.random import rand,randint

# from keras.models import Sequential
# from keras.optimizers import SGD
# from keras.layers import Dense, Activation, Flatten
# from keras.layers.convolutional import Convolution2D
# from keras.utils.np_utils import to_categorical

from deep_lfd.learning_driving.learner import *
from deep_lfd.tensor.nets.net_driving import *
# y_binary = to_categorical(y_int)
import traceback

class DeepLearner(Learner):   
	# TODO: Replace 'to_categorical' with one-hot vector
	def __init__(self, gpu=False):
		super(DeepLearner, self).__init__()
		# traceback.print_stack()
		os.environ["CUDA_VISIBLE_DEVICES"] = ""	
		if gpu:
			os.environ["CUDA_VISIBLE_DEVICES"] = "0"
		self.net = Net_Driving(channels=1) #, on_gpu=gpu)
		self.reset()

	def train_learner(self,iterations):
		print "SIZE OF TRAIN DATA ",len(self.train_states)
		print "SIZE OF TEST DATA ", len(self.test_states)
		data = IMData(self.train_states,self.train_labels,self.test_states,self.test_labels,channels=1)
		if(iterations == 0):
			initialize = True
		else: 
			initialize = False
		self.net.optimize(2000,data, batch_size=200,save=False,initialize = initialize)
		#train_states, train_labels = self.compile_dataset('train', tensor=True)
		
		# TODO: Fit model to training set
		#self.net.fit(train_states, train_labels, nb_epoch=5, batch_size=32, verbose=0)

	def eval_policy(self, state):
		processed_state = self.preprocess_image(state)
		#IPython.embed()
		A = np.zeros([1,processed_state.shape[0],processed_state.shape[1],1])
		A[0,:,:,0] = processed_state

		# TODO: Predict output of net
		output = self.net.predict(A/255.0)
		return output

	def get_statistics(self):
		return self.net.train_loss, self.net.test_loss

	def preprocess_image(self, state):

		h,w = state.shape

		size = 150

		crop_image = state[h/2-size:h/2+size,w/2-size:size+w/2]
		
		# cv2.imshow('debug',crop_image)
		# cv2.waitKey(30)
		
		
		return crop_image

	def reset(self):
		#TODO: Compile model
		self.state_space = []
		self.labels = []

		self.train_states = []
		self.train_labels = []

		self.test_states = []
		self.test_labels = []

		self.test_loss = []
		self.train_loss = []

	
		#self.net = Net_Driving(channels=1)

class IMData():
	
	def __init__(self,trn_s,trn_l,tst_s,tst_l,channels=3):

		self.trn_s = trn_s
		self.trn_l = trn_l

		self.tst_s = tst_s
		self.tst_l = tst_l
		self.channels = channels


	def im2tensor(self,im,channels=1):
	    """
	    convert 3d image (height, width, 3-channel) where values range [0,255]
	    to appropriate pipeline shape and values of either 0 or 1
	    cv2 --> tf

	    Prameters
	    ---------
	    im : numpy array 
	        matrix with shape of image

	    channels : int
	        number of channels into the network (Default 1)

	    Returns
	    -------
	    numpy array
	        image converted to the correct tensor shape
	    """
	    shape = np.shape(im)
	    h, w = shape[0], shape[1]
	   
	    zeros = np.zeros((h, w, channels))
	    for i in range(channels):
	        zeros[:,:,i] = im[:,:]/255.0
	    return zeros

	def label_to_binary(self,label):
		label_ar = np.zeros(5)
		label_ar[label] = 1.0
		return label_ar

	def next_train_batch(self,n):
		"""
		Read into memory on request
		:param n: number of examples to return in batch
		:return: tuple with images in [0] and labels in [1]
		"""
		num_data = len(self.trn_s)
		batch = []

		for i in range(n):
			traj_idx = randint(num_data)
			traj_len = len(self.trn_s[traj_idx])

			state_idx = randint(traj_len)
			
			im = self.trn_s[traj_idx][state_idx]
			im = self.im2tensor(im,self.channels)

			label = self.trn_l[traj_idx][state_idx]
			
			batch.append((im, self.label_to_binary(label)))

		batch = zip(*batch)
		return list(batch[0]), list(batch[1])


	def next_test_batch(self,n = 50):
		"""
		read into memory on request
		:return: tuple with images in [0], labels in [1]
		"""
		num_data = len(self.tst_s)
		batch = []

		for i in range(n):
			traj_idx = randint(num_data)
			traj_len = len(self.tst_s[traj_idx])

			state_idx = randint(traj_len)

			im = self.tst_s[traj_idx][state_idx]
			im = self.im2tensor(im,self.channels)

			label = self.tst_l[traj_idx][state_idx]
			batch.append((im, self.label_to_binary(label)))

		batch = zip(*batch)
		return list(batch[0]), list(batch[1])




