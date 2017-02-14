import sys, os

import IPython
import numpy as np, argparse
from numpy.random import rand,randint

# from keras.models import Sequential
# from keras.optimizers import SGD
# from keras.layers import Dense, Activation, Flatten
# from keras.layers.convolutional import Convolution2D
# from keras.utils.np_utils import to_categorical

from deep_lfd.learning_driving.learner import *
# from deep_lfd.tensor.nets.net_driving import *
# y_binary = to_categorical(y_int)

class DeepLearner(Learner):   
	# TODO: Replace 'to_categorical' with one-hot vector
	def __init__(self):
		super(DeepLearner, self).__init__()
		self.reset()

	def train_learner(self):
		train_states, train_labels = self.compile_dataset('train', tensor=True)
		train_labels = to_categorical(train_labels, nb_classes=5)
		# TODO: Fit model to training set
		self.net.fit(train_states, train_labels, nb_epoch=5, batch_size=32, verbose=0)

	def eval_policy(self, state):
		processed_state = self.preprocess_image(state)
		state_expanded = np.expand_dims(np.expand_dims(processed_state, 0), 1)
		# TODO: Predict output of net
		output = self.net.predict_classes(state_expanded, verbose=0)[0]
		return output

	def get_statistics(self):
		train_states, train_labels = self.compile_dataset('train', tensor=True)
		train_labels = to_categorical(train_labels, nb_classes=5)
		#TODO: Evaluate model on train set
		train_loss, train_acc = self.net.evaluate(train_states, train_labels, verbose=0)
		test_states, test_labels = self.compile_dataset('test', tensor=True)
		test_labels = to_categorical(test_labels, nb_classes=5)
		if len(test_states) > 0:
			# TODO: Evaluate model on test set
			test_loss, test_acc = self.net.evaluate(test_states, test_labels, verbose=0)
		else:
			test_loss, test_acc = [np.inf, 0.0]
		return train_acc, test_acc

	def preprocess_image(self, state):
		downsampled = self.downsample_image(self.downsample_image(state))
		return downsampled

	def reset(self):
		#TODO: Compile model
		super(DeepLearner, self).reset()
		model = Sequential()
		model.add(Convolution2D(5, 7, 7, border_mode='same', input_shape=(1, 125, 125)))
		model.add(Activation("relu"))
		model.add(Flatten())
		model.add(Dense(output_dim=60))
		model.add(Activation("relu"))
		model.add(Dense(output_dim=5))
		model.add(Activation("softmax"))
		model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['categorical_accuracy'])
		self.net = model
		# self.net = Net_Driving(channels=1)

class IMData():
	
	def __init__(self,trn_s,trn_l,tst_s,tst_l,channels=3):

		self.trn_s = trn_s
		self.trn_l = trn_l

		self.tst_s = tst_s
		self.tst_l = tst_l
		self.channels = channels


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




