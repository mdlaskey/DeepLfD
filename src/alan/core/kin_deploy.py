import numpy as np
from alan.control import YuMiRobot, YuMiState
from alan.k_rope_tie.options import Rope_TieOptions as Options
import time
import IPython

class Kinesthetic_Deployer:
    def __init__(self, yumi, opt,name):
        self._yumi = yumi

        self.motion_R = np.load(opt.policies_dir+name+'R.npy')
        self.motion_L = np.load(opt.policies_dir+name+'L.npy')

    def rollout(self): 

        #for now i will assume these matrices DEFINITELY have the same
        #length...
   
        T = len(self.motion_R)
        self._yumi.set_z('z10')
        self._yumi.set_v(1500)
        for i in range(1,T):
            time.sleep(0.01)
            self._yumi.right.goto_state(YuMiState(self.motion_R[i]))
            self._yumi.left.goto_state(YuMiState(self.motion_L[i]))

        self._yumi.set_z('fine')
        self._yumi.set_v(1500)



if __name__ == '__main__':

    yumi = YuMiRobot()
    opt = Options()
    name = "puppet_1"
    KD = Kinesthetic_Deployer(yumi, opt,name)
    KD.rollout()

