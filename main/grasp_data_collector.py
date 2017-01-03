
from alan.control.yumi_subscriber import YuMiSubscriber
import time, os, pygame
import IPython
import cv2
from deep_lfd.control.xbox_controller import *
from deep_lfd.core.net_trainer import Net_Trainer
from deep_lfd.rgbd.bincam_2D import BinaryCamera 

###############CHANGGE BELOW TO TRAIN A DIFFERENT PRIMITIVE##############
from deep_lfd.p_pi.p_grasp.options import Grasp_Options as p_options
from deep_lfd.p_pi.p_grasp.com import Grasp_COM as com
##########################################################################

class Demonstration:

	def __init__(self, controller):
		self.c = controller
		self.sub = YuMiSubscriber()
		self.sub.start()
	

		self.bc = BinaryCamera(p_options())
		self.bc.open()   
		self.net_train = Net_Trainer(com(),self.bc,'None',self.c,self.sub)


	def do_net_training(self):

		self.net_train.capture_state()
		self.net_train.collect_data_full()
	


if __name__ == '__main__':

	# new participants name to create dir for their demonstration
	controller = XboxController()
	d = Demonstration(controller)
	
	while True:
		d.do_net_training()


