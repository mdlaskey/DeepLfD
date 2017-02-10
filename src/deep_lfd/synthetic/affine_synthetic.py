import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
import cv2


from deep_lfd.synthetic.synthetic_translation import transform_image
from deep_lfd.synthetic.synthetic_rotation import rotate_images
from deep_lfd.rgbd.registration_wc import RegWC
from deep_lfd.synthetic.synthetic_util import re_binarize
import numpy as np, argparse
#Things to change
from perception import DepthImage, RgbdForegroundMaskQueryImageDetector
from alan.core.points import Point




class Affine_Synthetic:

    def __init__(self,options,translation=False,rotation= False, max_trans = 20, max_rot = 20):

        self.options = options

        self.translation = translation
        self.rotation = rotation
        self.max_trans = max_trans
        self.max_rot = max_rot
        self.reg_wc = RegWC(options)


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
                    self.inflate_data(read_path,filename)

                    infile = open(read_path, 'r')

                    self.copy_over(infile, outfile)
                    infile.close()


    def get_bounds_ps(self):
        rot_bounds = np.array([self.options.ROT_MIN,self.options.ROT_MAX])
        p_l_b = np.array([self.options.LOWER_X_P_BOUNDS,self.options.LOWER_Y_P_BOUNDS])
        p_u_b = np.array([self.options.UPPER_X_P_BOUNDS,self.options.UPPER_Y_P_BOUNDS])

        return p_l_b,p_u_b,rot_bounds

    def get_bounds(self):
        low_bound = np.array([self.options.X_LOWER_BOUND,self.options.Y_LOWER_BOUND])
        up_bound = np.array([self.options.X_UPPER_BOUND,self.options.Y_UPPER_BOUND])
        rot_bounds = np.array([self.options.ROT_MIN,self.options.ROT_MAX])
        p_l_b = self.reg_wc.robot_to_pixel(low_bound)
        p_u_b = self.reg_wc.robot_to_pixel(up_bound)

        return p_l_b,p_u_b,rot_bounds


    def copy_over(self,infile, outfile):
        lines = infile.readlines()
        for line in lines:
        	outfile.write(line)

    def conv_deltas_to_str(self,deltas):
        label = " "

        for i in range(len(deltas)):
            label = label+str(deltas[i])+" "

        label = label+"\n"
        return label



    #Each image is stored as follows [path,rollout,index,img])
    def save_images(self,imgs):
     
        for img_d in imgs:
            path = img_d[0]
            rollout = img_d[1]
            index = img_d[2]
            img = img_d[3]
            #img = re_binarize(img)

            img.save(path+rollout+'_frame_'+str(index)+".npy")

            print "IMAGE INDEX ", str(index)

        return

    def load_images(self,path):
        if self.options.SENSOR == 'PRIMESENSE':
            img = DepthImage.open(path)
        elif self.options.SENSOR == 'BINCAM':
            img = BinaryImage.open(path)

        return img





    def inflate_data(self,read_path,rollout,tras = True, rotation = False):
        f = open(read_path,"r")
        f_c = open(self.options.sup_dir+rollout+'/net_deltas_c.txt',"w")

        changes = []
        idx = self.options.T
        i = 0

        if(self.options.SENSOR == 'PRIMESENSE'):
            bounds = self.get_bounds_ps()
        else: 
            bounds = self.get_bounds()
            
        for line in f:
            f_c.write(line)
            line = line.split()
            
            if(self.translation):
                cp = np.array([float(line[1]),float(line[2]),float(line[3])])
                deltas,idx,imgs = transform_image(self.options.binaries_dir,rollout,line[0],idx,bounds,cp, max_imgs = self.max_trans)
                changes.append(deltas)
                print "ENDED TRANSLATION"

                #Save images 
                self.save_images(imgs)

            if(self.rotation):
                imgs = []
                if(not self.translation):
                    img = self.load_images(self.options.binaries_dir+line[0])
                    img_data = [self.options.binaries_dir,rollout,idx,img]
                    imgs.append(img_data)

                cp = np.array([float(line[1]),float(line[2]),float(line[3]),float(line[4])])
                deltas,idx,imgs = rotate_images(imgs,idx,bounds,cp,max_imgs = self.max_rot)
       
                changes.append(deltas)
                #Save images 
                self.save_images(imgs)
                print "ENDED ROTATION"
          
            i = i+1
            if(i == self.options.T):
                break;
        f_c.close()
        f.close()

        #Clean Shit Up
        f = open(read_path,"w")
        f_c = open(self.options.sup_dir+rollout+'/net_deltas_c.txt',"r")
        for line in f_c:
            f.write(line)


        f.close()
        f_c.close()

        f = open(read_path,'a+')
        idx = self.options.T
        for i in range(len(changes)):
            for k in range(len(changes[i])):
                
                f_name = rollout+"_frame_"+str(idx)+".npy"
                f.write(f_name+self.conv_deltas_to_str(changes[i][k]))
                #print f_name+conv_deltas_to_str(changes[i][k])
                idx += 1

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


    if args.net_name is not None:
        net_name = args.net_name+'/'
        demonstrator = '/'+args.demonstrator+'/'
        root_dir = '/home/autolab/Workspace/michael_working/alan/AHRI'+demonstrator
        Options.setup(root_dir, net_name,folder='net')





    outfile = open(self.options.data_dir + 'deltas.txt', 'w+')
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
