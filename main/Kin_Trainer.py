'''
This script is design to train Kinesthic polices 
From The YuMi in Lead Through Mode
Author: Michael Laskey

'''

from alan.control import YuMiConstants as YMC
from alan.control.yumi_subscriber import YuMiSubscriber
from deep_lfd.control.xbox_controller import XboxController
import os
import IPython
import numpy as np

import logging
from time import sleep
from deep_lfd.core.k_trainer import Kinesthetic_Trainer

#############CHANGE HERE TO TRAIN A NEW PRIMITIVE##############
from deep_lfd.k_pi.k_cap.options import Cap_Options as Options



if __name__ == '__main__':

    sub = YuMiSubscriber()
    sub.start()
    opt = Options()
    controller = XboxController()
    name = "pi_2"
    KT = Kinesthetic_Trainer(sub,opt,name,controller)
    KT.start_motion(True)

