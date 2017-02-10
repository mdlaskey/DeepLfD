import sys
import numpy as np
import random
import IPython
from deep_lfd.rgbd.registration_wc import RegWC

#from alan.lfd_amazon.options import AmazonOptions as Options
#we can pass this into the Compile_Sup object.



class Compile_Sup:
    def __init__(self, Options):
        self.Options = Options

    def get_range(self):
        reg = RegWC(self.Options)
        low_bound = np.array([self.Options.X_LOWER_BOUND,self.Options.Y_LOWER_BOUND])
        up_bound = np.array([self.Options.X_UPPER_BOUND,self.Options.Y_UPPER_BOUND])

        #Convert to Pixels
        low_bound = reg.robot_to_pixel(low_bound)
        up_bound = reg.robot_to_pixel(up_bound)

        x_mid_range = (up_bound[0] - low_bound[0])/2.0
        y_mid_range = (up_bound[1] - low_bound[1])/2.0

        x_center = low_bound[0] + x_mid_range
        y_center = low_bound[1] + y_mid_range


        return [x_mid_range,y_mid_range,x_center,y_center]


    def get_range_ps(self):


        #Convert to Pixels
        low_bound = np.array([self.Options.LOWER_X_P_BOUNDS,self.Options.LOWER_Y_P_BOUNDS])
        up_bound = np.array([self.Options.UPPER_X_P_BOUNDS,self.Options.UPPER_Y_P_BOUNDS])

        x_mid_range = (up_bound[0] - low_bound[0])/2.0
        y_mid_range = (up_bound[1] - low_bound[1])/2.0

        x_center = low_bound[0] + x_mid_range
        y_center = low_bound[1] + y_mid_range


        return [x_mid_range,y_mid_range,x_center,y_center]

    def scale(self,deltas,constants):
        deltas[0] = float(deltas[0])
        deltas[1] = float(deltas[1])
        deltas[2] = float(deltas[2])
        deltas[3] = float(deltas[3])

        deltas[0] = (deltas[0]-constants[2])/constants[0]
        deltas[1] = (deltas[1]-constants[3])/constants[1]

        if(np.abs(deltas[0])>1.0):
            deltas[0] = np.sign(deltas[0])*1.0

        if(np.abs(deltas[1])>1.0):
            deltas[1] = np.sign(deltas[1])*1.0


        deltas[2] = (deltas[2] - self.Options.ROT_MIN)/((self.Options.ROT_MAX - self.Options.ROT_MIN)/2.0) - 1

        if(len(deltas) == 4):
            deltas[3] = (deltas[3] - self.Options.Z_MIN)/((self.Options.Z_MAX - self.Options.Z_MIN)/2.0) - 1

        return deltas

    def get_rollout(self,f_name):
        i = f_name.find('_')
        rollout_num = int(f_name[7:i])
        return rollout_num

    def compile_reg(self,img_path = None): #might need selfs here
        train_path = self.Options.train_file
        test_path = self.Options.test_file
        deltas_path = self.Options.deltas_file

        if(self.Options.SENSOR == 'PRIMESENSE'):
            scale_constants = self.get_range_ps()
        else:
            scale_constants = self.get_range()

        if(img_path == None):
            img_path = self.Options.binaries_dir

        print "Moving deltas from " + deltas_path + " to train: " + train_path + " and test: " + test_path
        train_file = open(train_path, 'w+')
        test_file = open(test_path, 'w+')
        deltas_file = open(deltas_path, 'r')
        i=0
        cur_rollout = 0
        p_rollout = -1

        for line in deltas_file:

            l = line.split()
            cur_rollout = self.get_rollout(l[0])

            if(cur_rollout != p_rollout):
                p_rollout = cur_rollout
                if random.random() > .2:
                    train = True
                else:
                    train = False

            path = img_path
            labels = line.split()

            print labels

           
            deltas = self.scale(labels[1:len(labels)],scale_constants)

            deltas = self.scale(labels[1:len(labels)],scale_constants)


            line = labels[0] + " "
            for bit in deltas:
                line += str(bit) + " "
            line = line[:-1] + '\n'

            if train:
                train_file.write(path + line)
            else:
                test_file.write(path + line)

            i=i+1

    if __name__ == '__main__':
        compile_reg()
