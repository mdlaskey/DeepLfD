from alan.control import YuMiConstants as YMC
from alan.control.yumi_subscriber import YuMiSubscriber
from deep_lfd.control.xbox_controller import XboxController
import os
import IPython
import numpy as np

import logging
from time import sleep

#############CHANGE HERE TO TRAIN A NEW PRIMITIVE##############
from deep_lfd.k_pi.k_box.options import Box_Options as Options


class Kinesthetic_Trainer:

    def __init__(self,sub,options,name,controller,only_goal=False,init_state=False):
        logging.getLogger().setLevel(YMC.LOGGING_LEVEL)
        self._sub = sub

        self.only_goal = only_goal
        self.init_state = init_state

        # whatre these values doing...
        self._controller = controller

        # will probably need to initialize these differently
        self._statesR = []
        self._statesL = []
        self._timingsR = []
        self._timingsL = []

        self.opt = options
        self.name = name
        if not os.path.exists(self.opt.policies_dir):
            os.makedirs(self.opt.policies_dir)
        self.fname_r = self.opt.policies_dir+name+"R"
        self.fname_l = self.opt.policies_dir+name+"L"

    def start_motion(self, collect_timing=False):
        low_pass = 250
        count = 0

        print "COLLECTING STARTED"

        while True:
            controls = self._controller.getUpdates()
            stop = self.detect_stop(controls)
            if stop:
                if not self.init_state:
                    self.save_trajectory()
                break
            else:
                if(count == low_pass):
                    self.collect_state(collect_timing)
                    count = 0
                else:
                    count += 1



    def collect_state(self, collect_timing=False):
        timeLeft, pose_l = self._sub.left.get_state()
        timeRight, pose_r = self._sub.right.get_state()

        print "Right: ", pose_r
        print "Left: ", pose_l
        self.store_state(pose_r, pose_l)
        if (collect_timing == True):
            self.store_timing(timeLeft, timeRight)
            
        
    def store_state(self, stateR, stateL):
        self._statesR.append(stateR.joints)
        self._statesL.append(stateL.joints)

    def store_timing(self, timeLeft, timeRight):
        self._timingsL.append(timeLeft)
        self._timingsR.append(timeRight)

    def save_trajectory(self):
        if self.only_goal:
            # only store goal state
            np.save(self.fname_r, self._statesR[-1])
            np.save(self.fname_l, self._statesL[-1])

        else:
            np.save(self.fname_r, self._statesR)
            np.save(self.fname_l, self._statesL)

        print("Trajectories stored!")

    def get_file_names(self):
        return fname_r, fname_l


    def detect_stop(self, controls):
        stop = False
        if controls == None:
            return None, True
        return stop
    

if __name__ == '__main__':

    sub = YuMiSubscriber()
    sub.start()
    opt = Options()
    controller = XboxController()
    name = "pi_6"
    KT = Kinesthetic_Trainer(sub,opt,name,controller)
    KT.start_motion(True)

