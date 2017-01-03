import sys, os
sys.path.append('/home/autolab/Workspace/michael_working/Tensor_Net')

import IPython
import cv2


from alan.synthetic.synthetic_translation import transform_image
from alan.synthetic.synthetic_rotation import rotate_images
from alan.rgbd.registration_wc import RegWC
import numpy as np, argparse
#Things to change

from alan.p_rope_grab_R.options import Rope_GrabROptions as options

Options = options()



#Read Image That has been rotated 

img_path = Options.binaries_dir+'rollout0_frame_34.png'
print img_path
img = cv2.imread(img_path)

# img_b = np.zeros([img.shape[0],img.shape[1],3])

# for i in range(3):
# 	img_b[:,: i] = img

label = np.array([187.739729023, 152.059301642, 0])


img[int(label[1])-5:int(label[1])+5,int(label[0])-5:int(label[0])+5,2] = 255
img[int(label[1])-5:int(label[1])+5,int(label[0])-5:int(label[0])+5,1] = 0
img[int(label[1])-5:int(label[1])+5,int(label[0])-5:int(label[0])+5,0] = 0
while True:
	cv2.imshow('debug',img)
	cv2.waitKey(30)
