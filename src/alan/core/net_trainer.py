'''
        A class used to train a neural network to predict (x,y,z,theta) pose
        Records the image of the current scene and the pose lable. Uses an Xbox Controller
        to signal when to save data. 

        Author: Michael Laskey 
'''


import sys
import tty, termios
from alan.rgbd.bincam_2D import BinaryCamera 
from alan.debug.ar_overlay import AR_Debug
import time, datetime, os, random, argparse
import cv2
import IPython
import numpy as np

class  Net_Trainer():

    def __init__(self,com,bincam,net_name,c,sub):
        """
            Init function for Net_Trainer 

            Parameters
            ----------
            com : Common Class for Policy 

            bincam : Camera Class for Webcam
                The camera should already have the webcam actived (i.e. bincam.open())

            net_name : String
                The name of the neural netwrok currently being controlled. If first neural_net
                displays a webcam image of the binary mask. Press ESC on the window to move forward


            c: Xbox Controller Class

            sub: Yumi Subscriber Class
                YuMi Subscrber must have start enabled (i.e. sub.start())

        """
        self.com = com
        self.b = bincam

        self.c = c 
        self.sub = sub
     
        self.bc = bincam
        self.net_name = net_name

        sampleFrame = self.bc.read_frame()

        if(net_name == 'neural_net_0/'):

            while (1):
                a = cv2.waitKey(30)
                if a == 1048603:
                    cv2.destroyWindow("camera")
                    break
                time.sleep(.005)       
                frame = self.bc.read_binary_frame()
                cv2.imshow("cam", frame)
                cv2.waitKey(30)

        
    def set_AR_markers(self,net_com):
        """
            Initialize the AR marker Class

            Parameters
            ----------
            net_com : Common Class for Policy 

        """
        self.ar_debug = AR_Debug(self.b,net_com)


    def get_initial_state(self,sample_iter):
        """
            Draw a state from the corresponding intial state distirbuion of sample_iter

            Parameters
            ----------
            sample_iter : int 
                Current iteration to be trained on 

        """
        # Plus 1 is only for Sammy folder (THIS IS AN ISSUE)
        self.ar_debug.get_initial_state(sample_iter)

    def collect_data_full(self):
        """
            Record the data images and (x,y,theta,z) pose of the YuMi

        """
        self.get_images()
        self.record_pose_full()

    def collect_data(self,arm = 'LEFT'):
        """
            Record the data images and (x,y) pose of the YuMi

            Parameters
            ----------
            arm: string
                Specifies which arm to train with (LEFT or RIGHT)

        """
        self.get_images()
        self.record_pose(arm)

    def get_images(self):
        """
            Saves colored images of the workspace, the number is specfied in the options file

        """
        self.frames = []

        #Clear Camera Buffer 
        for i in range(4):
            self.bc.read_color_frame()

        for i in range(self.com.Options.T):
            frame = self.bc.read_color_frame()
            self.frames.append(frame)

    def extract_angle(self,pose):
        """
            Extracts the correct rotation of the YuMi Gripper

            Parameters
            ----------
            pose : Yumi Pose

            Returns
            --------
            float
                The z roation of the YuMi Gripper in degrees

        """
        z = pose.euler_angles[2]
        rotation = z*180.0/np.pi
        return rotation

    def capture_state(self,use_binary = False):
        """
            Displays the webcam image and waits for the user to hit ESC on the XBox Controller
            to begin collecting data

            Parameters
            ----------
            use_binary : bool
                If set to true will display a binary mask, while false displays the color image

        """
        while True:
            update = self.c.getUpdates()
            if(use_binary):
                state = self.bc.read_binary_frame()
            else:
                state = self.bc.read_color_frame()
            cv2.imshow('state',state )
            cv2.waitKey(30)
            if update is None:
                break;



    def record_pose_full(self):
        """
            Records the (x,y,theta,z) Pose of the Current YuMi, which is used for learning 
            Function waits until Start is Pressed on the Xbox Controller and records pose

        """

        while True:
            update = self.c.getUpdates()
            if update is None:
                
                pose = self.sub.left.get_pose()
                if(pose == None):
                    raise Exception('YuMi Did Not Return a Pose')
                pose = pose[1]
                pose_t = pose.translation
                break;



        self.label = []

        pixels = self.com.reg.robot_to_pixel(pose_t[0:2])
        rotation = self.extract_angle(pose)

        self.label = [pixels[0], pixels[1],rotation,pose_t[2]]

        self.save_data(self.net_name)




    def record_pose(self,arm = 'LEFT'):
        """
            Records the (x,y) Pose of the Current YuMi, which is used for learning 

            Function waits until Start is Pressed on the Xbox Controller and records pose

            Parameters
            ----------
            arm: string
                Specifies which arm to train with (LEFT or RIGHT)

        """

        while True:
            update = self.c.getUpdates()
            if update == None:

                if(arm == 'LEFT'):
                    pose = self.sub.left.get_pose()
                elif(arm == 'RIGHT'):
                    pose = self.sub.right.get_pose()

                if(pose == None):
                    raise Exception('YuMi Did Not Return a Pose')

                pose = pose[1]
                pose_t = pose.translation
                break
          


        self.label = []

        pixels = self.com.reg.robot_to_pixel(pose_t[0:2])
        #rotation = self.extract_angle(pose)

        self.label = [pixels[0], pixels[1],0.0]

        self.save_data(self.net_name)

    def save_data(self,net_name):
        """
            Save data using the provided function path of net_name and options

            Parameters
            ----------
            net_name : String 
                The name of the neural network 

        """
        recording = []
        for i in range(len(self.frames)):
            recording.append([self.frames[i],self.label])

        self.com.save_recording(recording,self.b)

   



if __name__ == "__main__":
   

    print "Done."
