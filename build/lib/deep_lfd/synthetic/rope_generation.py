import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
import cv2


from alan.synthetic.synthetic_translation import transform_image
from alan.synthetic.synthetic_rope import get_rope_car
from alan.rgbd.registration_wc import RegWC
from alan.synthetic.synthetic_util import re_binarize
import numpy as np, argparse
#Things to change

from alan.p_rope_grab_R.options import Rope_GrabROptions as options_R
from alan.p_rope_grab_L.options import Rope_GrabLOptions as options_L


def conv_deltas_to_str(deltas):
    label = " "

    for i in range(len(deltas)):
        label = label+str(deltas[i])+" "

    label = label+"\n"
    return label

def get_rope_params(reg):
	#Measurments in meters
	Length = 1.07
	Width = 0.007

	l_p = reg.robot_to_pixel_scale(Length)
	w_p = reg.robot_to_pixel_scale(Width)

	print "LENGTH ", l_p
	print "WIDTH ", w_p
	return int(l_p),int(w_p)

def get_bounds(Options,reg):
    low_bound = np.array([Options.X_LOWER_BOUND,Options.Y_LOWER_BOUND])
    up_bound = np.array([Options.X_UPPER_BOUND,Options.Y_UPPER_BOUND])
    rot_bounds = np.array([Options.ROT_MIN,Options.ROT_MAX])
    p_l_b = reg.robot_to_pixel(low_bound)
    p_u_b = reg.robot_to_pixel(up_bound)

    return p_l_b,p_u_b,rot_bounds


def write_labels(opt,labels,idx,first):

	write_path = opt.sup_dir+'rollout0/' 
	if(not os.path.isdir(write_path)):
		os.makedirs(write_path)
	

	if(first):
		f = open(write_path+'net_deltas.txt', 'w')
	else: 
		f = open(write_path+'net_deltas.txt', 'a+')

	for i in range(len(labels)):
		label = labels[i]
		f_name = "rollout0_frame_"+str(idx)+".png"
		f.write(f_name+conv_deltas_to_str(label))
		idx += 1

	return idx


def save_images(opt,images,idx):

	for img in images:
		#IPython.embed()
		cv2.imwrite(opt.binaries_dir+"rollout0_frame_"+str(idx)+".png", img)
		idx += 1

	return


def generate_rope_images(optR,optL,length,width,b_r,b_lf,num_imgs=40000):

	labels_r = []
	img_r = []

	labels_l = []
	img_l = []

	idx_r = 0
	idx_l = 0
	iters = 0
	first = True

	#IPython.embed()

	for i in range(num_imgs):
		[img, labels,success] = get_rope_car(h = optR.HEIGHT, w = optL.WIDTH, rope_l_pixels = length , rope_w_pixels = width)

		if success == 1:

			#Check Right Arm
			b_l = b_r[0]
			b_u = b_r[1]
			rot = b_r[2]

			l_r = labels[0]
			
			if(l_r[0] >= b_l[0] and l_r[0] <= b_u[0] and l_r[1] >= b_l[1] and l_r[1] <= b_u[1]):
				#if(l_r[2] >= rot[0] and l_r[2] <= rot[1]):
				labels_r.append(l_r)
				img_r.append(img)

	       	#Check Left Arm
			b_l = b_lf[0]
			b_u = b_lf[1]
			rot = b_lf[2]

			l_l = labels[1]

			print l_l
			
			if(l_l[0] >= b_l[0] and l_l[0] <= b_u[0] and l_l[1] >= b_l[1] and l_l[1] <= b_u[1]):
				#if(l_l[2] >= rot[0] and l_l[2] <= rot[1]):
				print "GOT HERE"
				labels_l.append(l_l)
				img_l.append(img)

			if(iters > 200):
				save_images(opt_r,img_r,idx_r)
				save_images(opt_l,img_l,idx_l)

				idx_r = write_labels(opt_r,labels_r,idx_r,first)
				idx_l = write_labels(opt_l,labels_l,idx_l,first)

				first = False

				labels_r = []
				img_r = []

				labels_l = []
				img_l = []

				iters = 0
			else: 
				iters +=1






if __name__ == '__main__':

	opt_r = options_R()
	opt_l = options_L()

	reg = RegWC(opt_r)


	length,width = get_rope_params(reg)

	b_r = get_bounds(opt_r,reg)
	b_l = get_bounds(opt_l,reg)

	generate_rope_images(opt_r,opt_l,length,width,b_r,b_l,num_imgs = 500000)













