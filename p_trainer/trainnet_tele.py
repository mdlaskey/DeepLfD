''''
    Used to train a nerual network that maps an image to robot poses

    Author: Michael Laskey 

'''
import sys, os

import IPython,cv2
from deep_lfd.tensor import inputdata
from compile_sup import Compile_Sup 
import numpy as np, argparse
from deep_lfd.synthetic.affine_synthetic import Affine_Synthetic
from yumi_teleop import load_records, load_poses, load_joints, load_images

#######NETWORK FILES TO BE CHANGED#####################
#specific: imports options from specific options file
from deep_lfd.s_ti.s_scoop.com import get_label,get_state 

#specific: fetches specific net file
from deep_lfd.tensor.nets.net_scooping import NetScooping as Net 
########################################### #############



def get_trajectory(trial):
    # get a single row of records from the csv
    
    trial_path = trial['trial_path']
    
    # poses of left arm
    left_poses = load_poses(trial_path, 'left')
    print 'left poses shape', left_poses.shape
    
    # poses of right arm
    right_poses = load_poses(trial_path, 'right')
    print 'right poses shape', right_poses.shape

    # kinect frames
    kinect = load_images(trial_path, 'webcam')
    print 'kinect shape', kinect.shape    

    T = np.min([left_poses.shape[0],right_poses.shape[0]])


    traj = []
    for i in range(T-1):
        # cv2.imshow('vid',kinect[i,:,:,:])
        # cv2.waitKey(50)
    
        label = np.concatenate((get_label(left_poses[i+1,:],left_poses[i,:]),get_label(right_poses[i+1,:],right_poses[i,:])))

        state = get_state(kinect[i,:])
        traj.append([state,label])

    return traj


if __name__ == '__main__':
    #CSV Model for all teleop trials
    records = load_records('t')

  


    all_trials = records.get_rows_by_cols({
        'supervisor': 'Jeff_Kinect',
        'success': True,
        'demo_name': 'scoop_demo'
    })

    trajectories = []
    for trial in all_trials:
        traj = get_trajectory(trial)
        trajectories.append(traj)


    #TRAJECTORIES: A LIST OF Rollouts with each rollout [[state,label],...,[state,label]]

    data = inputdata.IMData(trajectories,channels = 3) 
    net = Net()
    net.optimize(500,data, batch_size=2)
