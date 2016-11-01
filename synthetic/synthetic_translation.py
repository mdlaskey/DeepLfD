import numpy as np
import cv2
import math
import IPython
from alan.rgbd.basic_imaging import add_dim
from alan.synthetic.synthetic_util import get_pixel_bounds
from alan.core.points import Point

"""
Parameters:
    2D binary matrix
    step size in pixels for each shift
Returns:
    array of two Points that correspond to number of shifts available in low and high directions
"""
def get_shifts(matrix, step):
    bounds = get_pixel_bounds(matrix)

    #convert upper vertex to distance from end
    bounds[1] = Point(np.array([len(matrix.T), len(matrix)]), "pixel_2D") - bounds[1]

    #convert from pixels to steps
    bounds = [[int(math.floor(v.vector[i]/step)) for i in range(2)] for v in bounds]

    return bounds
"""
Parameters:
    data = [2D binary matrix, [x, y]]
    curr_pix_shift = amount to shift image by
    dim: 0 == x, 1 == y
Returns:
    [shifted matrix, [new x shift, new y shift]]
"""
def get_translation(data, curr_pix_shift, dim):
    matrix = data[0]
    prev_shift = data[1]
    rows, cols = matrix.shape

    M = np.array([[1.0, 0, 0], [0, 1.0, 0]])
    M[dim,2] = float(curr_pix_shift)
   
    shifted_matrix = cv2.warpAffine(matrix, M, (rows, cols))

    curr_shift = [prev_shift[0], prev_shift[1]]
    curr_shift[dim] += curr_pix_shift
    return [shifted_matrix, curr_shift]

"""
Parameters:
    data = [2D binary matrix, [x, y]]
    bounds = [low, high]- # of shifts in each direction
    step = pixels per shift
    dim: 0 == x, 1 == y
Returns:
    list with format [shifted matrix, [new x shift, new y shift]]
        does not include input data
"""
def get_translations_1D(data, bounds, step, dim):
    new_data = []

    #shifts start at 1 since 0 is no shift

    #down/left
    for curr_num_shifts in range(1, bounds[0] + 1):
        curr_pix_shift = -1 * step * curr_num_shifts
        new_data.append(get_translation(data, curr_pix_shift, dim))

    #up/right
    for curr_num_shifts in range(1, bounds[1] + 1):
        curr_pix_shift = step * curr_num_shifts
        new_data.append(get_translation(data, curr_pix_shift, dim))

    return new_data

"""
Parameters:
    path, f_name - used to read/write matrix- must be binary
    rollout, index- used to write matrix
    bounds- upper/lower x/y bounds
    max_imgs- limit number of translations
    shift_step- size of each translation in pixels
-- also saves images
Returns:
    --
"""
def transform_image(path, rollout, f_name, index, bounds, cp, options=None, max_imgs = 20, step = 10):
    #read first channel of image
    imgName =  path+f_name

    matrix = cv2.imread(imgName,1)
    matrix = matrix[:,:,0]

    b_l = bounds[0]
    b_u = bounds[1]

    #gets number of possible translations for each edge
    num_shifts = get_shifts(matrix, step)

    #initialize with the unshifted matrix
    shifts = [[matrix, [0, 0]]]

    #add all shifts with just y translation
  
    shifts += get_translations_1D(shifts[0], [num_shifts[i][1] for i in range(2)], step, 1)

    xshifts = []
    for yshift in shifts:
        #combine each y translation (and the unshifted matrix) with every possible x translation
        xshifts += get_translations_1D(yshift, [num_shifts[i][0] for i in range(2)], step, 0)


    #grab correct shifts and prepare for neural net
    shifts = shifts + xshifts

    shifts = shifts[1:max_imgs]
    #IPython.embed()
    #shifts = [[add_dim(s[0]), s[1]] for s in shifts]


    deltas = []
    imgs = []
    for i in range(len(shifts)):
        #read from shifts, which has format [img, [y, x]]
        img = shifts[i][0]
        cords = shifts[i][1]

        #Check if outside robot position
        cp_d = np.copy(cp)
        cp_d[0:2]= cp_d[0:2]+cords



        if(cp_d[0] >= b_l[0] and cp_d[0] <= b_u[0] and cp_d[1] >= b_l[1] and cp_d[1] <= b_u[1]):
            deltas.append(cp_d)
            imgs.append([path,rollout,index,img])
            index += 1

    return deltas,index,imgs

if __name__ == '__main__':

    transform_image("",'0','get_jp.jpg',0)