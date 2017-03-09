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
from deep_lfd.tensor.nets.net_grasp import Net_Grasp as Net 
########################################### #############



def get_trajectory(num,records):
    # get a single row of records from the csv
    a_trial_record = records.get_by_cols({
        'supervisor': 'Jeff',
        'demo_name': 'scoop_demo',
        'trial_num': num
    })
    
    trial_path = a_trial_record['trial_path']
    
    # poses of left arm
    left_poses = load_poses(trial_path, 'left')
    print 'left poses shape', left_poses.shape
    
    # poses of right arm
    right_poses = load_poses(trial_path, 'right')
    print 'left poses shape', right_poses.shape

    # kinect frames
    kinect = load_images(trial_path, 'webcam')
    print 'kinect shape', kinect.shape    

    T = left_poses.shape[0]
    print "TRAJ ",num
    traj = []
    for i in range(T):
        cv2.imshow('vid',kinect[i,:,:,:])
        cv2.waitKey(300)
        # label = [left_poses[i,:],right_poses[i,:]]
        # state = get_state(kinect[i,:])
        #traj.append([state,label])

    return traj


if __name__ == '__main__':
    #CSV Model for all teleop trials
    records = load_records('t')

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

    #get_trajectory(3,records)

    trajectories = []
    for i in range(first,last):
        traj = get_trajectory(i,records)
        trajectories.append(traj)


    #TRAJECTORIES: A LIST OF Rollouts with each rollout [[state,label],...,[state,label]]
    data = inputdata.IMData(trajectories) 
    net = Net(Options)
    net.optimize(iterations,data, batch_size=10)
