import cv2
import IPython
import numpy as np
from scipy import ndimage
import perception.image

class Synthetic:

    def __init__(self, Options, num_samples):
        """
        Parameters
        ----------
        Options : options file containing workspace pixel bounds
        num : number of transformations to apply to each image in data

        """

        self.bounds = Options.bounds
        self.num = num_samples

    def get_dist_from_bounds(image):
        """
        Parameters
        ----------
        image : binary image

        Returns
        -------
        distance from object bounding box to image bounds in order of low_x, high_x, low_y, high_y
        """
        pixel_points = image.nonzero_pixels()
        lx = min(pixel_points, key = lambda x: x[0])
        hx = len(image.T) - max(pixel_points, key = lambda x: x[0])
        ly = min(pixel_points, key = lambda x: x[1])
        hy = len(image.T) - max(pixel_points, key = lambda x: x[1])

        return lx, hx, ly, hy

    def apply_rotations(data):
        """
        Parameters
        ----------
        data : list of format (image, label)
        num : number of transformations to apply to each image in data

        Returns
        -------
        input data rotated by randomly selected amounts
        """

        results = np.array([])

        for img, label in data:

            curr = np.array([(img, label)])

            sample_num = 0
            while sample_num < self.num:
                degree_shift = np.random.uniform(-90, 90)

                new_img = img.transform(np.array([0,0]),np.deg2rad(degree_shift))

                c = img.center 
                M = cv2.getRotationMatrix2D((c[0], c[1]), degree_shift, 1)
                new_xy = np.matmul(M, np.array([label[0], label[1], 1]))
                new_theta = np.array([label[2] - degree_shift])
                new_label = np.append(new_xy, new_theta, np.array([label[3]]))

                if check_bounds(new_label):
                    curr = np.append(curr, (new_img, new_label)))
                    sample_num += 1

            results = np.append(results, curr)

        return results

    def apply_translations(data):
        """
        Parameters
        ----------
        data : list of format (image, label)

        Returns
        -------
        input data translated by randomly selected amounts in x and y
        """

        results = np.array([])

        for img, label in data:

            curr = np.array([img, label])

            sample_num = 0
            while sample_num < self.num:
                lx, hx, ly, hy = get_dist_from_bounds(matrix)

                x_shift = np.random.uniform(-lx, hx)
                y_shift = np.random.uniform(-ly, hy)
                new_img = img.transform(np.array([x_shift,y_shift]), 0)

                M = cv2.getRotationMatrix2D((img.center[0], img.center[1]), 0, 1)
                new_xy = np.array([label[0] + x_shift, label[1] + y_shift])
                new_label = np.append(new_xy, np.array([label[2], label[3]]))

                if check_bounds(new_label):
                    curr = np.append(curr, (new_img, new_label)))
                    sample_num += 1

            results = np.append(results, curr)

        return results

    def apply_reflection(data):
        """
        Parameters
        ----------
        data : list of format (image, label)

        Returns
        -------
        input data reflected across y-axis
        """

        results = np.array([])

        for img, label in data:

            new_img = cv2.flip(img, 1)
            new_x = np.array([len(img.T) - label[0]])
            new_theta = np.array([180 - label[2]])
            new_label = np.append(new_x, np.array([label[1]) new_theta, np.array(label[3]]))

            if check_bounds(new_label):
                results = np.append(results, (new_img, new_label))

        return results

    def apply_filters(data, rotate = False, translate = False, reflect = False):
        """
        Parameters
        ----------
        data : list of format (image, label)
        rotate, translate, reflect : bools specifying types of transformation to aply

        Returns
        -------
        input data transformed (does not compose transformations)
        """

        output_data = np.copy(data)

        if rotate:
            output_data = np.append(output_data, apply_rotations(data, 20))
        if translate:
            output_data = np.append(output_data, apply_translations(data, 20))
        if reflect:
            output_data = np.append(output_data, apply_reflection(data))

        return output_data


    def check_bounds(label):
        """
        Parameters
        ----------
        label : (x, y, theta, depth)

        Returns
        -------
        True if label falls within workspace bounds
        """

        b_l = self.bounds[0]
        b_u = self.bounds[1]
        b_r = self.bounds[2]
        c_bounds = np.array([[b_l[0], b_u[0]], [b_l[1], b_u[1]], b_r)

        for coord in range(3):
            if not (c_bounds[i][0] <= label[i] and c_bounds[i][1] >= label[i]):
                return False

        return True
