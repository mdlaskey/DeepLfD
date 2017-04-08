from alan.core.options import Options #the imports may need to change on actual computer
import os
from alan.rgbd.registration_wc import RegWC
from alan.rgbd.bincam_2D import BinaryCamera 
import cv2
import time

class Grasp_Options(Options):
    # OFFSET_X = 102
    # OFFSET_Y = 150

    # WIDTH = 120 #halve this to look at half of the box with objects
    # HEIGHT = 230 #this currently brings y to the max
    # OFFSET_X = 160
    # OFFSET_Y = 125

    OFFSET_X = 250  # Bin offset
    OFFSET_Y = 50  # Bin offset

    WIDTH = 200   # bin width
    HEIGHT = 150  # bin height

    ROT_MAX = 180
    ROT_MIN = 0.0

    Z_MIN = 0.020
    Z_MAX = 0.080
    # THRESH_TOLERANCE = 80
    # THRESH_TOLERANCE = 50
    THRESH_TOLERANCE = 45

    CHECK_COLLISION = True

    ROT_SCALE = 100.0

    T = 40

    setup_dir = "grasp/"

    root_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self):
        
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

        self.setup(self.root_dir, self.setup_dir)


    def set_filter_paths(self):

        self.gray_mask_dir = self.setup_dir + "gray_mask/"
        if not os.path.exists(self.gray_mask_dir):
            os.makedirs(self.gray_mask_dir)

        self.gray_mask_binned_dir = self.setup_dir + "gray_mask_binned/"
        if not os.path.exists(self.gray_mask_binned_dir):
            os.makedirs(self.gray_mask_binned_dir)

        self.gray_dir = self.setup_dir + "gray/"
        if not os.path.exists(self.gray_dir):
            os.makedirs(self.gray_dir)

        self.rgb_mask_dir = self.setup_dir + "rgb_mask/"
        if not os.path.exists(self.rgb_mask_dir):
            os.makedirs(self.rgb_mask_dir)

        self.rgb_mask_binned_dir = self.setup_dir + "rgb_mask_binned/"
        if not os.path.exists(self.rgb_mask_binned_dir):
            os.makedirs(self.rgb_mask_binned_dir)

        self.rgb_gray_dir = self.setup_dir + "rgb_gray_dir/"
        if not os.path.exists(self.rgb_gray_dir):
            os.makedirs(self.rgb_gray_dir)




if __name__ == '__main__':
    options = Grasp_Options()
    b = BinaryCamera(options)
    b.open(threshTolerance= options.THRESH_TOLERANCE)

    while (1):
        frame = b.read_color_frame()
        out = frame
        cv2.imshow("camera", out)
        print("reading")
        a = cv2.waitKey(30)
        if a == 1048603:
            cv2.destroyWindow("camera")
            break
        time.sleep(.005)
