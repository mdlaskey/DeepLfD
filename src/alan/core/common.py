import sys, os, time, cv2, argparse
import tty, termios
sys.path.append(sys.path[0] + "/../../../deps/gripper/")
from alan.rgbd.bincam_2D import BinaryCamera
import alan.database.functions as db
import numpy as np
import IPython
from alan.control import YuMiRobot, YuMiState
from alan.rgbd.registration_wc import RegWC
#overwrite execute_motion, error_handler, go_to_initial_state.

def list2str(deltas):
    label = " "
    for i in range(len(deltas)):
        label = label+str(deltas[i])+" "

    label = label+"\n"
    return label

MM_TO_M = 0.001

class Common:   

    def __init__(self,Options,train=False):
        self.Options = Options()
        self.reg = RegWC(Options)
        if(not train):
            self.net = net.NetAmazon()
            self.sess =self.net.load(var_path=Options.policies_dir+'amazon_net_09-22-2016_14h18m45s.ckpt')
        self.constants = self.get_range()

    #Common decorator that checks for override, else throws AssertionError
    def overrides(super_class):
        def overrider(method):
            assert(method.__name__ in dir(super_class))
            return method
        return overrider


    def rescale(self,deltas):

        deltas[0] = float(deltas[0])
        deltas[1] = float(deltas[1])
        deltas[2] = float(deltas[2])
        deltas[0] = self.constants[0]*deltas[0]+self.constants[2]
        deltas[1] = self.constants[1]*deltas[1]+self.constants[3]
        deltas[2] = (deltas[2]+1)*((self.Options.ROT_MAX - self.Options.ROT_MIN)/2)+self.Options.ROT_MIN
        return deltas

    def get_range(self,reg):
        low_bound = np.array([self.Options.X_LOWER_BOUND,self.Options.Y_LOWER_BOUND])
        up_bound = np.array([self.Options.X_UPPER_BOUND,self.Options.Y_UPPER_BOUND])

        #Convert to Pixels
        low_bound = self.reg.robot_to_pixel(low_bound)
        up_bound = self.reg.robot_to_pixel(up_bound)

        x_mid_range = (up_bound[0] - low_bound[0])/2.0
        y_mid_range = (up_bound[1] - low_bound[1])/2.0

        x_center = low_bound[0] + x_mid_range
        y_center = low_bound[1] + y_mid_range
        
        
        return [x_mid_range,y_mid_range,x_center,y_center]

    #This is common to everyone
    def add_z_offset(self,yumi, z, arm = 'RIGHT'):
        c_p = np.zeros(3)

        c_p[2] = z
        if(arm == 'RIGHT'):
            yumi.right.goto_pose_delta(c_p)
        elif(arm == 'LEFT'):
            yumi.left.goto_pose_delta(c_p)

    #Common But override
    def execute_motion(self,yumi,theta=90.0):
        # Go Up
        yumi.set_v(200.0)
        self.add_z_offset(yumi,-0.08)

        #Push
        self.push(yumi,0.20,theta)
        #Go up
        self.add_z_offset(yumi,0.2)
        yumi.set_v(1500)
    
    def move_to_pose(self,yumi,posit,rot):
        yumi.right.goto_pose_delta(posit)
        yumi.right.goto_pose_delta(np.zeros(3),rot_delta=[0.0,0.0,rot])


    #Common but override
    def error_handler(self,yumi):
        add_z_offset(yumi,0.15)
        go_to_initial_state(yumi)

    #Common
    def rotate_gripper(self,yumi=None,theta=90.0,pose = None):
        theta = np.deg2rad(theta)

        if(pose == None):
            c_p = yumi.right.get_pose()
        else:
            c_p = pose

        rot_z = np.array([[np.cos(theta),-np.sin(theta),0.0],[np.sin(theta),np.cos(theta),0.0],[0.0,0.0,1.0]])
        c_p._rotation = np.matmul(rot_z,c_p.rotation)

        if(pose == None):
            yumi.right.goto_pose(c_p)
        else:
            return pose

    #Common but override
    def go_to_initial_state(self,yumi):
        #Takes arm out of camera field of view to record current state of the enviroment
        state = YuMiState([51.16, -99.4, 21.57, -107.19, 84.11, 94.61, -36.00])
        yumi.right.goto_state(state)
        #Open Gripper


    def eval_label(self,state):
        pos = self.rescale(state)
        

        #convert to robot frame 
        pos_p = self.reg.pixel_to_robot(pos[0:2])

        label = np.array([pos_p[0],pos_p[1],pos[2]])
        #print "PREDICTED CORRECTION ", pos_p
        #print "PREDICTED POSE ", pos[2]
        return label

    def eval_policy(self,state):
        outval = self.net.output(self.sess, state,channels=1)
        pos = self.rescale(outval)
        print "PREDICTED CORRECTION ", pos
        #print "PREDICTED POSE ", pos[2]

        #convert to robot frame 
        pos_p = self.reg.pixel_to_robot(pos[0:2])

        label = np.array([pos_p[0],pos_p[1],pos[2]])
        
        return label

    def is_rot_bound(self,theta_n):
        if(theta_n > self.Options.ROT_MAX or theta_n < self.Options.ROT_MIN):
            return False
        else: 
            return True 

    #Common
    def bound_pose(self,pose,theta,delta_state):
        pose.position[0] += delta_state[0]
        pose.position[1] += delta_state[1]


        if(pose.position[0] < self.Options.X_LOWER_BOUND):
            pose.position[0] = self.Options.X_LOWER_BOUND
        elif(pose.position[0] > self.Options.X_UPPER_BOUND):
            pose.position[0] = self.Options.X_UPPER_BOUND

        if(pose.position[1] < self.Options.Y_LOWER_BOUND):
            pose.position[1] = self.Options.Y_LOWER_BOUND
        elif(pose.position[1] > self.Options.Y_UPPER_BOUND):
            pose.position[1] = self.Options.Y_UPPER_BOUND

        #TODO: add rotation bound
        if(not theta == None):
            if(theta < self.Options.ROT_MIN):
                theta = self.Options.ROT_MIN
            elif(theta > self.Options.ROT_MAX):
                theta = self.Options.ROT_MAX
            return pose,theta

        # print pose

        return pose

    #Common
    def apply_deltas(self,delta_state,pose,grip_open,theta):
        """
            Get current states and apply given deltas
            Handle max and min states as well
        """
        g_open = grip_open
        if delta_state[3] != 0:
            g_open = delta_state[3]
        pose,theta = self.bound_pose(pose,theta, delta_state)
        theta = theta + delta_state[4]
        return pose, g_open,theta

    #Common
    def next_rollout(self,rollouts=False):
            """
            :return: the String name of the next new potential rollout
                    (i.e. do not overwrite another rollout)
            """
            i = 0
            if rollouts:
                prefix = self.Options.rollouts_dir
            else:
                prefix = self.Options.sup_dir

            path = prefix + 'rollout'+str(i) + "/"
            print path

            while os.path.exists(path):
                i += 1
                path = prefix + 'rollout'+str(i) + "/"
            return 'rollout' + str(i)

    #Common
    def save_recording(self,recording,bc, rollouts=False):
        """  File "/home/autolab/Libraries/miniconda2/envs/alan_michael/lib/python2.7/multiprocessing/process.py", line 258, in _bootstrap
        self.run()
      File "/home/autolab/Workspace/micha
            Save instance recordings and states by writing filename and corresponding state
            to states files and writing images to ma  File "/home/autolab/Libraries/miniconda2/envs/alan_michael/lib/python2.7/multiprocessing/process.py", line 258, in _bootstrap
        self.run()
      File "/home/autolab/Workspace/micha  File "/home/autolab/Libraries/miniconda2/envs/alan_michael/lib/python2.7/multiprocessing/process.py", line 258, in _bootstrap
        self.run()
      File "/home/autolab/Workspace/michaster frames dir and appropriate rollout dir.
            Clear recordings and states from memory when done writing
            :return  File "/home/autolab/Libraries/miniconda2/envs/alan_michael/lib/python2.7/multiprocessing/process.py", line 258, in _bootstrap
        self.run()
      File "/home/autolab/Workspace/micha:
        """

        if rollouts:
            name = self.next_rollout(rollouts)
            path = self.Options.rollouts_dir + name + '/'
        else:
            name = self.next_rollout(rollouts)
            path = self.Options.sup_dir + name + '/'

        print "Saving to " + path + "..."

    
        os.makedirs(path)

        rollout_deltas_file = open(path + "net_deltas.txt", 'a+')


        print "Saving raw frames to " + self.Options.originals_dir + "..."
        print "Saving binaries to " + self.Options.binaries_dir + "..."

        i = 0
        for frame, deltas in recording:
            filename = name + "_frame_" + str(i) + ".jpg"


            rollout_deltas_file.write(filename + list2str(deltas))

            db.writeData(frame,self.Options.originals_dir, name, i)
            db.writeData(frame,bc.apply_mask(frame), name, i)
            # cv2.imwrite(path + filename, frame)
            i += 1

        rollout_deltas_file.close()

        print "Done saving."