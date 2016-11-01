from alan.control import YuMiConstants as YMC
from alan.control.yumi_subscriber import YuMiSubscriber
from alan.control.xboxController import *

import IPython
import numpy as np

import logging
from time import sleep

from alan.k_rope_tie.options import Rope_TieOptions as Options


class Kinesthetic_Trainer:

    def __init__(self, sub,options,name):
        logging.getLogger().setLevel(YMC.LOGGING_LEVEL)
        self._sub = sub

        # whatre these values doing...
        self._controller = XboxController([1,1,1,1,1,1,1])

        # will probably need to initialize these differently
        self._statesR = []
        self._statesL = []
        self.opt = options
        self.name = name

    def start_motion(self):
        self._sub.start()
        low_pass = 250
        count = 0

        while True:
            controls = self._controller.getUpdates()
            stop = self.detect_stop(controls)
            if stop:
                print "WE STOPPED"
                self.save_trajectory()
                break

            else:
                if(count == low_pass):
                    self.collect_state()
                    count = 0
                else:
                    count += 1



    def collect_state(self):
        t1, pose_l = sub.left.get_state()
        t2, pose_r = sub.right.get_state()

        print "Right: ", pose_r
        print "Left: ", pose_l
        self.store_state(pose_r, pose_l)
        
    def store_state(self, stateR, stateL):
        self._statesR.append(stateR.joints)
        self._statesL.append(stateL.joints)

    def save_trajectory(self):
        np.save(self.opt.policies_dir+name+"R", self._statesR)
        np.save(self.opt.policies_dir+name+"L", self._statesL)

        print("Trajectories stored!")



    def detect_stop(self, controls):
        deltas = [0.0] * 5
        MM_T_M = 0.001
        stop = False
        if controls == None:
            return None, True
        return stop
    

if __name__ == '__main__':

    sub = YuMiSubscriber()
    opt = Options()
    name = "puppet_1"
    KT = Kinesthetic_Trainer(sub,opt,name)
    KT.start_motion()

