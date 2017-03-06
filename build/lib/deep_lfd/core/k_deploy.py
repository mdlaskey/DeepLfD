'''
Class for deploying a kinesthic motion

Author: Michael Laskey

'''


import numpy as np
from alan.control import YuMiRobot, YuMiState
import time
import IPython

class Kinesthetic_Deployer:
    def __init__(self, yumi,opt,name):
        '''
        Initilization Class for Deploy class 

        Parameters
        ----------
        yumi : YumiRobot 

        opt : Options

        name : string
            File name of policy

        '''
        self._yumi = yumi

        self.motion_R = np.load(opt.policies_dir+name+'R.npy')
        self.motion_L = np.load(opt.policies_dir+name+'L.npy')

    def rollout(self): 
        '''
        Deploys the current policy
        '''

        #for now i will assume these matrices DEFINITELY have the same
        #length...

        T = len(self.motion_R)
        self._yumi.set_z('z1')
        self._yumi.set_v(400)

        

        if len(self.motion_L.shape) == 1:
            self._yumi.right.goto_state(YuMiState(self.motion_R))
            self._yumi.left.goto_state(YuMiState(self.motion_L))

        else:
            for i in range(1,T):
                time.sleep(0.01)
                self._yumi.right.goto_state(YuMiState(self.motion_R[i]))
                self._yumi.left.goto_state(YuMiState(self.motion_L[i]))

        self._yumi.set_z('fine')
        self._yumi.set_v(1500)

    



if __name__ == '__main__':

    yumi = YuMiRobot()
    opt = Options()
    name = "breathe_in"
    KD = Kinesthetic_Deployer(yumi, opt,name)
    KD.rollout()

