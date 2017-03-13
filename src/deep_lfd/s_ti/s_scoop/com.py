import sys, os, time, cv2, argparse
import tty, termios
import numpy as np
import IPython
from scipy.ndimage.filters import gaussian_filter
import joblib 

#TODO: FILL IN 
#lower bound x,y,z,angle
#u_b = np.array([1e-2,1e-2,1e-2,6])
u_b = np.array([1e-2,1e-2,6])
#upper bound x,y,z,angle
#l_b = np.array([-1e-2,-1e-2,-1e-2,-1])
l_b = np.array([-1e-2,-1e-2,-1])
sigmas = {
    'tra': 3,
    'rot': 2
}

thresholds = {
    'tra': 0.001,
    'rot': 0.5
}

def prune_stationary_poses(left_poses, right_poses):
    tra_e = thresholds['tra']
    rot_e = thresholds['rot']
    pruned_left_poses = []
    pruned_right_poses = []
    for i in range(min(len(left_poses), len(right_poses))):
        left_pose = left_poses[i]
        right_pose = right_poses[i]
        pruned_left_pose = []
        pruned_right_pose = []
        for t in range(1, min(len(left_pose), len(right_pose))):
            diff_left = left_pose[t] - left_pose[t-1]
            diff_right = right_pose[t] - right_pose[t-1]
            
            max_diff_tra_left = np.max(np.abs(diff_left[:3]))
            max_diff_tra_right = np.max(np.abs(diff_right[:3]))
            
            max_diff_rot_left = np.max(np.abs(diff_left[3:]))
            max_diff_rot_right = np.max(np.abs(diff_right[3:]))
            
            if not (max_diff_tra_left < tra_e and max_diff_tra_right < tra_e and \
                max_diff_rot_left < rot_e and max_diff_rot_right < rot_e):
                pruned_left_pose.append(left_pose[t])
                pruned_right_pose.append(right_pose[t])
                
        pruned_left_poses.append(np.array(pruned_left_pose))
        pruned_right_poses.append(np.array(pruned_right_pose))
    pruned_left_poses = np.array(pruned_left_poses)
    pruned_right_poses = np.array(pruned_right_poses)
    return pruned_left_poses, pruned_right_poses

def scale_to_nn(x, i):
    return (x - l_b[i]) / ((u_b[i] - l_b[i]) / 2.0) - 1.0

def scale_to_data(x, i):
    return (x + 1.0) * ((u_b[i] - l_b[i]) / 2.0) + l_b[i]

def low_pass(poses):
    poses = poses.copy()
    for i in range(3):
        poses[:,i] = gaussian_filter(poses[:,i], sigmas['tra'])
    for i in range(3, 6):
        poses[:,i] = gaussian_filter(poses[:,i], sigmas['rot'])

    return poses

def get_label(pos,prev_pos):
    #Hack up the poses
    print "POSES ",pos
    delta_pos = pos-prev_pos
    label = [delta_pos[0],delta_pos[1],delta_pos[3]]

    for i in range(len(label)):
       label[i] = scale_to_nn(label[i], i)
    print label
    return label

def rescale(outval):
    pos_l = outval[:3]
    pos_r = outval[3:] 
  
    for i in range(3):
        pos_l[i] = scale_to_data(pos_l[i], i)
        pos_r[i] = scale_to_data(pos_r[i], i)        

    return pos_l, pos_r


def rescale_n(outval):
    pos_l = outval[:,0:4]
   
    pos_r = outval[:,4:] 
   
  
    for i in range(4):
        print scale_to_data(pos_l[:,i], i)
        print scale_to_data(pos_r[:,i], i)        

    return pos_r


def get_state(image):
    #CROP VALUES 
    org = [60,200]
    dim = [100,250]
    
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
    cv2.imshow('img',255.0*crop_image)
    cv2.waitKey(30)

    
    return crop_image 

if __name__ == '__main__':
    poses = joblib.load('src/deep_lfd/s_ti/s_scoop/poses_right.jb')
    IPython.embed()
   
    # sub = YuMiSubscriber()
    # sub.start()
