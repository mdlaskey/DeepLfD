import numpy as np
from alan.control import YuMiRobot, YuMiState
import time
import IPython

class Kinesthetic_Deployer:
    def __init__(self, yumi,opt,name):
        self._yumi = yumi

        self.motion_R = np.load(opt.policies_dir+name+'R.npy')
        self.motion_L = np.load(opt.policies_dir+name+'L.npy')

    def rollout(self): 

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

    def rollout_time(self):
        # for now I will assume these files exist
        #self.timings_R = np.load(opt.policies_dir+name+'Rtimings.npy')
        #self.timings_L = np.load(opt.policies_dir+name+'Ltimings.npy')
   
        #for now i will assume these matrices DEFINITELY have the same
        #length...
        T = len(self.motion_R)
        self._yumi.set_z('z1')
        self._yumi.set_v(400)

        delay = 0.01
        for i in range(1,T):
            #print('R timing: ' + str(self.timings_R[i]))
            #print('L timing: ' + str(self.timings_L[i]))
            time.sleep(delay)
            self._yumi.right.goto_state(YuMiState(self.motion_R[i]))
            self._yumi.left.goto_state(YuMiState(self.motion_L[i]))

        self._yumi.set_z('fine')
        self._yumi.set_v(1500)

    def isolate_movement(self, jointList=[]):
        # pass in a list of joints to not move
        # this only works on one arm right now - left or right
        T = len(self.motion_R)
        self._yumi.set_z('z1')
        self._yumi.set_v(400)

        for i in range(1, T):
            time.sleep(0.01)
            newStateLeft = self.updateState(YuMiState(self.motion_L[i]), jointList)
            #recordedStateRight = updateState(self.motion_R[i])

            #self._yumi.right.goto_state(recordedStateRight)
            self._yumi.left.goto_state(newStateLeft)


    def updateState(self, state, jointList=[]):
        print("planned state: " + str(state))
        currentState = self._yumi.left.get_state()
        print("currentState" + str(currentState))
        jointLength = len(jointList)
        print("jointLength: " + str(jointLength))
        for j in range(0, jointLength):
            print("joint: " + str(j))
            if jointList[j] == 1:
                state.joint1 = currentState.joint1
            elif jointList[j] == 2:
                state.joint2 = currentState.joint2
            elif jointList[j] == 3:
                state.joint3 = currentState.joint3
            elif jointList[j] == 4:
                state.joint4 = currentState.joint4
            elif jointList[j] == 5:
                state.joint5 = currentState.joint5
            elif jointList[j] == 6:
                state.joint6 = currentState.joint6
            elif jointList[j] == 7:
                state.joint7 = currentState.joint7
        print ('updated state: ' + str(state))
        return state




if __name__ == '__main__':

    yumi = YuMiRobot()
    opt = Options()
    name = "breathe_in"
    KD = Kinesthetic_Deployer(yumi, opt,name)
    KD.rollout()

