import cv2
from alan.synthetic.synthetic_util import get_pixel_bounds
import numpy as np
import cv
import IPython
from alan.core.points import Point
from scipy import ndimage

"""
Parameters:
    list with format [[matrix, [x, y, theta]]]
    step = degrees per rotational shift
    max number of images to generate for each matrix in the list
        total generated = list length * maxImgs
Returns:
    list with same format including original and expanded data
"""
def get_rotations_list(data_list, step = 20, max_imgs = 10):
    results = np.array([])
    for data in data_list:
        results = np.append(results, get_rotations_single(data, degree_step, max_imgs))
    return results

"""
Parameters:
    data with format [matrix, [x, y, theta]]
    step = degrees per rotational shift
    max number of images to generate
Returns:
    list with format [[matrix, label]
        Includes original and expanded data
"""
def get_rotations_single(data, step = 20):
    img = data[0]
    label = data[1]
    rows, cols = img.shape[0], img.shape[1]

    bounds = get_pixel_bounds(img)
    center = (bounds[1] + bounds[0])/2

    results = []

    for degree_shift in range(0, 360, step):
        #see for reference: http://docs.opencv.org/trunk/da/d6e/tutorial_py_geometric_transformations.html
        M = cv2.getRotationMatrix2D((center.x, center.y), degree_shift, 1)

        new_img = cv2.warpAffine(img, M, (cols, rows), flags= cv2.INTER_NEAREST)
        #new_img = cv.GetQuadrangleSubPix(img,M,(cols, rows))
        # cv2.imshow('debug',new_img)
        # cv2.waitKey(30)
        # print "ROTATION LABEL ",np.array([label[2] - degree_shift])

        #transform the label
        new_xy = np.matmul(M, np.array([label[0], label[1], 1]))
        new_label = np.append(new_xy, np.array([label[2] - degree_shift]))
        results.append([new_img, new_label])


    return results


"""
Parameters:
    data
        imgs: a list of all labels from transform image, each image [path,rollout,index,img])
        idx: the current index of the images
    max number of images to generate
Returns:
    list with format [[matrix1, label1], ...] including original and expanded data
        expanded data has rotated image, updated label
"""
def rotate_images(imgs,idx,bounds,deltas_i,cp,max_imgs = 20):
    #read first channel of image
    deltas = []
    rotated_imgs = []
    b_l = bounds[0]
    b_u = bounds[1]
    b_r = bounds[2]
    index = idx

    num_trans_imgs = len(imgs)

    for i in range(num_trans_imgs):
        label = np.zeros(3)
        label[0] = deltas_i[i][0]
        label[1] = deltas_i[i][1]
        label[2] = cp[2]

        path = imgs[i][0]
        rollout = imgs[i][1]
        img = imgs[i][3]

        rotated_images = get_rotations_single([img,label])

        rotated_images = rotated_images[0:max_imgs]

        for r_im in rotated_images:
            #read from shifts, which has format [img, [y, x]]
            img = r_im[0]
            label = r_im[1]

            if(label[0] >= b_l[0] and label[0] <= b_u[0] and label[1] >= b_l[1] and label[1] <= b_u[1]):
                if(label[2] >= b_r[0] and label[2] <= b_r[1]):
                    deltas.append(label)
                    rotated_imgs.append([path,rollout,index,img])
                    index += 1

    return deltas,index, rotated_imgs
