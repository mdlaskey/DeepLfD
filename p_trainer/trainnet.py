''''
    Used to train a nerual network that maps an image to robot pose (x,y,z)
    Supports the Option of Synthetically Growing the data for Rotation and Translation 

    Author: Michael Laskey 


    Flags
    ----------
    --first (-f) : int
        The first roll out to be trained on (required)

    --last (-l) : int
        The last rollout to be trained on (reguired)

    --net_name (-n) : string
        The name of the network if their exists multiple nets for the task (not required)

    --demonstrator (-d) : string 
        The name of the person who trained the network (not required)

'''


import sys, os

import IPython
from deep_lfd.tensor import inputdata
from compile_sup import Compile_Sup 
import numpy as np, argparse
from deep_lfd.synthetic.affine_synthetic import Affine_Synthetic


#######NETWORK FILES TO BE CHANGED#####################
#specific: imports options from specific options file
from deep_lfd.p_pi.p_grasp.options import Grasp_Options as options 

#specific: fetches specific net file
from deep_lfd.tensor.nets.net_grasp import Net_Grasp as Net 
########################################################

#########SYNTHETIC PARAMS##########

#Type of Translations

translation = False
rotation = False

#Max Number of Translations per Images
max_trans = 50

#Max Number of Rotations per Images 
max_rot = 20

########TRAINING PAPRAMETERS##########
batch_size = 150
iterations = 300000

########################################################


Options = options()


def copy_over(infile, outfile):
    ''''
        Appends one file into another

        Parameters
        ----------
        infile : file
            file path for input data

        outfile: file
            file path for output data

     '''

    lines = infile.readlines()
    for line in lines:
    	outfile.write(line)



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

    if(translation or rotation):
        aff_syn = Affine_Synthetic(Options,translation,rotation,max_trans,max_rot)
        aff_syn.generate_data(first,last)


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
    net = Net(Options)
    net.optimize(iterations,data, batch_size=batch_size)
