import cv2
import IPython

"""
Parameters:
    data- has format [matrix, label]
    label has format [x, y, theta]
Returns:
    [reflected_matrix, reflected_label]
"""
def get_reflection(data):
    new_img = cv2.flip(data[0], 1)
    old_label = data[1]
    new_label = [len(new_img[0]) - old_label[0], old_label[1], 0]#180 - old_label[2]]

    return [new_img, new_label]


def reflect_images(img_data,idx,bounds,label):
    #read first channel of image
    deltas = []
    r_imgs = []
    b_l = bounds[0]
    b_u = bounds[1]
    b_r = bounds[2]
    index = idx


    path = img_data[0]
    rollout = img_data[1]
    img = img_data[2]

    r_im = get_reflection([img,label])

    img = r_im[0]
    label = r_im[1]

    if(label[0] >= b_l[0] and label[0] <= b_u[0] and label[1] >= b_l[1] and label[1] <= b_u[1]):
        if(label[2] >= b_r[0] and label[2] <= b_r[1]):
            deltas.append(label)
            r_imgs = [path,rollout,index,img]
            index += 1

    return deltas,index,r_imgs
