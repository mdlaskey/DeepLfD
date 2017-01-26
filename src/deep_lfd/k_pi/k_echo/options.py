from deep_lfd.core.options import Options #the imports may need to change on actual computer
import os

class Echo_Options(Options):

    setup_dir = "echo/"
    root_dir = os.path.dirname(os.path.realpath(__file__)) + "/"

    def __init__(self):
        self.setup(self.root_dir, self.setup_dir)
