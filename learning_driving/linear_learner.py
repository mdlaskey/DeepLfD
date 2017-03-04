import sys, os

import IPython
from deep_lfd.tensor import inputdata
from deep_lfd.tensor.nets.net_driving import Net_Driving as Net
from compile_sup import Compile_Sup 
import numpy as np, argparse
from numpy.random import rand,randint
from deep_lfd.synthetic.affine_synthetic import Affine_Synthetic
import cv2 

class LinearLearner:   


	def __init__(self):

		self.state_space = []
		self.labels = []

		self.train_states = []
		self.train_labels = []

		self.test_states = []
		self.test_labels = []

		self.pi = LinearSVM(alpha=1.0)


		self.test_loss = []
		self.train_loss = []


	def train_learner(self):
		train_s, train_l = self.compile_training()
    	self._pi_L.fit(train_s,train_l)

    def eval_policy(self,img):
    	outval= self.net.output(self.sess, state,channels=1)
    	self.test_loss.append(self.net.test_loss)
    	self.train_loss.append(self.net.train_loss)

   	def compile_training(self,n):
        """
        Read into memory on request
        :param n: number of examples to return in batch
        :return: tuple with images in [0] and labels in [1]
        """
       	num_data = len(self.train_states)
       	batch = []

       	for i in range(n):
       		traj_idx = randint(num_data)
       		traj_len = len(self.trn_s[traj_idx])

       		state_idx = randint(traj_len)

       		im = self.trn_s[traj_idx][state_idx]
            im = extract_HOG(img)

            label = self.trn_l[traj_idx][state_idx]
			batch.append((im, labels))

        batch = zip(*batch)
        return list(batch[0]), list(batch[1])

    def add_to_data(self,states,labels):

    	#First split between test and train 

    	batch_size = len(states)

    	for i in range(batch_size):

    		if(rand() > 0.1):
    			hog_state = self.extract_HOG(stat)
    			self.train_states.append(states[i])
    			self.train_states.append(labels[i])

    		else:
    			self.test_states.append(states[i])
    			self.test_states.append(labels[i])

    def extract_HOG(self,state):
    	hog = cv2.HOGDescriptor()
 		h = hog.compute(im)
 		return h







