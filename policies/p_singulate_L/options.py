from alan.core.options import Options #the imports may need to change on actual computer
import os

class Singulate_LOptions(Options):
    #OFFSET_X = 270     # original offset
    #OFFSET_Y = 150     # original offset
    OFFSET_X = 350  # Bin offset
    OFFSET_Y = 100  # Bin offset
    WIDTH = 120     # original width #halve this to look at half of the box with objects
    HEIGHT = 230    # original height #this currently brings y to the max
    # WIDTH = 250   # bin width
    # HEIGHT = 355  # bin height

    X_LOWER_BOUND = 0.334   # original bound
    X_UPPER_BOUND = 0.580   # original bound


    # Y_LOWER_BOUND = -0.165    # original bound
    # Y_UPPER_BOUND = 0.007     # original bound

    Y_LOWER_BOUND = .094    # bin offset
    Y_UPPER_BOUND = .266    # bin offset

    ROT_MIN = -210.0
    ROT_MAX = 90.0
    
    THRESH_TOLERANCE = 80

    CHECK_COLLISION = True


    setup_dir = "singulate_L/"

    root_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self):
        self.setup(self.root_dir, self.setup_dir)
