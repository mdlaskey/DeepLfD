import sys, os
import numpy as np
from numpy.random import rand,randint
import cv2 
import IPython

class Learner(object):

	def __init__(self):

		self.state_space = []
		self.labels = []

		self.train_states = []
		self.train_labels = []

		self.test_states = []
		self.test_labels = []

		self.net = None

		self.test_loss = []
		self.train_loss = []

	def compile_training(self):
		"""
		Read into memory on request
		:param n: number of examples to return in batch
		:return: tuple with images in [0] and labels in [1]
		"""
		num_data = len(self.train_states)
		batch = []

		for i in range(num_data):
			traj_idx = i
			traj_len = len(self.train_states[traj_idx])
			for j in range(traj_len):
				state_idx = j
				# traj_idx = randint(num_data)
				# state_idx = randint(traj_len)
				im = self.train_states[traj_idx][state_idx]
				# IPython.embed()

				label = self.train_labels[traj_idx][state_idx]
				batch.append((im, label))

		# IPython.embed()
		batch = zip(*batch)
		return np.array(list(batch[0])), np.array(list(batch[1]))

	def add_to_data(self, states, labels):

		#First split between test and train 

		num_trajectories = len(states)
		for i in range(num_trajectories):
			if(rand() > 0.1):
				# hog_state = self.extract_HOG(states[i])
				# List of trajectories
				self.train_states.append([self.preprocess_image(image) for image in states[i]])
				self.train_labels.append(labels[i])
			else:
				self.test_states.append([self.preprocess_image(image) for image in states[i]])
				self.test_labels.append(labels[i])

	def preprocess_image(self, state):
		# IPython.embed()
		w, h = state.shape
		downsampled = cv2.pyrDown(state, dstsize = (w / 2, h / 2))
		w, h = downsampled.shape
		downsampled = cv2.pyrDown(downsampled, dstsize = (w / 2, h / 2))
		hog = self.extract_HOG(downsampled)
		return hog

	def extract_HOG(self, state):
		hog = cv2.HOGDescriptor()
		h = np.ravel(hog.compute(state))
		return h

