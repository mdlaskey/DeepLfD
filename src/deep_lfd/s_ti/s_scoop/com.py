import sys, os, time, cv2, argparse
import tty, termios
import numpy as np
import IPython


import joblib 


#lower bound x,y,z,angle
l_b = np.array([0.0,0.0,0.0,-80])

#upper bound x,y,z,angle
u_b = np.array([1.0,1.0,1.0,80])


def get_label(pos,euler):
    #Hack up the poses 

    z_angle = euler[1]

    state = [pos,euler]

    S_D = len(state)

    for i in range(S_D)
       state[i] = (state[i] - l_b[i])/((u_b[i] - l_b[i])/2.0) - 1.0

    return state

def get_state(image):
    #CROP VALUES 
    org = [180,200]
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

    cv2.imshow('img',255.0*(crop_image))
    cv2.waitKey(30)
    IPython.embed()
    return crop_image 




if __name__ == '__main__':
    poses = joblib.load('src/deep_lfd/s_ti/s_scoop/poses_right.jb')
    IPython.embed()
   
    # sub = YuMiSubscriber()
    # sub.start()
