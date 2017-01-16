import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
import cv2


from alan.synthetic.synthetic_translation import transform_image
from alan.synthetic.synthetic_rotation import rotate_images
from alan.rgbd.registration_wc import RegWC
from alan.synthetic.synthetic_util import re_binarize

from alan.synthetic.filters import apply_all
import numpy as np, argparse
#Things to change

from alan.core.points import Point
from alan.p_grasp.options import Grasp_Options as Options



class Filter_Gen:

    def __init__(self):

        self.options = Options()
        self.options.set_filter_paths()


    def generate_data(self,first,last):
 
        outfile = open(self.options.data_dir + 'deltas.txt', 'w+')
        f = []
        for (dirpath, dirnames, filenames) in os.walk(self.options.sup_dir):
            print dirpath
            print filenames
            f.extend(dirnames)
        for filename in f:
            read_path = self.options.sup_dir+filename+'/net_deltas.txt'
            if read_path.find("net_deltas") != -1 and read_path.find("~") == -1:
                index = int(filename[7:])
                if index < last and first <= index:
                    self.generate_filters(read_path,filename)





    def make_imgs(self,img,name):
        print "NAME ", name

        filters = apply_all(img)
        
        #gray image
        gray = filters[0]
        cv2.imwrite(self.options.gray_dir+name,gray)

        #gray masked
        gray_m = filters[1]
        cv2.imwrite(self.options.gray_mask_dir+name,gray_m)

        #gray binned
        gray_m_b= filters[2]
        cv2.imwrite(self.options.gray_mask_binned_dir+name,gray_m_b)

        #rgb binned
        rgb_m_b= filters[3]
        cv2.imwrite(self.options.rgb_mask_dir+name,rgb_m_b)

        #rgb binned
        rgb_m_b= filters[4]
        cv2.imwrite(self.options.rgb_mask_binned_dir+name,rgb_m_b)

        #rgb gray
        rgb_gray= filters[5]
        cv2.imwrite(self.options.rgb_gray_dir+name,rgb_gray)


    def generate_filters(self,read_path,rollout):
        f = open(read_path,"r")

        for line in f:
            line = line.split()
            img_name = line[0]
            img = cv2.imread(self.options.originals_dir+img_name)
            self.make_imgs(img,img_name)




        f.close()
       


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--first", type=int,
                        help="enter the starting value of rollouts to be used for training")
    parser.add_argument("-l", "--last", type=int,
                        help="enter the last value of the rollouts to be used for training")

    parser.add_argument("-n", "--net_name", type=str,
                        help="enter the name of the net to be trained")

    parser.add_argument("-d", "--demonstrator", type=str,
                        help="enter the name of the subject trained")


    args = parser.parse_args()

    if args.first is not None:
        first = args.first
    else:
        print "please enter a first value with -f"
        sys.exit()

    if args.last is not None:
        last = args.last
    else:
        print "please enter a last value with -l (not inclusive)"
        sys.exit()


    fg = Filter_Gen()

    fg.generate_data(first,last)

