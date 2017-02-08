''''
File to collect data for a neural network policy

Author: Michael Laskey
'''
from alan.control.yumi_subscriber import YuMiSubscriber
import time, os, pygame
import IPython
import cv2
from deep_lfd.control.xbox_controller import *
from deep_lfd.core.net_trainer import Net_Trainer
from deep_lfd.rgbd.bincam_2D import BinaryCamera 
from perception.primesense_sensor import PrimesenseSensor
###############CHANGGE BELOW TO TRAIN A DIFFERENT PRIMITIVE##############
from deep_lfd.p_pi.p_grasp_rss.options import Grasp_Options as p_options
from deep_lfd.p_pi.p_grasp_rss.com import Grasp_COM as com
##########################################################################

class Demonstration:

	def __init__(self, controller):
		'''
		Init class for demonstration collecitng File

		Parameters
		----------
		controller: XboxController
			XboxController commands use to start and stop demonstration
		'''
		self.c = controller
		self.sub = YuMiSubscriber()
		self.sub.start()
		#clear buffer 
		for i in range(5):
			pose = self.sub.left.get_pose()


		self.ps = PrimesenseSensor(frame = 'primesense_overhead')
		self.ps.start()  
		self.net_train = Net_Trainer(com(),'None',self.c,self.sub,depthcam=self.ps)


	def do_net_training(self):
		'''
		Function call to get state and demonstration. See net_train for 
		more detail
		'''

		self.net_train.capture_state()
		self.net_train.collect_data_full()
	


if __name__ == '__main__':

	# new participants name to create dir for their demonstration
	controller = XboxController()
	d = Demonstration(controller)
	
	while True:
		d.do_net_training()


