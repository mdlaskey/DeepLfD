# PROJECT Deep Learning From Demonstrations
# AutoLab, UC Berkeley
Policies folder for each trained manipulation primitive. A manipulation primitive is defined as a neural network that takes in an image and then decides where to execture a motion (such as grasping, pushing, ) 

## Usage

Step 0: See p_grasp_align for an example of a motion primitive. 

Step 1: For every new primitve a folder should be created 

'''mkdir policies/p_primitive_name

Step 2: Overwrite the parameters in the options class (i.e. where the crop image is located and the bounding box around the robot)

'''mkdir policies/p_primitive_name

Step 3: Overwrite execute motion in the com class, the default is current to go downwards and close gripper. 

