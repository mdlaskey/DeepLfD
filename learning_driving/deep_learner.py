import sys, os

import IPython
from deep_lfd.tensor import inputdata
from deep_lfd.tensor.nets.net_driving import Net_Driving as Net
from compile_sup import Compile_Sup 
import numpy as np, argparse
from numpy.random import rand,randint
from deep_lfd.synthetic.affine_synthetic import Affine_Synthetic

class DeepLearner:   


	def __init__(self):

		self.state_space = []
		self.labels = []

		self.train_states = []
		self.train_labels = []

		self.test_states = []
		self.test_labels = []

		self.net = Net()

		self.test_loss = []
		self.train_loss = []

	def add_rollout(self,imgs,labels):

		self.state_space.append(imgs)
		self.labels.append(labels)

	def train_learner(self):
    	self.net.optimize(iterations,data, batch_size=batch_size)

  def eval_policy(self,img):
    	outval= self.net.output(self.sess, state,channels=1)
    	self.test_loss.append(self.net.test_loss)
    	self.train_loss.append(self.net.train_loss)


  def add_to_data(self,states,labels):

    	#First split between test and train 

    	batch_size = len(states)

    	for i in range(batch_size):

    		if(rand() > 0.1):
    			self.train_states.append(states[i])
    			self.train_states.append(labels[i])

    		else:
    			self.test_states.append(states[i])
    			self.test_states.append(labels[i])




class IMData():
    
    def __init__(self,trn_s,trn_l,tst_s,tst_l,channels=3):

    	self.trn_s = trn_s
    	self.trn_l = trn_l

    	self.tst_s = tst_s
    	self.tst_l = tst_l


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
          im = im2tensor(im,self.channels)

          label = self.trn_l[traj_idx][state_idx]
			   batch.append((im, labels))

        batch = zip(*batch)
        return list(batch[0]), list(batch[1])


    def next_test_batch(self,n = 50):
        """
        read into memory on request
        :return: tuple with images in [0], labels in [1]
        """
        num_data = len(self.trn_s)
       	batch = []

       	for i in range(n):
       		traj_idx = randint(num_data)
       		traj_len = len(self.tst_s[traj_idx])

       		state_idx = randint(traj_len)

       		im = self.tst_s[traj_idx][state_idx]
            im = im2tensor(im,self.channels)

            label = self.tst_l[traj_idx][state_idx]
			batch.append((im, labels))

        batch = zip(*batch)
        return list(batch[0]), list(batch[1])




