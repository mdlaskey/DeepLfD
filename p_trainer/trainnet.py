import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
from tensor import inputdata
from alan.p_trainer.compile_sup import Compile_Sup #specific: imports compile_reg from sup
#from alan.rgbd.binaryThreshBox import transform_image
import numpy as np, argparse

from alan.p_rope_grab_R.options import Rope_GrabROptions as options #specific: imports options from specific options file
from tensor import net_rope_grab #specific: fetches specific net file

Options = options()

def copy_over(infile, outfile):
    lines = infile.readlines()
    for line in lines:
    	outfile.write(line)

def conv_deltas_to_str(deltas,cur_pose):
    label = " "
    for i in range(2):
        deltas[i] = deltas[i] #specific: deltas from specific options
    #deltas = bound_pose(cur_pose,deltas)
    for i in range(len(deltas)):
        label = label+str(deltas[i])+" "

    label = label+"\n"
    return label

def bound_pose(pose,delta_state):
    pose[0] += delta_state[0]
    pose[1] += delta_state[1]

    if(pose[0] < Options.X_LOWER_BOUND): #specific: x y information from specific options
        pose[0] = Options.X_LOWER_BOUND
    elif(pose[0] > Options.X_UPPER_BOUND):
        pose[0] = Options.X_UPPER_BOUND

    if(pose[1] < Options.Y_LOWER_BOUND):
        pose[1] = Options.Y_LOWER_BOUND
    elif(pose[1] > Options.Y_UPPER_BOUND):
        pose[1] = Options.Y_UPPER_BOUND


    # print pose
    return pose

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



    outfile = open(Options.deltas_file, 'w+') #specific: fetches specific directory. CHANGE
    f = []
    for (dirpath, dirnames, filenames) in os.walk(Options.sup_dir): #specific: sup_dir from specific options
        print dirpath
        print filenames
        f.extend(dirnames)
    for filename in f:
        read_path = Options.sup_dir+filename+'/net_deltas.txt' #specific: sup_dir from specific options
        if read_path.find("net_deltas") != -1 and read_path.find("~") == -1:
            index = int(filename[7:])
            if index < last and first <= index:

                infile = open(read_path, 'r')

                copy_over(infile, outfile)
                infile.close()


    CS = Compile_Sup(Options)

    outfile.close()
    CS.compile_reg()

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = net_rope_grab.Net_Rope_Grab(Options) 
    #path = Options.policies_dir+'grasp_net_10-23-2016_21h26m19s.ckpt' 
    net.optimize(3000,data, batch_size=150)
