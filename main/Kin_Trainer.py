'''
This script is design to train Kinesthic polices
From The YuMi in Lead Through Mode
Author: Michael Laskey

'''
import argparse, logging
from deep_lfd.control import XboxController
from deep_lfd.core.k_trainer import Kinesthetic_Trainer

#############CHANGE HERE TO TRAIN A NEW PRIMITIVE##############
from deep_lfd.k_pi.k_cap.options import Cap_Options as Options

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser(description='Kinesthetic Trainer')
    parser.add_argument('-c', '--config_path', type=str, default='cfg/demo_config.yaml', help='path to config file')
    parser.add_argument('-d', '--demo_name', type=str, help='name of desired demonstration task to train')
    args = parser.parse_args()

    opt = Options()
    # controller = XboxController()
    controller = None

    KT = Kinesthetic_Trainer(opt, controller, args)
    KT.start_motion(True)
