''''
Class used to collect demonstrations from the YuMi in Lead-Through
Mode

Author : Michael Laskey
'''

import os, logging
import IPython
import numpy as np
from time import sleep
from core import YamlConfig
from perception import OpenCVCameraSensor
from yumipy import YuMiSubscriber, YuMiRobot
from yumi_teleop import DemoWrapper, TeleopExperimentLogger, QueueEventsSub
from core import DataStreamSyncer, DataStreamRecorder
from deep_lfd.control import XboxController

class Kinesthetic_Trainer:

    def __init__(self, options, controller, args, only_goal=False):
        '''
        Initialization class for Kinesthic Trainer

        Parameters
        ----------
        options : Options
            Instance of Options class

        controller : XboxController
            Instance of XboxController class

        args : parser arguments
            Parsed arguments from Kin_Trainer

        only_goal : bool TODO: Implement
            Specifies whether or not to capture the goal state only (Defaults to False)
        '''
        logging.getLogger().setLevel(logging.INFO)

        self.opt = options
        self.controller = controller
        self.only_goal = only_goal
        self.cfg_path = args.config_path
        self.cfg = YamlConfig(self.cfg_path)

        self.demo_name = args.demo_name
        self.demo_filename = os.path.join(self.cfg['demo_path'], '{0}.py'.format(self.demo_name))
        if not os.path.exists(self.demo_filename):
            raise ValueError("Demonstration file path not found! Tried {0}".format(self.demo_filename))

        # setting up logger
        self.logger = TeleopExperimentLogger(self.cfg['output_path'], self.cfg['supervisor'])
        _ = raw_input("Please start server so setup motions can be performed. Click [ENTER] to confirm.")
        self.yumi = YuMiRobot()

        demo_obj = DemoWrapper.load(self.demo_filename, self.yumi)
        logging.info("Performing setup motions...")
        demo_obj.setup()
        logging.info("Done!")
        try:
            self.yumi.stop()
        except Exception:
            pass

        self.ysub = YuMiSubscriber()
        self.ysub.start()

        self.datas = {}
        self.all_datas = []

        cache_path, save_every = self.cfg['cache_path'], self.cfg['save_every']

        if self.cfg['data_srcs']['webcam']['use']:
            self.webcam = OpenCVCameraSensor(self.cfg['data_srcs']['webcam']['n'])
            self.webcam.start()
            self.datas['webcam'] = DataStreamRecorder('webcam', self.webcam.frames, cache_path=cache_path, save_every=save_every)
            self.all_datas.append(self.datas['webcam'])

        self.datas['poses'] = {
            'left': DataStreamRecorder('poses_left', self.ysub.left.get_pose, cache_path=cache_path, save_every=save_every),
            'right': DataStreamRecorder('poses_right', self.ysub.right.get_pose, cache_path=cache_path, save_every=save_every)
        }
        self.datas['states'] = {
            'left': DataStreamRecorder('states_left', self.ysub.left.get_state, cache_path=cache_path, save_every=save_every),
            'right': DataStreamRecorder('states_right', self.ysub.right.get_state, cache_path=cache_path, save_every=save_every)
        }
        self.datas['torques'] = {
            'left': DataStreamRecorder('torques_left', self.ysub.left.get_pose, cache_path=cache_path, save_every=save_every),
            'right': DataStreamRecorder('torques_right', self.ysub.right.get_pose, cache_path=cache_path, save_every=save_every)
        }

        self.grippers_bool = {
            'left': QueueEventsSub(),
            'right': QueueEventsSub()
        }

        self.datas['grippers_bool'] = {
            'left': DataStreamRecorder('grippers_bool_left', self.grippers_bool['left'].get_event, cache_path=cache_path, save_every=save_every),
            'right': DataStreamRecorder('grippers_bool_right', self.grippers_bool['right'].get_event, cache_path=cache_path, save_every=save_every)
        }

        self.all_datas.extend([
            self.datas['grippers_bool']['left'],
            self.datas['grippers_bool']['right'],
            self.datas['poses']['left'],
            self.datas['poses']['right'],
            self.datas['states']['left'],
            self.datas['states']['right'],
            self.datas['torques']['left'],
            self.datas['torques']['right']
        ])

        self.syncer = DataStreamSyncer(self.all_datas, self.cfg['fps'])
        self.syncer.start()
        logging.info("Waiting for initial flush...")
        sleep(3)
        self.syncer.pause()
        self.syncer.flush()
        logging.info("Done!")

    def _stop(self):
        self.syncer.stop()
        self.ysub.stop()
        try:
            self.webcam.stop()
        except Exception:
            pass
        print 'hello'

    def start_motion(self, collect_timing=False):
        '''
        Starts recording the moitons of the YuMi's Arms

        Parameters
        ----------
        collect_timing : bool #TODO: Implement
            Specifies whether to also record timestamps (Defaults False)
        '''
        _ = raw_input("Please stop server and ready demonstration.\nClick [ENTER] to begin data collection.")
        logging.info("Collection started!")

        self.syncer.resume(reset_time=True)
        last_controls = self.controller.getUpdates()
        while True:
            controls = self.controller.getUpdates()
            if controls == None: # stopping recording
                logging.info("Collection stopped!")
                self.syncer.pause()
                self.logger.save_demo_data(self.demo_name,
                                           self.cfg['supervisor'],
                                           self.demo_filename,
                                           self.cfg_path,
                                           self.all_datas,
                                           self.cfg['fps'])
                self._stop()
                break
            button_downs = np.logical_and(np.logical_xor(last_controls, controls), controls)
            if True in button_downs[2:]: # log gripper event
                if controls[2]:
                    self.grippers_bool['left'].put_event('close_gripper')
                elif controls[3]:
                    self.grippers_bool['left'].put_event('open_gripper')
                elif controls[4]:
                    self.grippers_bool['right'].put_event('close_gripper')
                elif controls[5]:
                    self.grippers_bool['right'].put_event('open_gripper')

            last_controls = controls