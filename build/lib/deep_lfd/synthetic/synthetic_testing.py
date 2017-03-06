import unittest
import sys
import numpy as np
import cv2

"""
Testing for the synthetic package
See for reference: https://docs.python.org/2/library/unittest.html
"""
class SyntheticTest(unittest.TestCase):
    def test_util(self):
        if which_tests[0] == 1:
            print("TESTING UTIL")

            folder = dir_main + "/src/alan/synthetic"
            sample_image = read_im(folder, "sample", "png")

            #convert to binary by taking red pixels
            sample_image = sample_image[:,:,2]

            #make sure binary image is correct
            write_im(sample_image, folder, "sample_bin", "png")

            bounds = get_pixel_bounds(sample_image)
            print("First vertex is " + str(bounds[0].vector))
            print("Second vertex is " + str(bounds[1].vector))

            correct_bounds = [Point(np.array([53, 41]), "pixel_2D"), Point(np.array([122, 94]), "pixel_2D")]
            for i in range(2):
                err = np.linalg.norm((correct_bounds[i] - bounds[i]).vector)
                print("Error " + str(i) + " is " + str(err))
                self.assertTrue(err < 5)

    def test_rot(self):
        if which_tests[1] == 1:
            print("TESTING ROTATION")

            folder = dir_main + "/src/alan/synthetic"
            sample_image = readIm(folder, "sample", "png")

            #convert to binary by taking red pixels
            sample_image = sample_image[:,:,2]

            #artifical label at approximate center of object - only theta changes
            old_label = [84, 70, 0]
            rotated_imgs = get_rotations_single([sample_image, old_label], step = 40)

            s = 0
            for r in rotated_imgs:
                #make sure rotated image is correct
                writeIm(r[0], folder, "sample_rot_" + str(s), "png")

                s += 90

                new_label = r[1]
                for i in range(3):
                    err = new_label[i] - old_label[i]
                    if i == 2:
                        err -= (90 * s)
                    print("Error " + str(i) + " is " + str(err))
                    #self.assertTrue(err < 5)

    def test_rope(self):
        if which_tests[2] == 1:
            print("TESTING CAR ROPE")
            for i in range(0, 100):
                m, labels, res = get_rope_car()
                #draw left label in white, right label in gray for testing
                # c = 256
                # for l in labels:
                #     x, y, theta, d = l[0], l[1], l[2], 5
                #     new_x, new_y = x + d * cos(theta), y + d * sin(theta)
                #     cv2.line(m, (int(x), int(y)), (int(new_x), int(new_y)), c, 4)
                #     c -= 128
                if res == 1:
                    writeIm(m, save_dir, "good_rope_car_test_" + str(i), "png")
                if res == -1:
                    writeIm(m, save_dir, "bad_rope_car_test_" + str(i), "png")

    def test_reflection(self):
        if which_tests[3] == 1:
            print("TESTING REFLECTION")
            folder = dir_main + "/src/alan/synthetic"
            sample_image = readIm(folder, "sample", "png")

            #convert to binary by taking red pixels
            sample_image = sample_image[:,:,2]

            old_label = [84, 70, 0]
            reflected_img, new_label = get_reflection([sample_image, old_label])

            writeIm(reflected_img, folder, "sample_reflect", "png")

    def test_translation(self):
        if which_tests[4] == 1:
            print("TESTING TRANSLATION")
            folder = dir_main + "/src/alan/synthetic"
            sample_image = readIm(folder, "sample", "png")

            #convert to binary by taking red pixels
            sample_image = sample_image[:,:,2]

            step = 100
            num_shifts = get_shifts(sample_image, step)
            shifts = [[sample_image, [0, 0]]]
            shifts += get_translations_1D(shifts[0], [num_shifts[i][1] for i in range(2)], step, 1)
            xshifts = []
            for yshift in shifts:
                xshifts += get_translations_1D(yshift, [num_shifts[i][0] for i in range(2)], step, 0)
            shifts = shifts + xshifts
            for i in range(len(shifts)):
                writeIm(shifts[i][0], folder, "translate" + str(i), "png")


if __name__ == '__main__':
    #dir_main will change by machine
    dir_main = "/Users/chrispowers/Desktop/research/alan"
    save_dir = dir_main + "/src/alan/synthetic/images"
    sys.path.append(dir_main + "/src")

    from alan.synthetic.synthetic_util import get_pixel_bounds
    from alan.synthetic.synthetic_rotation import get_rotations_single
    from alan.synthetic.synthetic_reflection import get_reflection
    from alan.synthetic.synthetic_translation import get_translations_1D, get_shifts
    from alan.rgbd.basic_imaging import sin, cos, readIm, writeIm
    from alan.synthetic.synthetic_rope import get_rope_car
    from alan.core.points import Point

    which_tests = [0, 0, 0, 0, 1]

    unittest.main()
