import sys, os, time, cv2, argparse
import tty, termios
sys.path.append(sys.path[0] + "/../../../deps/gripper/")
from alan.rgbd.bincam_2D import BinaryCamera
import numpy as np
import IPython
from alan.control import YuMiRobot, YuMiState
from alan.core.common import Common
from alan.p_rope_grab_R.options import Rope_GrabROptions as Options
from alan.rgbd.registration_wc import RegWC

sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')
#These are policy specific and need to be changed
from tensor import net_rope_grab as net

#Common decorator that checks for override, else throws AssertionError
def overrides(super_class):
    def overrider(method):
        assert(method.__name__ in dir(super_class))
        return method
    return overrider

class Rope_GrabRCOM(Common):

    @overrides(Common)
    def __init__(self,train=False):
        self.Options = Options()
        self.reg = RegWC(self.Options)
        if(not train):
            self.net = net.Net_Rope_Grab(self.Options)
            self.sess =self.net.load(var_path=self.Options.policies_dir+'grasp_net_10-31-2016_11h51m11s.ckpt')
        self.constants = self.get_range(self.reg)

    @overrides(Common)
    def eval_policy(self,state):
        outval = self.net.output(self.sess, state,channels=1)
        pos = self.rescale(outval)
        print "PREDICTED CORRECTION ", pos
        #print "PREDICTED POSE ", pos[2]

        #convert to robot frame 
        pos_p = self.reg.pixel_to_robot(pos[0:2])

        pos_n =  np.array([pos_p[0],pos_p[1]])
        rot = pos[2]
        
        return pos_n,rot
    def grasp(self,yumi,offset,theta):
        theta = np.deg2rad(theta)
        c_p = np.zeros(3)

        x = offset
        y = 0

        c_p[0] += x*np.cos(theta) - y*np.sin(theta)
        c_p[1] += x*np.sin(theta) + y*np.cos(theta)

        # c_p.position[0] = c_p.position[0]+offset
        yumi.right.goto_pose_delta(c_p)

    def check_collision(frame,pos,posit,reg,debug=True):
        #Check if in Collision
        pos_check = 1000*(self.cp.position + posit)

        p_p= reg.mm_to_pixel(pos_check)
        r_x,r_y,img = CC.findValidPlacement(frame,p_p[0],p_p[1])
        r_x,r_y = reg.pixel_to_mm(np.array([r_x,r_y]))

        if(debug):
            cv2.imshow('debug',img)
            cv2.waitKey(30)

        posit[0] = r_x*0.001-self.cp.position[0]
        posit[1] = r_y*0.001-self.cp.position[1]
        return posit

    @overrides(Common)
    def execute_motion(self,yumi,theta=90.0): #was execute_mot not execute_motion
        yumi.set_v(50.0)
        #go down
        self.add_z_offset(yumi,-0.09)
        #close gripper
        yumi.right.close_gripper()
        yumi.set_v(1500.0)

    @overrides(Common)
    def error_handler(self,yumi):
        add_z_offset(yumi,-0.15)
        go_to_initial_state(yumi)

    @overrides(Common)
    def go_to_initial_state(self,yumi):
        #Takes arm out of camera field of view to record current state of the enviroment
        state = YuMiState([51.16, -99.4, 21.57, -107.19, 84.11, 94.61, -36.00])
        yumi.right.goto_state(state)
        self.add_z_offset(yumi,-0.065)

        #Open Gripper
        yumi.right.open_gripper()


    def get_cp(self,yumi):
        self.go_to_initial_state(yumi)
        return yumi.right.get_pose()