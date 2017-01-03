from deep_lfd.core.options import Options #the imports may need to change on actual computer
import os

class Box_Options(Options):
    OFFSET_X = 160
    OFFSET_Y = 125

    WIDTH = 350 #halve this to look at half of the box with objects
    HEIGHT = 230 #this currently brings y to the max

    X_LOWER_BOUND = 0.240
    X_UPPER_BOUND = 0.580

    Y_LOWER_BOUND = -0.165
    Y_UPPER_BOUND = 0.280

    ROT_MIN = -210.0
    ROT_MAX = 90.0

    THRESH_TOLERANCE = 50

    CHECK_COLLISION = False

    ROT_SCALE = 100
    T= 40

    setup_dir = "box/"
    root_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self):
        self.setup(self.root_dir, self.setup_dir)
