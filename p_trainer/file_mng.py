import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
from tensor import inputdata
from alan.p_trainer.compile_sup import Compile_Sup #specific: imports compile_reg from sup
#from alan.rgbd.binaryThreshBox import transform_image
import numpy as np, argparse
from alan.synthetic.affine_synthetic import Affine_Synthetic

#######NETWORK FILES####################
#specific: imports options from specific options file
from alan.p_hanoi.options import Hanoi_Options as options 

#specific: fetches specific net file
from tensor.net_hanoi import Net_Hanoi as Net 


class File_Mng():

	def __init__(self,options):
		self.bc = bc
		self.com = com
		self.options = options
		#load train set
		self.load_files()



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



	def delete_synth_data(self):

