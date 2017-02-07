import sys, os

import IPython
import numpy as np, argparse
from numpy.random import rand,randint

from keras.models import Sequential
from keras.optimizers import SGD
from keras.layers import Dense, Activation

from deep_lfd.learning_driving.learner import *
from keras.utils.np_utils import to_categorical
# y_binary = to_categorical(y_int)

class DeepLearner(Learner):   

	def __init__(self):
		super(DeepLearner, self).__init__()
		model = Sequential()
		model.add(Dense(output_dim=64, input_dim=30240))
		model.add(Activation("relu"))
		model.add(Dense(output_dim=5))
		model.add(Activation("softmax"))
		model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])
		self.net = model

	def train_learner(self):
		print("adding to data")
		X_train, Y_train = self.compile_training()
		print("fitting")
		Y_train_one_hot = to_categorical(Y_train, nb_classes=5)
		self.net.fit(X_train, Y_train_one_hot, nb_epoch=5, batch_size=32)

	def eval_policy(self, state):
		processed_state = self.preprocess_image(state).reshape(1, -1)
		output = self.net.predict_classes(processed_state)[0]
		return output

	def get_statistics(self):
		train_score = np.mean(np.array([self.net.evaluate(np.array(self.train_states[i]), \
			to_categorical(np.array(self.train_labels[i]), nb_classes=5)) \
			for i in range(len(self.train_states))]))
		test_score = np.mean(np.array([self.net.evaluate(np.array(self.test_states[i]), \
			to_categorical(np.array(self.test_labels[i]), nb_classes=5)) \
			for i in range(len(self.test_states))]))
		return train_score, test_score

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




