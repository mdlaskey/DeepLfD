import sys, os, time, cv2, argparse
import tty, termios
sys.path.append(sys.path[0] + "/../../../deps/gripper/")
from alan.rgbd.bincam_2D import BinaryCamera
import numpy as np
import IPython
from alan.core.common import Common
from alan.control import YuMiRobot, YuMiState
from alan.p_singulate_L import collisionChecker as CC
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')
#These are policy specific and need to be changed

from tensor import net_amazon as net
from alan.rgbd.registration_wc import RegWC
from alan.p_singulate_L.options import Singulate_LOptions as Options

#Common decorator that checks for override, else throws AssertionError
def overrides(super_class):
    def overrider(method):
        assert(method.__name__ in dir(super_class))
        return method
    return overrider

class Singulate_LCOM(Common):

    @overrides(Common)
    def __init__(self,train=False):
        self.Options = Options()
        self.reg = RegWC(Options)
        self.var_path = self.Options.policies_dir+'amazon_net_10-11-2016_11h55m07s.ckpt'
        # if(not train):
        #     self.net = net.NetAmazon()
        #     #self.sess =self.net.load(var_path=self.Options.policies_dir+'amazon_net_10-11-2016_11h55m07s.ckpt')
        self.constants = self.get_range(self.reg)

    @overrides(Common)
    def execute_motion(self,yumi,theta=-90.0):
        # Go Up
<<<<<<< HEAD
        yumi.set_v(500.0)
        self.add_z_offset(yumi,-0.08,arm='LEFT')
=======
        #yumi.set_v(400.0)
        self.add_z_offset(yumi,-0.18,arm='LEFT')
>>>>>>> 24c7c70464ccd25a4d233494a65a81381623f112

        #Push
        self.push(yumi,0.15,theta)
        #Go up
        self.add_z_offset(yumi,0.2,arm='LEFT')
        yumi.set_v(1500)
        self.go_to_initial_state(yumi)

    #Common but override
    @overrides(Common)
    def error_handler(self,yumi):
        add_z_offset(yumi,0.15)
        go_to_initial_state(yumi)


    @overrides(Common)
    def eval_policy(self,state):
        self.net = net.NetAmazon()
        self.sess =self.net.load(var_path=self.var_path)
        outval = self.net.output(self.sess, state,channels=1)
        self.sess.close()
        self.net.clean_up()
        #IPython.embed()
        pos_s = self.rescale(outval)
        print "PREDICTED CORRECTION ", pos_s
        #IPython.embed()
        #convert to robot frame
        pos = self.reg.pixel_to_robot(pos_s[0:2])
     
        return pos, 0.0


    @overrides(Common)
    def move_to_pose(self,yumi,posit,rot):
        yumi.left.goto_pose_delta(posit)
        yumi.left.goto_pose_delta(np.zeros(3), [0.0,0.0,rot])

    #Singulation Only
    def push(self,yumi,offset,theta):
        theta = np.deg2rad(theta)
        c_p = np.zeros(3)

        x = offset
        y = 0

        c_p[0] += x*np.cos(theta) - y*np.sin(theta)
        c_p[1] += x*np.sin(theta) + y*np.cos(theta)

        # c_p.position[0] = c_p.position[0]+offset
        yumi.left.goto_pose_delta(c_p)



    def check_collision(self,frame,pos,posit,reg,debug=False):
        #Check if in Collision

        pos_check = (pos.position + posit)
        p_c = pos_check[0:2]

        p_p= reg.robot_to_pixel(p_c)
        r_x,r_y,u_img,img = CC.findValidPlacement(frame,p_p[0],p_p[1])
        r_x,r_y = reg.pixel_to_robot(np.array([r_x,r_y]))

        if(debug):
            cv2.imshow('debug',img)
            cv2.waitKey(30)

        posit[0] = r_x-pos.position[0]
        posit[1] = r_y-pos.position[1]
        return posit

    def get_cp(self,yumi):
        self.go_to_initial_state(yumi)
        return yumi.left.get_pose()


    def go_to_initial_state(self,yumi):
        #Takes arm out of camera field of view to record current state of the enviroment
       # yumi.left.close_gripper()
        state = YuMiState([-41.83, -94.64, 26.15, 93.50, 102.85, 86.52, 20.56])
        #state = YuMiState([-51.16, -99.4, 21.57, 107.19, 84.11, 94.61, 36.00])
        #state = YuMiState([-51.16, -99.4, 21.57, 65.19, 84.11, 94.61, 36.00])
        yumi.left.goto_state(state)
