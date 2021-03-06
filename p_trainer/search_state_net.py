''''
    Used to train a nerual network that maps an image to robot pose (x,y,z)
    Supports the Option of Synthetically Growing the data for Rotation and Translation 
    This file supports the specifc task of searching over different filters to be trained on

    Author: Michael Laskey 


    Flags
    ----------
    --first (-f) : int
        The first roll out to be trained on (required)

    --last (-l) : int
        The last rollout to be trained on (reguired)

'''


import sys, os


import IPython
from tensor import inputdata
from alan.p_trainer.compile_sup import Compile_Sup #specific: imports compile_reg from sup
#from alan.rgbd.binaryThreshBox import transform_image
import numpy as np, argparse
from alan.synthetic.affine_synthetic import Affine_Synthetic


#######NETWORK FILES####################
#specific: imports options from specific options file
from alan.p_grasp.options import Grasp_Options as options 
#specific: fetches specific net file
from tensor.net_grasp import Net_Grasp as Net 


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
iterations = 3000

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

    #Try Different Filters 
    #Binaries Filter 
    CS.compile_reg(Options.binaries_dir)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)

    #Gray 
    CS.compile_reg(Options.gray_dir)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)

    #Color
    CS.compile_reg(Options.originals_dir)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)

    #Gray Mask
    CS.compile_reg(Options.gray_mask_dir)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)

    #Gray Mask Binned
    CS.compile_reg(Options.gray_mask_binned_dir)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)


    #Gray Mask Traced
    CS.compile_reg(Options.gray_mask_traced_dir)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)

    #RGB Mask 
    CS.compile_reg(Options.rgb_mask)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)

    #RGB Mask 
    CS.compile_reg(Options.rgb_mask)

    data = inputdata.IMData(Options.train_file, Options.test_file) 
    net = Net(Options)  
    net.optimize(iterations,data, batch_size=batch_size)



