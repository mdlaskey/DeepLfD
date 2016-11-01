import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
import cv2


from alan.synthetic.synthetic_translation import transform_image
from alan.synthetic.synthetic_rotation import rotate_images
from alan.rgbd.registration_wc import RegWC
from alan.synthetic.synthetic_util import re_binarize
import numpy as np, argparse
#Things to change

from alan.p_grasp_align.options import Grasp_AlignOptions as options
from alan.core.points import Point

#All units will be in MM

Options = options()
reg_wc = RegWC(Options)

def get_bounds():
    low_bound = np.array([Options.X_LOWER_BOUND,Options.Y_LOWER_BOUND])
    up_bound = np.array([Options.X_UPPER_BOUND,Options.Y_UPPER_BOUND])
    rot_bounds = np.array([Options.ROT_MIN,Options.ROT_MAX])
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
        path = img_d[0]
        rollout = img_d[1]
        index = img_d[2]
        img = img_d[3]
        #img = re_binarize(img)
<<<<<<< HEAD
        cv2.imwrite(path+rollout+'_frame_'+str(index)+".png",img)
=======
        db.writeData(path,bc.apply_mask(frame), rollout, index)
>>>>>>> 21357785a3ae2f93af0c84c6aabb5589e12e6f0a
        print "IMAGE INDEX ", str(index)

    return




def inflate_data(read_path,rollout,tras = True, rotation = True):
    f = open(read_path,"r")
    f_c = open(Options.sup_dir+rollout+'/net_deltas_c.txt',"w")

    changes = []
    idx = Options.T
    i = 0
    bounds = get_bounds()
    for line in f:
        f_c.write(line)
        line = line.split()
        
        
        cp = np.array([float(line[1]),float(line[2]),float(line[3])])
        deltas,idx,imgs = transform_image(Options.binaries_dir,rollout,line[0],idx,bounds,cp)
        changes.append(deltas)
        print "ENDED TRANSLATION"

        #Save images 

        save_images(imgs)

        if(rotation):
            cp = np.array([float(line[1]),float(line[2]),float(line[3])])
            deltas,idx,imgs = rotate_images(imgs,idx,bounds,deltas,cp)
   
            changes.append(deltas)
            #Save images 
            save_images(imgs)
            print "ENDED ROTATION"
      
        i = i+1
        if(i == Options.T):
            break;
    f_c.close()
    f.close()

    #Clean Shit Up
    f = open(read_path,"w")
    f_c = open(Options.sup_dir+rollout+'/net_deltas_c.txt',"r")
    for line in f_c:
        f.write(line)


    f.close()
    f_c.close()

    f = open(read_path,'a+')
    idx = Options.T
    for i in range(len(changes)):
        for k in range(len(changes[i])):
            
            f_name = rollout+"_frame_"+str(idx)+".png"
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



    outfile = open(Options.data_dir + 'deltas.txt', 'w+')
    f = []
    for (dirpath, dirnames, filenames) in os.walk(Options.sup_dir):
        print dirpath
        print filenames
        f.extend(dirnames)
    for filename in f:
        read_path = Options.sup_dir+filename+'/net_deltas.txt'
        if read_path.find("net_deltas") != -1 and read_path.find("~") == -1:
            index = int(filename[7:])
            if index < last and first <= index:
                inflate_data(read_path,filename)

                infile = open(read_path, 'r')

                copy_over(infile, outfile)
                infile.close()




    outfile.close()
