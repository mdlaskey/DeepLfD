import sys, os

import IPython
import numpy as np

from sklearn import svm
from deep_lfd.learning_driving.learner import *

class LinearLearner(Learner):   

	def __init__(self):
		super(LinearLearner, self).__init__()
		self.net = svm.LinearSVC()

	def train_learner(self):
		print("adding to data")
		X_train, Y_train = self.compile_training()
		print("fitting")
		# IPython.embed()
		self.net.fit(X_train, Y_train)

	def eval_policy(self, state):
		processed_state = self.preprocess_image(state).reshape(1, -1)
		output = self.net.predict(processed_state)[0]
		return output

	def get_statistics(self):
		train_score = np.mean(np.array([self.net.score(self.train_states[i], self.train_labels[i]) \
			for i in range(len(self.train_states))]))
		test_score = np.mean(np.array([self.net.score(self.test_states[i], self.test_labels[i]) \
			for i in range(len(self.test_states))]))
		return train_score, test_score




