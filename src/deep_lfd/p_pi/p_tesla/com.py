'''
Common class for singulation policy

Author: Michael Laskey


'''
import sys, os, time, cv2, argparse
import tty, termios
from alan.rgbd.bincam_2D import BinaryCamera
import numpy as np
import IPython

from alan.control import YuMiRobot, YuMiState

#These are policy specific and need to be changed
from deep_lfd.core.common import Common
from deep_lfd.p_pi.p_tesla import collisionChecker as CC
from deep_lfd.tensor.nets.net_tesla import Net_Tesla as Net 
from deep_lfd.rgbd.registration_wc import RegWC
from deep_lfd.p_pi.p_tesla.options import Tesla_Options as Options

#Common decorator that checks for override, else throws AssertionError
def overrides(super_class):
    def overrider(method):
        assert(method.__name__ in dir(super_class))
        return method
    return overrider

class Tesla_COM(Common):

    @overrides(Common)
    def __init__(self,train=False):
        self.Options = Options()

        self.target_pose = None
        self.cp = None

        self.reg = RegWC(self.Options)
        IPython.embed()
        self.var_path=self.Options.policies_dir+'tesla_net_12-11-2016_20h15m42s.ckpt'

        self.constants = self.get_range()

    @overrides(Common)
    def execute_motion(self,yumi,theta=90.0):
        '''
        Execute the push motion at the current pose of the close_gripper
        if theta is spec

        Paramters
        ---------
        yumi : A instantiated YuMi Robot
            
        theta : float
            The degree for which the paddle to push (90.0)

        '''
        # Go Up
        self.add_z_offset(yumi,-0.09)

        #Push
        self.push(yumi,0.15,theta)

        #Go up
        self.add_z_offset(yumi,0.2)
        yumi.set_v(1500)
        self.go_to_initial_state(yumi)

    @overrides(Common)
    def eval_policy(self,state,debug = False):
        ''' 
        Evaulate the current neural network policy
        Also check if the policy is in collsion

        Paramters
        ---------
        frame : (WxHx1) shape numpy array
            A binary image of the workspace

        debug : bool
            True displays the output of collsion checker

        Returns
        -------
        (2,) shape numpy array
            The x,y position where to push (in robot coordinates)

        float
            The rotation of the paddle (defualted to 0)

        '''

        print 'Evaulate Policy'

        #####Greying Out Box Zone#####
        cv2.imshow('image state',state)
        cv2.waitKey(30)
       
        netn = Net(self.Options)
        sess = netn.load(var_path=self.var_path)
        outval = netn.output(sess, state,channels=1)
        sess.close()
        netn.clean_up()

        pos = self.rescale(outval)
        pos[2] = 0.0
        print "PREDICTED CORRECTION ", pos

        #Check for collsion
        pos,img = CC.findValidPlacement(state,pos)



        print "Collsion Fix Point ", pos

        #convert to robot frame
        pos = self.reg.pixel_to_robot(pos[0:2])

        return pos,0

    def get_angle(self,cur_pos,tar_pose):
        vec = tar_pose - cur_pos
        vec = vec/LA.norm(vec)

        theta = np.tan2(vec[1],vec[0])*180/math.pi

        return theta

    #Singulation Only
    def push(self,yumi,offset,theta):
        theta = np.deg2rad(theta)
        c_p = np.zeros(3)

        x = offset
        y = 0

        c_p[0] += x*np.cos(theta) - y*np.sin(theta)
        c_p[1] += x*np.sin(theta) + y*np.cos(theta)

        # c_p.position[0] = c_p.position[0]+offset
        yumi.right.goto_pose_delta(c_p)



    def check_collision(self,frame,posit,debug=False):
        ''' 
        Check if a collision can be caused by the current pose
        If a collison is possible then modifies the postion to be not 
        in collision

        Paramters
        ---------
        frame : (WxHx1) shape numpy array
            A binary image of the workspace

        posit : (3,) shape numpy array
            The delta change in (x,y,z) position

        '''

        pos_check = (self.cp.position + posit)
        p_c = pos_check[0:2]

        p_p= self.reg.robot_to_pixel(p_c)
        r_x,r_y,u_img,img = CC.findValidPlacement(frame,p_p)
        r_x,r_y = reg.pixel_to_robot(np.array([r_x,r_y]))

        if(debug):
            cv2.imshow('debug',img)
            cv2.waitKey(30)

        posit[0] = r_x-pos.position[0]
        posit[1] = r_y-pos.position[1]
        return posit



    def get_cp(self,yumi):
        self.go_to_initial_state(yumi)
        self.cp = yumi.right.get_pose()
        return self.cp


    def go_to_initial_state(self,yumi):
        #Takes arm out of camera field of view to record current state of the enviroment
        yumi.right.close_gripper()
        state = YuMiState([51.16, -99.4, 21.57, -107.19, 84.11, 94.61, -36.00])
        yumi.right.goto_state(state)
