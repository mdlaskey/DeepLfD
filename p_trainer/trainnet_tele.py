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
from deep_lfd.s_ti.s_scoop.com import get_label,get_state, low_pass, prune_stationary_poses

#specific: fetches specific net file
from deep_lfd.tensor.nets.net_scooping import NetScooping as Net 
########################################### #############



def get_trajectory(left_poses, right_poses, webcam):
    # get a single row of records from the csv
    
    T = np.min([left_poses.shape[0],right_poses.shape[0]])
    left_poses = low_pass(left_poses)
    right_poses = low_pass(right_poses)

    traj = []
    for i in range(T-1):
        # cv2.imshow('vid',webcam[i,:,:,:])
        # cv2.waitKey(50)

        l_p = get_label(left_poses[i+1,:],left_poses[i,:])
        r_p = get_label(right_poses[i+1,:],right_poses[i,:])

        
    
        label = np.concatenate((l_p,r_p))
        state = get_state(webcam[i,:])
        traj.append([state,label])

    return traj


if __name__ == '__main__':
    #CSV Model for all teleop trials
    records = load_records('t')

    all_trials = records.get_rows_by_cols({
        'supervisor': 'Jeff_3_12',
        'success': True,
        'demo_name': 'scoop_demo'
    })

    

    print 'loading data...'
    all_left_poses = []
    all_right_poses = []
    all_webcam = []
    for trial in all_trials:
        all_left_poses.append(load_poses(trial, 'left'))
        all_right_poses.append(load_poses(trial, 'right'))
        all_webcam.append(load_images(trial, 'webcam'))

    print 'done!'

    print 'processing data...'
    #all_left_poses, all_right_poses = prune_stationary_poses(all_left_poses, all_right_poses)      
    trajectories = []
    for i in range(len(all_webcam)):
        traj = get_trajectory(all_left_poses[i], all_right_poses[i], all_webcam[i])
        trajectories.append(traj)
    print 'done!'

    #TRAJECTORIES: A LIST OF Rollouts with each rollout [[state,label],...,[state,label]]
    data = inputdata.IMData(trajectories,channels = 3) 
    net = Net()
    print 'start training...'
    net.optimize(2000,data, batch_size=1)
    print 'done!'
