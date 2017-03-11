import sys, os, time, cv2, argparse
import tty, termios
import numpy as np
import IPython


import joblib 

#TODO: FILL IN 
#lower bound x,y,z,angle
l_b = np.array([1e-2,1e-20,1e-2,6])

#upper bound x,y,z,angle
u_b = np.array([-1e-2,-1e-2,-1e-2,-6])


def get_label(pos,prev_pos):
    #Hack up the poses
    delta_pos = pos-prev_pos
 
    label = np.zeros(4) 
    label[0:3] = delta_pos[0:3]
    label[3] = delta_pos[4]
    

    S_D = len(label)

    for i in range(S_D):
       label[i] = (label[i] - l_b[i])/((u_b[i] - l_b[i])/2.0) - 1.0

    return label

def rescale(outval):

    S_D = len(outval)
    s_outval = outval

    for i in range(S_D):
        s_outval = (outval[i]+1.0)*((u_b[i] - l_b[i])/2.0)+l_b[i]
 
    pos_l = s_outval[0:4]
    pos_r = s_outval[4:S_D] 

    return pos_r,pos_l



def get_state(image):
    #CROP VALUES 
    org = [60,200]
    dim = [100,250]
    print image.shape
    crop_image = image[org[0]:org[0]+dim[0],org[1]:org[1]+dim[1],:]

   
    #BGR
    crop_image[:,:,0] = np.round(crop_image[:,:,0]/280.0)
    crop_image[:,:,1] = np.round(crop_image[:,:,1]/255.0)
    crop_image[:,:,2] = np.round(crop_image[:,:,2]/250.0)

    # for i in range(100):
    #     for j in range(250):
    #         if(crop_image[i,j,0] == 1 and crop_image[i,j,1] == 1 and crop_image[i,j,2] == 1):
    #             crop_image[i,j,:] = 0.0

    #crop_image[:,:,0] = 0.0

    # cv2.imshow('img',255.0*(crop_image))
    # cv2.waitKey(30)

    return crop_image 




if __name__ == '__main__':
    poses = joblib.load('src/deep_lfd/s_ti/s_scoop/poses_right.jb')
    IPython.embed()
   
    # sub = YuMiSubscriber()
    # sub.start()
