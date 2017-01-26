''''
Class used to collect demonstrations from the YuMi in Lead-Through 
Mode using the Echo

Author : Michael Laskey
Modified by: Rishi Kapadia
'''

import os
import IPython
import numpy as np
import logging
from time import sleep

from alan.control import YuMiConstants as YMC
from alan.control.yumi_subscriber import YuMiSubscriber

import robot_logger as audio_logger

#############CHANGE HERE TO TRAIN A NEW PRIMITIVE##############
from deep_lfd.k_pi.k_echo.options import Echo_Options as Options


class Kinesthetic_Trainer:

    def __init__(self,sub,options,only_goal=False, init_state = False):
        '''
        Initialization class for Kinesthic Trainer 

        Parameters
        ----------
        sub : YuMiSubscriber
            Instance of YuMiScriber that is started 

        options : Options 
            Instance of Options class 

        only_goal : bool 
            Specifies whether or not to capture the goal state only (Defaults to False)

        init_state : bool
            Leave as False

        '''

        logging.getLogger().setLevel(YMC.LOGGING_LEVEL)

        self._sub = sub

        self.only_goal = only_goal
        self.init_state = init_state

        # will probably need to initialize these differently
        self._statesR = []
        self._statesL = []
        self._timingsR = []
        self._timingsL = []

        self.opt = options


    def init_name(self, name):
        '''
        Helper init function to create the recorded file

        Parameters
        ----------
        name : string
        '''
        self.name = name
        if not os.path.exists(self.opt.policies_dir):
            os.makedirs(self.opt.policies_dir)
        self.fname_r = self.opt.policies_dir+name+"R"
        self.fname_l = self.opt.policies_dir+name+"L"


    def start_motion(self, collect_timing=False):
        '''
        Starts recording the motions of the YuMi's Arms

        Parameters
        ----------
        collect_timing : bool
            Specifies whether to also record timestamps (Defaults False)
        '''

        low_pass = 250
        count = 0

        print "COLLECTING STARTED"

        while True:
            command = audio_logger.getDataCommand()
            stop = self.detect_stop(command)
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
        '''
        Reads the current joint angles of the YuMi arms
        and calls store functions to save values

        Parameters
        ----------
        collect_timing : bool
            Specifies whether to also record timestamps (Defaults False)
        '''
        timeLeft, pose_l = self._sub.left.get_state()
        timeRight, pose_r = self._sub.right.get_state()

        self.store_state(pose_r, pose_l)
        if (collect_timing == True):
            self.store_timing(timeLeft, timeRight)
            
        
    def store_state(self, stateR, stateL):
        '''
        Saves the current joint angles to the lists

        Parameters
        ----------
        statesR : YuMiState

        statesL : YuMiState

        '''
        self._statesR.append(stateR.joints)
        self._statesL.append(stateL.joints)

    def store_timing(self, timeLeft, timeRight):
        '''
        Saves the current timestamps to the designated lists

        Parameters
        ----------
        timeLeft : float

        timeRight : float

        '''
        self._timingsL.append(timeLeft)
        self._timingsR.append(timeRight)

    def save_trajectory(self):
        '''
        Saves the data to the specifed file

        '''

        if self.only_goal:
            # only store goal state
            np.save(self.fname_r, self._statesR[-1])
            np.save(self.fname_l, self._statesL[-1])

        else:
            np.save(self.fname_r, self._statesR)
            np.save(self.fname_l, self._statesL)

        print("Trajectories stored!")


    def detect_stop(self, command):
        '''
        Reads the current controls from the Echo and returns
        if the user wants to stop the recording

        Parameters
        ----------
        command : string

        Returns 
        -------
        bool 
            False if stop not recorded, True Otherwise

        '''
        if command == "stop" or command == "pause":
            audio_logger.log("Stopped")
            return True
        return False
    

    def start_loop(self, collect_timing=False):
        '''
        Restarts the Kinesthetic_Trainer motion recorder
        to record several path trajectories

        Parameters
        ----------
        collect_timing : bool
            Specifies whether to also record timestamps (Defaults False)

        '''

        iteration = 0
        base_name = "pi_"
        while True:
            command = audio_logger.getDataCommand()
            if command == "start" or command == "record":
                audio_logger.log("Recording")
                name = base_name + str(iteration)
                self.init_name(name)
                self.start_motion(collect_timing)
                iteration += 1
            elif command == "finish":
                audio_logger.log("All done! I've finished recording your trajectories.")
                break
            sleep(0.01)  # for stability
        return


if __name__ == '__main__':

    sub = YuMiSubscriber()
    sub.start()
    opt = Options()
    KT = Kinesthetic_Trainer(sub,opt)
    KT.start_loop(True)

