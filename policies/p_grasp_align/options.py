from alan.core.options import Options #the imports may need to change on actual computer
import os

class Grasp_AlignOptions(Options):
    OFFSET_X = 102
    OFFSET_Y = 150

    WIDTH = 240 #halve this to look at half of the box with objects
    HEIGHT = 240 #this currently brings y to the max

    X_LOWER_BOUND = 0.334
    X_UPPER_BOUND = 0.580

    Y_LOWER_BOUND = -0.355
    Y_UPPER_BOUND = -0.05

    ROT_MIN = -210.0
    ROT_MAX = 90.0

    THRESH_TOLERANCE = 40

    CHECK_COLLISION = False

    ROT_SCALE = 100
    T= 40

    setup_dir = "grasp_align/"
    root_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self):
        self.setup(self.root_dir, self.setup_dir)
