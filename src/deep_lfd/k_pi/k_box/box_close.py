'''
Kinesthic Motions to close the amazon box

Author: Michael Laskey

'''
import numpy as np
from alan.control import YuMiRobot, YuMiState
from deep_lfd.core.k_deploy import Kinesthetic_Deployer
import time
import IPython
from options import Box_Options as Options


def box_close(yumi):
	'''
	Call function to execute a motion to close the box

	Parameters
	----------
	yumi: An instantiated robot class

	'''
	opt = Options()
	p_1 = Kinesthetic_Deployer(yumi,opt,"pi_1")
	p_2 = Kinesthetic_Deployer(yumi,opt,"pi_2")
	p_3 = Kinesthetic_Deployer(yumi,opt,"pi_3")

	#Go To Stretch State
	s_R = YuMiState([51.16, -99.4, 21.57, -107.19, 84.11, 94.61, -36.00])
	yumi.right.goto_state(s_R)
	s_L = YuMiState([0, -130, 30, 0, 40, 0, 135])
	yumi.left.goto_state(s_L)

	yumi.right.close_gripper()
	yumi.left.close_gripper()

	p_1.rollout()
	p_2.rollout()
	p_3.rollout()

if __name__ == '__main__':
	yumi = YuMiRobot()

	box_close(yumi)