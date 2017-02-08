import sys, os, time, cv2, argparse
import tty, termios
import numpy as np
import IPython
from alan.control import YuMiRobot, YuMiState
from alan.control.yumi_subscriber import YuMiSubscriber

from deep_lfd.core.common import Common
from deep_lfd.rgbd.registration_ps import RegPS
from deep_lfd.rgbd.bincam_2D import BinaryCamera

from core import RigidTransform, YamlConfig
from dexnet.planning.grasp_planner import SegmentationBasedGraspState



###############CHANGGE FOR DIFFERENT PRIMITIVES##########################
from deep_lfd.p_pi.p_grasp_rss.options import Grasp_Options as Options 

from deep_lfd.tensor.nets.net_grasp import Net_Grasp as Net 
#########################################################################

#Common decorator that checks for override, else throws AssertionError
def overrides(super_class):
    def overrider(method):
        assert(method.__name__ in dir(super_class))
        return method
    return overrider

def list2str(deltas):
    label = " "
    for i in range(len(deltas)):
        label = label+str(deltas[i])+" "

    label = label+"\n"
    return label


class Grasp_COM(Common):

    @overrides(Common)

    def __init__(self):

        self.Options = Options()

        self.reg = RegPS()
        # self.var_path = self.Options.policies_dir+'grasp_net_01-31-2017_10h56m12s.ckpt'

        yml_file = '/home/autolab/Workspace/jeff_working/dexnet_reorg/data/experiments/grasping_gym/cfg/default_lfd.yaml'
        cfg = YamlConfig(yml_file)
        self.grasp_state = SegmentationBasedGraspState(cfg)
      
        self.constants = self.get_range()

        # self.netn = Net(self.Options)
        # self.sess = self.netn.load(var_path=self.var_path)

    @overrides(Common)
    def execute_motion(self,yumi,theta=90.0):
        ''''
        '''
        yumi.left.close_gripper()
        self.add_z_offset(yumi,0.20,arm = 'LEFT')

    @overrides(Common)
    def get_range(self):
        ''''
        Converts the bounding box specifed in robot pose, into the bounding
        box specifed in pixel space

        Returns
        -------
        list size 4
            First two elements specify the length of each range (x and y)
            Last two elementes specifiy the midpoint of each range


        '''

        low_bound = np.array([self.Options.LOWER_X_P_BOUNDS,self.Options.LOWER_Y_P_BOUNDS])
        up_bound = np.array([self.Options.UPPER_X_P_BOUNDS,self.Options.UPPER_Y_P_BOUNDS])

        x_mid_range = (up_bound[0] - low_bound[0])/2.0
        y_mid_range = (up_bound[1] - low_bound[1])/2.0

        x_center = low_bound[0] + x_mid_range
        y_center = low_bound[1] + y_mid_range
        
        
        return [x_mid_range,y_mid_range,x_center,y_center]

    @overrides(Common)
    def eval_policy(self,state):
        self.depth = state
        
        outval = self.netn.output(self.sess, state,channels=1)
        

        pos = self.rescale(outval)
        print "PREDICTED CORRECTION ", pos
        
        #convert to robot frame
        #pos_xy = self.pixel_to_robot(pos[0:2])
        #pose = np.array([pos_xy.x,pos_xy.y,pos[3]])
        pose = np.array([pos[0],pos[1],pos[3]])

        return pose,pos[2]

    @overrides(Common)
    def eval_label(self,state):

        pos = self.rescale(state)
        print "PREDICTED CORRECTION ", pos
        
        #convert to robot frame
        #pos_xy = self.pixel_to_robot(pos[0:2])
        pose = np.array([pos[0],pos[1],pos[3]])

        return pose,pos[2]

    @overrides(Common)
    def go_to_initial_state(self,yumi):
        #Takes arm out of camera field of view to record current state of the enviroment
        state = YuMiState([-64.83, -74.64, 0.0, 105.50, 77.85, 90.0, 45.56])
        yumi.left.goto_state(state)
        yumi.left.open_gripper()

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
        for frames,deltas in recording:
            [c_im,d_img,thumb_img] = frames
            if(self.check_data_size(d_img)):
                print "DATA NOT CORRECT"
                return
        
        name = self.next_rollout()
        path = self.Options.sup_dir + name + '/'

        print "Saving to " + path + "..."

  
        os.makedirs(path)

        rollout_deltas_file = open(path + "net_deltas.txt", 'a+')

        if not os.path.exists(self.Options.originals_dir):
            os.makedirs(self.Options.originals_dir)

        if not os.path.exists(self.Options.binaries_dir):
            os.makedirs(self.Options.binaries_dir)

        if not os.path.exists(self.Options.depth_dir):
            os.makedirs(self.Options.depth_dir)

        print "Saving raw frames to " + self.Options.originals_dir + "..."
        print "Saving binaries to " + self.Options.binaries_dir + "..."

        i = 0
        for frames, deltas in recording:
            filename = name + "_frame_" + str(i) + ".npy"

            filename_png = name + "_frame_" + str(i) + ".png"

            [c_im,d_img,thumb_img] = frames


            rollout_deltas_file.write(filename + list2str(deltas))
           
            c_im.save(self.Options.originals_dir+filename_png)
            d_img.save(self.Options.depth_dir+filename)
            thumb_img.save(self.Options.binaries_dir+filename)
        
            i += 1

        rollout_deltas_file.close()

        print "Done saving."

    def check_data_size(self,img):
        if(img.shape[0] == 200 and img.shape[1] == 200):
            return True
        else: 
            return False
    def get_cp(self,yumi):
        self.go_to_initial_state(yumi)
        return yumi.left.get_pose()

    def move_to_pose(self,yumi,posit,rot):

        x_y = np.array([posit[0],posit[1],0.0])
        yumi.left.goto_pose_delta(x_y)
        #yumi.right.goto_pose_delta(np.zeros(3), rot_delta=[0.0,0.0,rot])
        yumi.left.goto_pose_delta(np.zeros(3), [0.0,0.0,rot])

        self.add_z_offset(yumi,posit[2],arm = 'LEFT')

    def robot_to_pixel(self,pos):

        return self.reg.robot_to_pixel(pos,self.intrs)

    def pixel_to_robot(self,pos):

        pos_camera = np.array([pos[0],pos[1],self.depth[int(pos[0]),int(pos[1])]])

        return self.reg.pixel_to_robot(pos_camera,self.intrs)

    def check_data(self,rot,trans):
        if(self.Options.ROT_MIN > rot or self.Options.ROT_MAX < rot):
            return False

        if(self.Options.Z_MIN > trans or self.Options.Z_MAX < trans):
            return False

        return True


    def get_grasp_state(self,ps):

        color_im,d_img,ir_img = ps.frames()
        median_depth = ps.median_depth_img()
        intrs = ps.ir_intrinsics

        obj_img = self.grasp_state.get_grasp_state(color_im,d_img,intrs)
        if obj_img == None:
            return [None,None,None]

        self.depth = obj_img.depth_thumbnail
        self.intrs = obj_img.cropped_ir_intrinsics

        depth_im_seg_cropped = obj_img.depth_im
        color_im_seg = obj_img.color_im

        return [color_im_seg,d_img,depth_im_seg_cropped]





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
