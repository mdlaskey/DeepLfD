import unittest
import sys
import numpy as np
import cv2
from scipy import spatial

"""
Testing for the synthetic package
See for reference: https://docs.python.org/2/library/unittest.html
"""
class RGBDTest(unittest.TestCase):
    def test_rot(self):
        if which_tests[0] == 1:
            print("TESTING ENDPOINTS")
            num_tests = 10
            for test in range(num_tests):
                #generate a rope image
                rope_image, labels, res = get_rope_car()

                #good image
                if res == 1:
                    writeIm(rope_image, save_dir, str(test) + "_rope", "png")

                    #(420, 420, 3) -> (420, 420)
                    #rope_image = rope_image[:,:,0]

                    rope_conv, endpoints = find_endpoints(rope_image)

                    #ignore rotation
                    labels = [l[0:2] for l in labels]

                    #check both and take min (might not be in same order)
                    err = [0, 0]
                    for end_num in range(2):
                        err[end_num] = spatial.distance.euclidean(endpoints[end_num], labels[end_num])
                    avg_err = sum(err)/len(err)

                    for end_num in range(2):
                        err[end_num] = spatial.distance.euclidean(endpoints[1 - end_num], labels[end_num])
                    avg_err_2 = sum(err)/len(err)

                    avg_err = min(avg_err, avg_err_2)

                    print("For test " + str(test) + ", endpoints are off by avg. distance " + str(avg_err))

                    writeIm(rope_conv, save_dir, str(test) + "_conv", "png")
                elif res == -1:
                    #resample
                    pass

    def test_new_binarize(self):
        if which_tests[1] == 1:
            name = "s"
            print("TESTING NEW BINARIZATION")
            folder = save_dir
            sample_image = readIm(folder, name, "jpg")

            out_imgs = apply_all(sample_image)

            labels = ["gray", "gray_mask", "gray_mask_binned", "trace", "blur", "rgb", "rgb_mask", "rgb_binned", "rgb_gray"]
            combined = zip(out_imgs, labels)

            for img, label in combined:
                writeIm(img, save_dir, name + "_out_" + label, "jpg")


if __name__ == '__main__':
    #dir_main will change by machine
    dir_main = "/Users/chrispowers/Desktop/research/alan"
    save_dir = dir_main + "/src/alan/rgbd/images"
    sys.path.append(dir_main + "/src")

    from alan.rgbd.basic_imaging import readIm, writeIm
    from alan.synthetic.filters import apply_all
    #from alan.rgbd.rope_endpoints import find_endpoints
    from alan.synthetic.synthetic_rope import get_rope_car
    from alan.core.points import Point

    which_tests = [0, 1]

    unittest.main()
