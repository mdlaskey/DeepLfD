import sys, os, time, cv2, argparse
import tty, termios
import numpy as np
import IPython
from alan.control import YuMiRobot, YuMiState
from alan.control.yumi_subscriber import YuMiSubscriber

from deep_lfd.core.common import Common
from deep_lfd.rgbd.registration_ps import RegPS
from deep_lfd.rgbd.bincam_2D import BinaryCamera



###############CHANGGE FOR DIFFERENT PRIMITIVES##########################
from deep_lfd.p_pi.p_grasp_rss.options import Grasp_Options as Options 
from 
#from tensor.net_grasp import Net_Grasp as Net 
#########################################################################

#Common decorator that checks for override, else throws AssertionError
def overrides(super_class):
    def overrider(method):
        assert(method.__name__ in dir(super_class))
        return method
    return overrider

class Grasp_COM(Common):

    @overrides(Common)

    def __init__(self):

        self.Options = Options()

        self.reg = RegWC(Options)
        self.var_path = self.Options.policies_dir

        yml_file = '/home/autolab/Workspace/jeff_working/dexnet_reorg/data/experiments/grasping_gym/cfg/default_lfd.yaml'
        cfg = YamlConfig(yml_file)
        self.grasp_state = SegmentationBasedGraspState(cfg)
      
        self.constants = self.get_range()

    @overrides(Common)
    def execute_motion(self,yumi,theta=90.0):
        ''''
        '''
        self.yumi.left.close_gripper()
        self.add_z_offset(yumi,-0.19,arm = 'LEFT')



    @overrides(Common)
    def eval_policy(self,state):
        netn = Net(self.Options)
        sess = netn.load(var_path=self.var_path)
        outval = netn.output(sess, state,channels=1)
        sess.close()
        netn.clean_up()

        pos = self.rescale(outval)
        print "PREDICTED CORRECTION ", pos

        #convert to robot frame
        pos = self.reg.pixel_to_robot(pos[0:2])
        return pos,0

    @overrides(Common)
    def go_to_initial_state(self,yumi):
        #Takes arm out of camera field of view to record current state of the enviroment
        state = YuMiState([-44.83, -84.64, 20.15, 95.50, 82.85, 82.52, 34.56])
        yumi.left.goto_state(state)

    @overrides(Common)
      #Common
    def save_recording(self,recording):
        """  
        Saves the recoring to the specified file

        Paramters
        ---------
        recording: list 
            The recording of the label point shoud be a list of images and labels

        """
      
        
        name = self.next_rollout(rollouts)
        path = self.Options.sup_dir + name + '/'

        print "Saving to " + path + "..."

    
        os.makedirs(path)

        rollout_deltas_file = open(path + "net_deltas.txt", 'a+')

        if not os.path.exists(self.Options.originals_dir):
            os.makedirs(self.Options.originals_dir)

        if not os.path.exists(self.Options.binaries_dir):
            os.makedirs(self.Options.binaries_dir)

        if not os.path.exists(self.Options.depth_dir):
            os.makedirs(self.Options.binaries_dir)

        print "Saving raw frames to " + self.Options.originals_dir + "..."
        print "Saving binaries to " + self.Options.binaries_dir + "..."

        i = 0
        for frames, deltas in recording:
            filename = name + "_frame_" + str(i) + ".npy"

            [c_im,d_img,thumb_img] = frames


            rollout_deltas_file.write(filename + list2str(deltas))
           
            c_im.save(self.Options.originals_dir+filename)
            d_img.save(self.Options.depth_dir+filename)
            thumb_img.save(self.Options.binaries_dir+filenam)
        
            i += 1

        rollout_deltas_file.close()

        print "Done saving."
    def get_cp(self,yumi):
        self.go_to_initial_state(yumi)
        return yumi.left.get_pose()

    def move_to_pose(self,yumi,posit,rot):
        yumi.left.goto_pose_delta(posit)
        #yumi.right.goto_pose_delta(np.zeros(3), rot_delta=[0.0,0.0,rot])
        yumi.left.goto_pose_delta(np.zeros(3), [0.0,0.0,rot])

        self.add_z_offset(yumi,posit[3],arm = 'LEFT')

    def robot_to_pixel(self,pos):

        return reg.robot_to_pixel(pos,self.intrs)

    def pixel_to_robot(self,pos):

        pos_camera = [pos[0],pos[1],self.depth[pos[0],pos[1]]]

        return reg.robot_to_pixel(pos_camera,self.intrs)


    def get_grasp_state(self,prime_sense):

        color_im,d_img,ir_img = ps.frames()
        median_depth = ps.median_depth(0)
        intrs = ps.ir_intrinsics

        obj_img = grasp_state.get_grasp_state(color_im,d_img,intrs)

        self.depth = ob_dect.depth_thumbnail
        self.intrs = ob_dect.cropped_ir_intrinsics

        return [color_im,d_img,thumb_img]





if __name__ == '__main__':
    options = Options()
    # sub = YuMiSubscriber()
    # sub.start()

    # while True:
    #     timeLeft, pose_l = sub.left.get_pose()
    #     print pose_l.euler_angles

    yumi = YuMiRobot()
    com = Grasp_COM()

    com.go_to_initial_state(yumi)
