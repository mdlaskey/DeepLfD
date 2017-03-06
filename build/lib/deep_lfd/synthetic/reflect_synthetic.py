import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
import cv2


from alan.synthetic.synthetic_reflection import reflect_images
from alan.rgbd.registration_wc import RegWC
from alan.synthetic.synthetic_util import re_binarize
import numpy as np, argparse
#Things to change

from alan.lfd_amazon.options import AmazonOptions as options_s
from alan.p_singulate_L.options import Singulate_LOptions as options_d
from alan.core.points import Point

#All units will be in MM

Options_s = options_s()
Options_d = options_d()
reg_wc = RegWC(Options_d)

def get_bounds():
    low_bound = np.array([Options_d.X_LOWER_BOUND,Options_d.Y_LOWER_BOUND])
    up_bound = np.array([Options_d.X_UPPER_BOUND,Options_d.Y_UPPER_BOUND])
    rot_bounds = np.array([Options_d.ROT_MIN,Options_d.ROT_MAX])
    p_l_b = reg_wc.robot_to_pixel(low_bound)
    p_u_b = reg_wc.robot_to_pixel(up_bound)

    return p_l_b,p_u_b,rot_bounds


def copy_over(infile, outfile):
    lines = infile.readlines()
    for line in lines:
    	outfile.write(line)

def conv_deltas_to_str(deltas):
    label = " "

    for i in range(len(deltas)):
        label = label+str(deltas[i])+" "

    label = label+"\n"
    return label



#Each image is stored as follows [path,rollout,index,img])
def save_images(imgs):
 
    for img_d in imgs:
        if(not len(img_d) == 0):
            path = img_d[0]
            rollout = img_d[1]
            index = img_d[2]
            img = img_d[3]
            #img = re_binarize(img)
            cv2.imwrite(path+rollout+'_frame_'+str(index)+".jpg",img)
            print "IMAGE INDEX ", str(index)

    return




def inflate_data(read_path,write_path,rollout,tras = True, rotation = True):
    f = open(read_path,"r")
    f_c = open(Options_s.sup_dir+rollout+'/net_deltas_c.txt',"w")

    changes = []
    idx = 0
    imgs = []
  
    bounds = get_bounds()
    for line in f:
        f_c.write(line)
        line = line.split()
        

        label = np.array([float(line[1]),float(line[2]),float(line[3])])
        

        matrix = cv2.imread(Options_s.binaries_dir+line[0],1)
        # cv2.imshow('debug',matrix)
        # cv2.waitKey(30)
        img_data = [Options_d.binaries_dir,rollout,matrix]
        deltas,idx,r_img = reflect_images(img_data,idx,bounds,label)
        changes.append(deltas)
        imgs.append(r_img)
       
    f_c.close()
    f.close()

    save_images(imgs)
    if(not os.path.isdir(write_path)):
        os.makedirs(write_path)
    f = open(write_path+'/net_deltas.txt','w')
    idx = 0
    for i in range(len(changes)):
        for k in range(len(changes[i])):
            
            f_name = rollout+"_frame_"+str(idx)+".jpg"
            f.write(f_name+conv_deltas_to_str(changes[i][k]))
            #print f_name+conv_deltas_to_str(changes[i][k])
            idx += 1

    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--first", type=int,
                        help="enter the starting value of rollouts to be used for training")
    parser.add_argument("-l", "--last", type=int,
                        help="enter the last value of the rollouts to be used for training")

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



    outfile = open(Options_d.data_dir + 'deltas.txt', 'w+')
    f = []
    for (dirpath, dirnames, filenames) in os.walk(Options_s.sup_dir):
        print dirpath
        print filenames
        f.extend(dirnames)
    for filename in f:
        read_path  = Options_s.sup_dir+filename+'/net_deltas.txt'
        write_path = Options_d.sup_dir+filename

        if read_path.find("net_deltas") != -1 and read_path.find("~") == -1:
            index = int(filename[7:])
            if index < last and first <= index:
                inflate_data(read_path,write_path,filename)

                infile = open(read_path, 'r')

                copy_over(infile, outfile)
                infile.close()




    outfile.close()
