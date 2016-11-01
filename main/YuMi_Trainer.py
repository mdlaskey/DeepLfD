import sys, os, time, cv2, argparse
import tty, termios
sys.path.append(sys.path[0] + "/deps/gripper/")
import IPython
from alan.rgbd.bincam_2D import BinaryCamera
from alan.control import YuMiRobot, YuMiState
from alan.lfd_amazon.amazon_overlay import makeOverlay,generalOverlay

from alan.rgbd.image import Image, DepthImage, ColorImage
# import xboxController

from alan.control.xboxController import *
from alan.rgbd.registration_wc import RegWC
import numpy as np
import numpy.linalg as LA

#Change this per task
from alan.p_grasp_align.options import Grasp_AlignOptions as Options
from alan.p_grasp_align.com import Grasp_AlignCOM as COM

def getch():
    """
        Pause the program until key press
        Return key press character
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def teleop(c, y, b,com):
    time.sleep(.5)
    com.go_to_initial_state(y)
   
    recording = []
    print "Start"
    i = 0

    states, saved_deltas = [], []

    grip_open = 0
    frames = []
    
    
    #Clear Camera Buffer
    for i in range(5):
        frame = b.read_frame()

    for i in range(Options.T):
        frame = b.read_frame()
        frames.append(frame)

  
    current_state = y.right.get_pose()
    prev_pose = np.copy(current_state.position)
    theta_n = 0.0
    try:
        while True:
            start = time.time()
            controls = c.getUpdates()
            deltas, stop = controls2deltas(controls)

            print stop
            if stop:
                c_pose = y.right.get_pose()
                pixels = com.reg.robot_to_pixel(c_pose.position[0:2])
      
                label = [pixels[0], pixels[1], theta_n]

                com.execute_motion(y)
                print "Do you want to save (yes-x/no-y/quit-b)"
                while True: 
                    char = getch()
                    

                    if char == 'y':
                        for i in range(len(frames)):
                            recording.append([frames[i],label])
                        com.save_recording(recording,b)
                        break
                    elif char == 'q':
                        return False
                    elif char =='n':
                        break
                break
            
            print "pose: ", current_state.position


            frame = b.read_binary_frame()
            cv2.imshow("camera", frame)
            cv2.waitKey(30)


            if not all(d == 0.0 for d in deltas):
                print i
                i += 1

                # ''' Perception code here '''

                true_state = y.right.get_pose()
                print "TRUE STATE ", true_state.position
                # ''' delta Low pass filter/ control regularization code here'''
                print "current_state: ", current_state.position
                print "deltas: ",deltas
                print "grip_open: ", grip_open

                pose, grip_new,theta_n = com.apply_deltas(deltas, true_state, grip_open,theta_n)
                print "new_state: ", pose.position

                
                p_d = pose.position - prev_pose
                p_d = np.matmul(LA.inv(pose.rotation),p_d)
                p_d[2] = 0
                print "POSE DELTA ", p_d
                #y.right.goto_pose_delta(p_d,)
                if(not com.is_rot_bound(theta_n)):
                    deltas[4] = 0.0


                y.right.goto_pose_delta(p_d,rot_delta=[0.0,0.0,deltas[4]])
                
                prev_pose = np.copy(pose.position)
                current_state = pose

            offset = max(0, .1 - (time.time() - start))
            print "offset time: ", offset
            time.sleep(offset)
            print "total time: ", time.time() - start

    except KeyboardInterrupt:
        pass
    stop = False
    return True
    

    # return prompt_save(frames, deltas_lst, states, name)

def getButtons(controls):
    if controls == None:
        return 'l'
    print controls
    val1 = controls[4]
    val2 = controls[6]

    if(val1 == -1):
        return 'y'
    elif(val1 == 1):
        return 'n'
    elif(val2 == 1):
        return 'q'
    else: 
        return 'l'



def controls2deltas(controls):
    deltas = [0.0] * 5
    MM_T_M = 0.001
    stop = False
    if controls == None:
        return None, True
    print "control: ", controls
    deltas[0] = -controls[3]*5*MM_T_M
    deltas[1] = -controls[2]*5*MM_T_M
    deltas[2] = controls[4]*1*MM_T_M
    deltas[3] = controls[6]*MM_T_M
    deltas[4] = controls[5]

    print "CONTROL LEFT STICK ", deltas[4]
    if abs(deltas[0]) < 8e-1*MM_T_M:
        deltas[0] = 0.0
    if abs(deltas[1]) < 8e-1*MM_T_M:#8e-4: #2e-2:
        deltas[1] = 0.0
    if abs(deltas[2]) < 5e-3*MM_T_M:
        deltas[2] = 0.0
    if abs(deltas[4]) < 8e-1:
        deltas[4] = 0.0
    deltas[4] = deltas[4]*20
    print "right: ", deltas[0], " forward: ", deltas[1], " vertical: ", deltas[2], "grip: ", deltas[3]
    return deltas, stop
    




if __name__ == '__main__':

    yumi = YuMiRobot(include_left=False)
    options = Options()
    com = COM(train=True)
    

    b = BinaryCamera(options)
    b.open(threshTolerance= Options.THRESH_TOLERANCE)
    yumi.set_z('fine')

    c = XboxController([1,1,1,1,1,1,1])
    NUM_MOTIONS = 600

    com.go_to_initial_state(yumi)
    frame = b.display_frame()
 
   

   
    while True:
        while (1):
            frame = b.display_frame()
            out = frame#+o
            cv2.imshow("camera", out)
            print("reading")
            a = cv2.waitKey(30)
            if a == 1048603:
                cv2.destroyWindow("camera")
                break
            time.sleep(.005)        
        

        grasps= 0

        while grasps<NUM_MOTIONS:
            if teleop(c,yumi,b,com):
                grasps=grasps+1
            else:
                break
        com.go_to_initial_state(yumi)
    
    print "Done"