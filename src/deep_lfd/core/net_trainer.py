'''
        A class used to train a neural network to predict (x,y,z,theta) pose
        Records the image of the current scene and the pose lable. Uses an Xbox Controller
        to signal when to save data. 

        Author: Michael Laskey
        Modified by: Rishi Kapadia
'''


import sys
import tty, termios
from deep_lfd.rgbd.bincam_2D import BinaryCamera 
from deep_lfd.debug.ar_overlay import AR_Debug
import time, datetime, os, random, argparse
import cv2
import pygame
import IPython
import numpy as np

import robot_logger as audio_logger

from visualization import Visualizer2D as vis2d
class  Net_Trainer():

    def __init__(self,com,net_name,c,sub,bincam = None, depthcam = None, use_audio_input = True, use_audio_output = False, experiment_id=-1):
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

            use_audio_input: Whether to use the Echo as input and speakers for output, or a keyboard button
            use_audio_output: Whether to use the speakers for output, or the GUI

        """
        self.com = com
        
        self.c = c 
        self.sub = sub
     
        self.net_name = net_name

        self.use_audio_input = use_audio_input
        self.use_audio_output = use_audio_output
        self.success = False
        self.experiment_id = experiment_id

        # if not self.use_audio_output:
        #     app = wx.App(False)
        #     frame = wx.Frame(None, wx.ID_ANY, "Experiments", size=(300,200))
        #     self.dialogue_gui = wx.StaticText(frame, wx.ID_ANY, label="Starting demonstration", style=wx.ALIGN_CENTER)
        #     frame.Show(True)
        #     app.MainLoop()
        

        if(not depthcam == None):
            self.dc = depthcam
        elif(not bincam == None):
            self.bc = bincam
            sampleFrame = self.bc.read_frame()
        else: 
            raise Exception('No Camera model specified')

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

        if(self.com.Options.SENSOR == 'BINCAM'):
            #Clear Camera Buffer 
            for i in range(4):
                self.bc.read_color_frame()

            for i in range(self.com.Options.T):
                frame = self.bc.read_color_frame()
                self.frames.append(frame)
        else:
          
            for i in range(self.com.Options.T):
                color_im,d_img,thumb_img = self.com.get_grasp_state(self.dc)
                self.frames.append([color_im,d_img,thumb_img])


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
        # Step 1
        # self.publish_output("Please place the object in the workspace.")

        while True:
            message = ""
            if self.success:
                message = "Success! "
                self.success = False
                self.log_to_file("Success")
            else:
                self.log_to_file("Init")
            update = self.do_io(message + "Please place the object in the workspace.")
            # update = self.get_input()

            if(self.com.Options.SENSOR == 'BINCAM'):
                if(use_binary):
                    state = self.bc.read_binary_frame()
                else:
                    state = self.bc.read_color_frame()
                cv2.imshow('state',state )
                cv2.waitKey(30)
            elif(self.com.Options.SENSOR == 'PRIMESENSE'): 

                color_im,d_img,thumb_img = self.com.get_grasp_state(self.dc)
                #cv2.imshow('state',thumb_img.data )
                #vis2d.show()

            if update:
                break
        return



    def record_pose_full(self):
        """
            Records the (x,y,theta,z) Pose of the Current YuMi, which is used for learning 
            Function waits until Start is Pressed on the Xbox Controller and records pose

        """
        # Step 2
        terminate = False
        i = 0
        # self.publish_output("You may now guide my arm.")
        
        while not terminate:
            if i == 0:
                update = self.do_io("You may now guide my arm.")
            i += 1
            # update = self.get_input()
            if update:
                #clear buffer 
                for i in range(5):
                    pose = self.sub.left.get_pose()
                if(pose == None):
                    raise Exception('YuMi Did Not Return a Pose')
                pose = pose[1]
                pose_t = pose.translation

                rotation = self.extract_angle(pose)
                translation = pose_t[2]
                if(self.com.check_data(rotation,translation)):
                    terminate = True
                    # self.publish_output("Success!")
                    self.success = True
                    time.sleep(1) # delay to allow Echo to speak, or user to read screen
                else: 
                    self.log_to_file("Failure")
                    message = ""
                    if translation > self.com.Options.Z_MAX:
                        message += " The gripper is too high."
                    elif translation < self.com.Options.Z_MIN:
                        message += " The gripper is too low."
                    elif rotation < self.com.Options.ROT_MIN:
                        message += " The gripper needs to be rotated."
                    elif rotation > self.com.Options.ROT_MAX:
                        message += " The gripper needs to be rotated."
                    
                    # self.publish_output("Failed to re cord!" + message, "Failed to record!" + message)
                    update = self.do_io("Failed to record!" + message)
                    # For debugging clockwise/ccw. Comment out below!
                    # print "INCORRECT LABELS "
                    # print "ROTATION ",rotation
                    # print "Z AXIS ", translation

        self.label = []

        pixels = self.com.robot_to_pixel(pose_t)
        

        self.label = [pixels.x, pixels.y,rotation,pose_t[2]]

        if(pixels.x < 0.0 or pixels.y < 0.0):
            print "ROBOT POSE ", pose_t
            # raise Exception('DATA NOT VALID')
        
        self.save_data(self.net_name)
        return


    # def get_pose_full(self):
    #     """
    #         Records the (x,y,theta,z) Pose of the Current YuMi, which is used for learning 
    #         Function waits until Start is Pressed on the Xbox Controller and records pose

    #     """
    #     terminate = False
    #     while not terminate:
    #         has_update = False
    #         if self.use_audio:
    #             update = self.detect_echo_record()
    #             if update:
    #                 has_update = True
    #         else:
    #             update = self.c.getUpdates()
    #             if update == None:
    #                 has_update = True
    #         if has_update:
                
    #             #clear buffer 
    #             for i in range(5):
    #                 pose = self.sub.left.get_pose()
    #             if(pose == None):
    #                 raise Exception('YuMi Did Not Return a Pose')
    #             pose = pose[1]
    #             pose_t = pose.translation

    #             rotation = self.extract_angle(pose)
    #             translation = pose_t[2]
    #             if(self.com.check_data(rotation,translation)):
    #                 terminate = True
    #             else: 
    #                 print "INCORRECT LABELS "
    #                 print "ROTATION ",rotation
    #                 print "Z AXIS ", translation

    #     return pose_t,rotation




    # def record_pose(self,arm = 'LEFT'):
    #     """
    #         Records the (x,y) Pose of the Current YuMi, which is used for learning 

    #         Function waits until Start is Pressed on the Xbox Controller and records pose

    #         Parameters
    #         ----------
    #         arm: string
    #             Specifies which arm to train with (LEFT or RIGHT)

    #     """
    #     while True:
    #         has_update = False
    #         if self.use_audio:
    #             update = self.detect_echo_record()
    #             if update:
    #                 has_update = True
    #         else:
    #             update = self.c.getUpdates()
    #             if update == None:
    #                 has_update = True
    #         if has_update:

    #             if(arm == 'LEFT'):
    #                 pose = self.sub.left.get_pose()
    #             elif(arm == 'RIGHT'):
    #                 pose = self.sub.right.get_pose()

    #             if(pose == None):
    #                 raise Exception('YuMi Did Not Return a Pose')

    #             pose = pose[1]
    #             pose_t = pose.translation
    #             break
          
        # self.label = []

        # pixels = self.com.reg.robot_to_pixel(pose_t[0:2])
        # #rotation = self.extract_angle(pose)

        # self.label = [pixels[0], pixels[1],0.0]

        # self.save_data(self.net_name)

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
        if(self.com.Options.SENSOR == 'BINCAM'):
            self.com.save_recording(recording,self.b)
        elif(self.com.Options.SENSOR == 'PRIMESENSE'): 
            self.com.save_recording(recording)
        return



    # def get_input(self, msg):
    #     if self.use_audio_input:
    #         command = audio_logger.getDataCommand()
    #         return (command is not None)
    #     else:
    #         # Get input from keyboard
    #         # def getchar():
    #         #     fd = sys.stdin.fileno()
    #         #     old_settings = termios.tcgetattr(fd)
    #         #     print "Press 'r' to record: ",
    #         #     try:
    #         #         tty.setraw(fd)
    #         #         ch = sys.stdin.read(1)
    #         #     # except KeyboardInterrupt:
    #         #     #     raise KeyboardInterrupt
    #         #     #     sys.exit(1)
    #         #     finally:
    #         #         termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    #         #     return ch
    #         # if getchar() == 'r':
    #         #     print "r"
    #         #     return True
    #         # return False
    #         pygame.init()
    #         pygame.font.init()
    #         screen = pygame.display.set_mode((400, 200))
    #         screen.fill((255, 255, 255))
    #         myfont = pygame.font.SysFont("monospace", 15)
    #         label = myfont.render("Press 'r' to record", 1, (0,0,0))
    #         screen.blit(label, (100, 100))
    #         pygame.display.flip()
    #         running = True
    #         while running:
    #             for event in pygame.event.get():
    #                 if event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_r]:
    #                     running = False
    #         pygame.quit()
    #     return False

    def get_keyboard_input(self, msg=""):
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((1700, 200))
        screen.fill((255, 255, 255))
        myfont = pygame.font.SysFont("monospace", 32)
        label = myfont.render(msg, 1, (0,0,0))
        screen.blit(label, (50, 50))
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_r]:
                    running = False
        pygame.quit()
        return True

    def display_to_monitor(self, msg):
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((1700, 200))
        screen.fill((255, 255, 255))
        myfont = pygame.font.SysFont("monospace", 32)
        label = myfont.render(msg, 1, (0,0,0))
        screen.blit(label, (50, 50))
        pygame.display.flip()
        return

    # def publish_output(self, msg1, msg2=None):
    #     if self.use_audio_output:
    #         # time.sleep(3)
    #         audio_logger.log(msg1)
    #     else:
    #         if msg2 is None:
    #             msg2 = msg1
    #         # UI display:
    #             # https://wiki.wxpython.org/Getting%20Started#A_First_Application:_.22Hello.2C_World.22
    #             # http://stackoverflow.com/questions/293344/wxpython-set-value-of-statictext
    #             # https://wxpython.org/docs/api/wx.StaticText-class.html
    #         # self.dialogue_gui.SetLabel(msg2)
    #         screen = pygame.display.set_mode((400, 200))
    #         screen.fill((255, 255, 255))
    #         myfont = pygame.font.SysFont("monospace", 15)
    #         label = myfont.render(msg2, 1, (0,0,0))
    #         screen.blit(label, (100, 100))
    #         pygame.display.flip()
    #         # running = True
    #         # while running:
    #         #     for event in pygame.event.get():
    #         #         if event.type == pygame.KEYDOWN and event.key == 'r':
    #         #             pygame.quit()
    #         #             running = False
    #         print msg2
    #     return

    # def detect_echo_record(self):
    #     """
    #     Detect whether the Echo was told to record
    #     """
    #     # self.c.getUpdates() # call the xbox controller for print statements, but don't use it
    #     # print "Querying Echo"
    #     command = audio_logger.getDataCommand()
    #     if command is not None:
    #         print "The Echo heard a Record! Wait for the next line..."
    #         audio_logger.log("I heard re cord! Please wait.")
    #         time.sleep(3)
    #         return True
    #     # print "Not recording"
    #     return False


    def do_io(self, msg):
        if self.use_audio_output:
            msg = msg.replace("record", "re cord")

        if self.use_audio_input and self.use_audio_output:
            audio_logger.log(msg)
            while audio_logger.getDataCommand() is None:
                time.sleep(0.01)
            audio_logger.log("Recording")
        elif not self.use_audio_input and self.use_audio_output:
            audio_logger.log(msg)
            self.get_keyboard_input()
            audio_logger.log("Recording")
        elif self.use_audio_input and not self.use_audio_output:
            self.display_to_monitor(msg)

            while audio_logger.getDataCommand() is None:
                time.sleep(0.01)
            self.display_to_monitor("Recording...")
        elif not self.use_audio_input and not self.use_audio_output:
            self.get_keyboard_input(msg + " Press 'r' to record.")
            self.display_to_monitor("Recording...")
        return True

    
    def log_to_file(self, status):
        file_path = "/home/autolab/Workspace/rishi_working/experiment_logs.csv"
        if not os.path.exists(file_path):
            f = open(file_path,'w')
            header = ["experiment_id", "use_audio_input", "use_audio_output", "rollout_number", "timestamp", "status"]
            f.write(",".join(header))
            f.close()

        f = open(file_path, 'a')
        row = [self.experiment_id, self.use_audio_input, self.use_audio_output, self.com.next_rollout(), time.time(), status]
        f.write(",".join(row))
        f.close()
        return





if __name__ == "__main__":
    print "Done."
