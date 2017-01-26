'''
Kinesthic Motions to close the amazon box

Author: Michael Laskey

'''
import numpy as np
from alan.control import YuMiRobot, YuMiState
from deep_lfd.core.k_deploy import Kinesthetic_Deployer
import time
import IPython
from options import Echo_Options as Options


def cap_on(yumi):
	'''
	Call function to execute a motion to close the box

	Parameters
	----------
	yumi: An instantiated robot class

	'''
	opt = Options()

	for i in range(3):
		policy = Kinesthetic_Deployer(yumi,opt,"pi_"+str(i))
		policy.rollout()
	



if __name__ == '__main__':
	yumi = YuMiRobot()

	cap_on(yumi)
