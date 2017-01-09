'''
Kinesthic Motions to close the amazon box

Author: Michael Laskey

'''
import numpy as np
from alan.control import YuMiRobot, YuMiState
from deep_lfd.core.k_deploy import Kinesthetic_Deployer
import time
import IPython
from options import Cap_Options as Options


def cap_on(yumi):
	'''
	Call function to execute a motion to close the box

	Parameters
	----------
	yumi: An instantiated robot class

	'''
	opt = Options()
	p_1 = Kinesthetic_Deployer(yumi,opt,"pi_1")

	p_1.rollout()
	



if __name__ == '__main__':
	yumi = YuMiRobot()

	cap_on(yumi)