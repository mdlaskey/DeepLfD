from deep_lfd.core.options import Options #the imports may need to change on actual computer
from deep_lfd.rgbd.registration_wc import RegWC
import os
from deep_lfd.rgbd.bincam_2D import BinaryCamera
import cv2,time

class Tesla_Options(Options):
  
    OFFSET_X = 117
    OFFSET_Y = 64

    WIDTH = 130 #halve this to look at half of the box with objects
    HEIGHT = 240 #this currently brings y to the max


    X_LOWER_BOUND = .280
    X_UPPER_BOUND = .587

    Y_LOWER_BOUND = -.260
    Y_UPPER_BOUND = -.023

    ROT_MAX = 90.0
    ROT_MIN = -210.0
    # THRESH_TOLERANCE = 80
    # THRESH_TOLERANCE = 50
    THRESH_TOLERANCE = 50

    CHECK_COLLISION = True

    ROT_SCALE = 100.0

    T = 40

    setup_dir = "telsa/"

    root_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self):
        self.setup(self.root_dir, self.setup_dir)
        reg = RegWC(self)
        l_b,u_b = reg.get_image_bounds()

        self.X_LOWER_BOUND = l_b[0]
        self.Y_LOWER_BOUND = l_b[1]

        self.X_UPPER_BOUND = u_b[0]
        self.Y_UPPER_BOUND = u_b[1]


        self.X_MID_RANGE = (self.X_UPPER_BOUND - self.X_LOWER_BOUND)/2.0
        self.Y_MID_RANGE = (self.Y_UPPER_BOUND - self.Y_LOWER_BOUND)/2.0

        self.X_CENTER = self.X_LOWER_BOUND+self.X_MID_RANGE
        self.Y_CENTER = self.Y_LOWER_BOUND+self.Y_MID_RANGE


if __name__ == '__main__':
    options = Tesla_Options()
    b = BinaryCamera(options)
    b.open(threshTolerance= options.THRESH_TOLERANCE)

    while (1):
        frame = b.read_binary_frame()
        out = frame
        cv2.imshow("camera", out)
        print("reading")
        a = cv2.waitKey(30)
        if a == 1048603:
            cv2.destroyWindow("camera")
            break
        time.sleep(.005)        
