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
from deep_lfd.tensor import inputdata
from compile_sup import Compile_Sup #specific: imports compile_reg from sup
#from alan.rgbd.binaryThreshBox import transform_image
import numpy as np, argparse
# from alan.synthetic.affine_synthetic import Affine_Synthetic
from plotter import plot_net


#######NETWORK FILES####################
#specific: imports options from specific options file
from deep_lfd.p_pi.p_grasp.options import Grasp_Options as options 
#specific: fetches specific net file
from deep_lfd.tensor.net_grasp_v2 import Net_Grasp as Net 


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
iterations = 600
plot_dir = "plots_v2"

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

    if translation or rotation:
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

    Options.set_filter_paths()


    all_tests = []
    # all_tests.append([Options.binary_dir, "Binary"])
    all_tests.append([Options.originals_dir, "Color"])
    # all_tests.append([Options.gray_dir, "Gray"])
    # all_tests.append([Options.gray_mask_dir, "Gray Mask"])
    # all_tests.append([Options.gray_mask_binned_dir, "Gray Mask Binned"])
    # all_tests.append([Options.rgb_gray_dir, "RGB Gray"])
    # all_tests.append([Options.rgb_mask_dir, "RGB Mask"])
    # all_tests.append([Options.rgb_mask_binned_dir, "RGB Mask Binned"])

    nodes = 500
    windows = 5


    plot_num = 0
    for test in all_tests:
        curr_options = test[0]
        curr_save = test[1]

        CS.compile_reg(curr_options)
       
        data = inputdata.IMData(Options.train_file, Options.test_file) 
        net = Net(Options, nodes, windows)  
        net.optimize(iterations,data, batch_size=batch_size)

        train_log, test_log = net.get_logs()
        curr_name = curr_save + "_" + str(nodes) + "_" + str(windows)

        plot_net(train_log, test_log, curr_name, Options.setup_dir + plot_dir, plot_num)
        plot_num += 1


    # Try Different Filters 
    # Binaries Filter 
    # CS.compile_reg(Options.binary_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "Binary", Options.setup_dir + plot_dir, 0)

    # #Gray 
    # CS.compile_reg(Options.gray_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "Gray", Options.setup_dir + plot_dir, 1)

    #Color
    # CS.compile_reg(Options.originals_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "Color", Options.setup_dir + plot_dir, 2)

    # #Gray Mask
    # CS.compile_reg(Options.gray_mask_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "Gray Mask", Options.setup_dir + plot_dir, 3)

    # #Gray Mask Binned
    # CS.compile_reg(Options.gray_mask_binned_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "Gray Mask Binned", Options.setup_dir + plot_dir, 4)

    # #RGB gray
    # CS.compile_reg(Options.rgb_gray_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "RGB Gray", Options.setup_dir + plot_dir, 5)

    # #RGB Mask 
    # CS.compile_reg(Options.rgb_mask_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "RGB Mask", Options.setup_dir + plot_dir, 6)

    # #RGB Mask binned
    # CS.compile_reg(Options.rgb_mask_binned_dir)

    # data = inputdata.IMData(Options.train_file, Options.test_file) 
    # net = Net(Options)  
    # net.optimize(iterations,data, batch_size=batch_size)
    # train_log, test_log = net.get_logs()
    # plot_net(train_log, test_log, "RGB Mask Binned", Options.setup_dir + plot_dir, 7)

